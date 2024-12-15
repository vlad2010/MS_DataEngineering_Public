#!/usr/bin/env python3

import json
import sys
import time
from dataclasses import dataclass

from datetime import datetime
from openai import OpenAI
import argparse
import os
import re

# in seconds
TOKEN_LIMIT_DELAY = 0

@dataclass
class TokensStat:
    prompt_tokens:int = 0
    answer_tokens:int = 0

g_token_stat = TokensStat()

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# OpenAI API help
# https://platform.openai.com/docs/api-reference/introduction

g_scanner_reports = {"cppcheck":"d:\GitHub\MS_DataEngineering\Dissertation\Sarif_To_MyErrorFormat\FinalReports\cppcheck_report_cpp_csharp_15_10_2024.json",
                     "semgrep":"d:\GitHub\MS_DataEngineering\Dissertation\Sarif_To_MyErrorFormat\FinalReports\semgrep_simple_ext_28_09_2024.json",
                     "flawfinder":"d:\GitHub\MS_DataEngineering\Dissertation\Sarif_To_MyErrorFormat\FinalReports\\flawfinder_simple_report_ext_28_09_2024_fixed.json",
                     "snyk":"d:\GitHub\MS_DataEngineering\Dissertation\Sarif_To_MyErrorFormat\FinalReports\snyk_simple_report_ext_29_09_2024.json" }

api_key = read_file_content("..\\api-key.txt")
client = OpenAI(api_key=api_key)

def get_value_with_check(data, property_name, default_value):
    value = default_value
    if property_name in data:
        value = data[property_name]
    return value

def load_json(file_path):
    """
    Loads a JSON file and returns its content.

    :param file_path: The path to the JSON file.
    :return: The content of the JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
    return None

def load_reports():

    reports = {}
    for scanner_name, report_path in g_scanner_reports.items():

        report = load_json(report_path)
        reports[scanner_name] = report

    return reports

# path normalisation
def fix_path(file_name, path_to_source_folder):
    match = re.match(r"^/mnt/([a-zA-Z])/", file_name)
    if match:
        full_file_path = fix_unix_full_path(file_name, match)
    else:
        # Combine pathToSourceFolder and the file field using Windows-style delimiters
        full_file_path = os.path.join(path_to_source_folder, file_name).replace('/', '\\')

    return full_file_path

def fix_unix_full_path(path, match):
    # drive_letter = match.group(1).lower() + ":\\"
    drive_letter = match.group(1).lower() + ":\\\\"
    new_path = re.sub(r"^/mnt/[a-zA-Z]/", drive_letter, path)
    # Replace all remaining forward slashes with backslashes
    new_path = new_path.replace("/", "\\")
    return new_path

# compare two file paths
def compare_paths(issue_path, reports_path, reports_base_path):
    fixed_report_path = fix_path(reports_path, reports_base_path)

    p1 = os.path.realpath(fixed_report_path)
    p2 = os.path.realpath(issue_path)
    res = os.path.samefile(p1, p2)
    return res

# load static reports data
g_reports_data = load_reports()
# we also can create list with block of issues automatically, we need to inject array of scanners into each issue

def check_path_in_reports(file_path):
    # list of scanner reports where this file was detected
    scanners = []
    report_entries = []

    for scanner_name, report_data in g_reports_data.items():
        issues = get_value_with_check(report_data, "issues", None)

        if issues is None:
            continue

        base_path = get_value_with_check(report_data, "pathToSourceFolder", "")

        for issue in issues:
            file_path_report = get_value_with_check(issue, "file", "")

            res = compare_paths(file_path, file_path_report, base_path)

            if res:
                new_issue = issue
                new_issue["scanner"] = scanner_name
                scanners.append(scanner_name)
                report_entries.append(new_issue)
                break

    return scanners, report_entries

def print_status(scanners):
    print(f"Scanners detected: {scanners}")
    print(f"Total tokens: prompt:{g_token_stat.prompt_tokens}  answers:{g_token_stat.answer_tokens}   total:{g_token_stat.answer_tokens + g_token_stat.prompt_tokens}")

def keep_unique_strings(input_list):
    # Use a set to track seen strings
    seen = set()
    unique_list = []

    for string in input_list:
        # If the string hasn't been seen yet, add it to both the set and the unique list
        if string not in seen:
            unique_list.append(string)
            seen.add(string)

    return unique_list

def read_issues(file_path):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if line and not line.startswith('#'):
                lines.append(line)

    unique_lines = keep_unique_strings(lines)

    print(f"Issues loaded from file: {len(lines)}")
    return unique_lines

# check that all folders are available in the path
def ensure_directories(file_path):

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        # print(f"Directories created for the path: {directory}")


def save_to_file(filename, text):
    # check all folders present
    ensure_directories(filename)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
    return f"Text saved to {filename}"


def init_openai(model_name):
    print(f"OpenAI init model name: {model_name}")

def send_message_to_gpt(prompt, model_name):
    global g_token_stat
    try:
        # initial chat content, always new chat
        chat = [{"role": "system", "content": "You are a helpful assistant."}]
        chat.append({"role": "user", "content": prompt})

        # Send a request to the OpenAI API
        response = client.chat.completions.create(
            model=model_name,
            messages = chat
            # seed = 1000
        )

        # Extract the response text
        message = response.choices[0].message.content
        # print(f"Answer: {message}")

        print(f"Tokens: Prompt: {response.usage.prompt_tokens} Answer: {response.usage.completion_tokens} Total: {response.usage.total_tokens}")
        g_token_stat.answer_tokens += response.usage.completion_tokens
        g_token_stat.prompt_tokens += response.usage.prompt_tokens

        return message

    except Exception as e:
        print (f"An OpenAI API error occurred: {e}")
        sys.exit(1)

def create_prompt(prompt, source_code, language):
    final_prompt = prompt + f"\n(```{language}\n" + source_code + "\n```)"
    return final_prompt

def extract_code(input_string):
    # Regular expression to extract multiple tag and source code fragments
    pattern = r"```(\w+)\n(.*?)```"

    # Find all matches in the input string
    matches = re.findall(pattern, input_string, re.DOTALL)

    # Return a list of tuples (tag, source_code)
    result = [(tag, code.strip()) for tag, code in matches]
    return result

def process(issues_file, prompt_file, output_base_folder, model, iterations = 1, scs_base_folder = ""):

    issues = read_issues(issues_file)
    new_reports = []

    # read prompt
    prompt = read_file_content(prompt_file);

    print(f"Number of unique issues: {len(issues)}")
    print(f"Prompt: {prompt}")

    # init OpenAI
    init_openai(model)

    issue_index = 0
    for issue_file in issues:

        # print(f"Issue file from list: {issue_file}")

        if scs_base_folder:
            full_issue_file = os.path.join(scs_base_folder, issue_file)
        else:
            full_issue_file = issue_file

        print(f"\n---\nIssue : {issue_index+1}")
        print(f"Issue file: {full_issue_file}")
        source_code = read_file_content(full_issue_file)
        source_file_name = os.path.basename(full_issue_file)

        ext = os.path.splitext(source_file_name)[1][1:]
        final_prompt = create_prompt(prompt, source_code, ext)

        scanners, report_entries = check_path_in_reports(full_issue_file)
        if len(report_entries) == 0:
            new_reports.append(full_issue_file)
        else:
            new_reports.append(report_entries)

        for i in range(iterations):
            output_folder = os.path.join(output_base_folder, f"Issue_{issue_index + 1:02d}")

            if iterations > 1:
                print(f"\tIteration : {i+1}")
                output_folder = os.path.join(output_folder, f"Iteration_{i+1:02d}")

            # single iteration conversation
            responce = send_message_to_gpt(final_prompt, model)

            code_fragments = extract_code(responce)

            generated_src_index = 1
            for tag, code in code_fragments:
                if tag == "csharp":
                    tag = "cs"
                generated_src_file_name = f"New_generated_code_{generated_src_index:02d}.{tag}"
                save_to_file(os.path.join(output_folder, generated_src_file_name), code)
                generated_src_index += 1

            save_to_file(os.path.join(output_folder, source_file_name), source_code)
            save_to_file(os.path.join(output_folder, "ChatGPT_Response.md"), responce)
            save_to_file(os.path.join(output_folder, "OurPrompt.txt"), final_prompt)

            info = f"Model name: {model}\nFile name: {full_issue_file}\nScanners: {scanners}"
            save_to_file(os.path.join(output_folder, "Info.txt"), info)

        issue_index += 1
        print_status(scanners)
        time.sleep(TOKEN_LIMIT_DELAY)

    # finalize

    output_data = {
        "pathToSourceFolder": "d:\GitHub\MS_DataEngineering\Dissertation\\Utils\cpp_csharp",
        "dateAndTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "issues": new_reports
    }

    output_report_file =  os.path.join(output_base_folder, f"Output_report.json")
    # Write the output JSON file
    with open(output_report_file, 'w', encoding='utf-8') as out_file:
        json.dump(output_data, out_file, indent=4)

    return issue_index


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process issues and asking extra questions.")

    # Required positional arguments
    parser.add_argument("--issues_file", required=True, type=str, help="Path to file with selected issues")
    parser.add_argument("--prompt_file", required=True, type=str, help="Path to file with prompt")
    parser.add_argument("--output_folder", required=True, type=str, help="Path to output folder")

    parser.add_argument("--src_base_folder", required=False, type=str, default="", help="Base path to source folder")

    parser.add_argument("--iterations",  required=False, type=int, default=1, help="Number of iterations for each issue")
    # Optional argument with a default value
    parser.add_argument("--model_name", required=False, type=str, default="gpt-4o", help="Model name (default: 'gpt-4o')")

    args = parser.parse_args()
    return args

def main():

    start_time = time.time()
    args = parse_arguments()

    print(f"JSON Path: {args.issues_file}")
    print(f"Prompt File: {args.prompt_file}")
    print(f"Model Name: {args.model_name}")
    print(f"Output folder: {args.output_folder}")
    print(f"Number of iterations: {args.iterations}")
    print(f"Source base folder: {args.src_base_folder}")

    issues_num = process(args.issues_file, args.prompt_file, args.output_folder, args.model_name, args.iterations, args.src_base_folder)
    end_time = time.time()

    print(f"\nIssues processed : {issues_num}")
    print(f"Tokens: prompt:{g_token_stat.prompt_tokens}  answers:{g_token_stat.answer_tokens}   total:{g_token_stat.answer_tokens + g_token_stat.prompt_tokens}")

    elapsed = end_time-start_time
    print(f"Elapsed time is: {elapsed:.2f} sec")
    print(f"Average seconds per issues: {(elapsed/issues_num):.2f} sec")

    print(f"Output path is: {args.output_folder}")

if __name__ == "__main__":
    main()
