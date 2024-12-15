#!/usr/bin/env python3

import argparse
import os.path
import subprocess
import platform
from datetime import datetime
import os
import time

#snyk
# snyk code test --org=c0d94333-4cd8-4428-8599-9080ca7cef78 --sarif-file-output="%report_filename%"

# git commands
GIT_ADD = ["git", "add"]
GIT_RESET = ["git", "reset"]


g_scanners = {

    # for Snyk add log file
    # new org ? dbd1a015-1a84-4971-8d00-8c62b004acf5
    # "snyk":["snyk", "code", "test","--org=c0d94333-4cd8-4428-8599-9080ca7cef78", "--sarif-file-output=" ],
    "snyk":["snyk", "code", "test","--org=dbd1a015-1a84-4971-8d00-8c62b004acf5", "--sarif-file-output=" ],
    # "cppcheck":[  "cppcheck", "--help" ]
    "cppcheck":[ "cppcheck", "--quiet", "--enable=warning,style,performance,portability,information,unusedFunction", "--error-exitcode=1", "--force", "--inconclusive",
                 "--suppress=missingIncludeSystem",
                 "--suppress=missingInclude",
                 "--suppress=missingIncludeSystem",
                 "--suppress=missingInclude",
                 "--suppress=syntaxError",
                 "--suppress=unusedStructMember",
                 "--suppress=unreadVariable",
                 "--suppress=passedByValue",
                 "--suppress=constParameter",
                 "--suppress=unusedFunction",
                 "--suppress=unusedVariable",
                 "--suppress=constVariable",
                 "--suppress=functionConst",
                 "--suppress=constParameterPointer",
                 "--suppress=noExplicitConstructor",
                 "--suppress=cstyleCast",
                 "--suppress=variableScope",
                 "--suppress=normalCheckLevelMaxBranches",
                 "--suppress=unusedPrivateFunction",
                 "--suppress=functionStatic",
                 "--suppress=functionConst",
                 "--suppress=initializerList",
                 "--suppress=constParameterReference",
                 "--suppress=useStlAlgorithm",
                 "--suppress=unknownMacro",
                 "--suppress=constVariablePointer",
                 "--suppress=constParameterCallback",
                 "--suppress=ctuOneDefinitionRuleViolation",
                 "--suppress=syntaxError",  "--template=gcc", "."],
    # "semgrep":["semgrep", "scan", "-v", "--no-force-color", "--sarif", "--text", "--exclude '**/*.html'",  "--include '**/*.c'", "--include '**/*.cpp'", "--include '**/*.cs'", ".", "--sarif-output="],
    "semgrep":["semgrep", "scan", "-v", "--no-force-color", "--sarif", "--text", "--exclude=*.html", "--exclude=*.htm", "--exclude=*.txt", ".", "--sarif-output="],
    "flawfinder":["python3", "-m", "flawfinder", "--sarif", "."]
}

def print_command(cmds):
    print("Command: [", end='')
    for cmd in cmds:
        print(cmd + " ", end='')
    print("]")

def generate_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def generate_report_name(scanner, timestamp, ext):
    return f"report_{scanner}_{timestamp}.{ext}"

# check that folders are available
def ensure_directories(file_path):
    # Get the directory part of the file path
    directory = os.path.dirname(file_path)

    # Check if the directory exists
    if not os.path.exists(directory):
        # If the directory doesn't exist, create it and all intermediate directories
        os.makedirs(directory)

def save_text_to_file(text, file_path):
    ensure_directories(file_path)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Text successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_command(cmd, is_stderr = False):
    """
    Run a command-line application with multiple parameters and capture its output.
    
    Args:
        command (str): The command to run.
        *args (str): Additional arguments for the command.

    Returns:
        str: Output from the command.
    """
    try:
        # Run the command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            shell=(platform.system() == 'Windows')  # shell=True for Windows
        )

        if result.returncode != 0:
            print(result.stderr.strip())

        # Check if the command ran successfully
        # result.check_returncode()  # Raise CalledProcessError if exit code is non-zero

        # err = result.stderr.strip()
        # print(f"Err : ", err)
        # stdout_txt = result.stdout.strip()
        # print(f"Std : ", stdout_txt)

        if is_stderr:
            return result.stderr.strip()

        # Return the output from stdout
        return result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        # Print or log the error as needed
        print(f"Error running command: {e.stderr}")
        print(f"Error running command: {e}")
        return e.stderr.strip()

def run_cpp_check_converter(report_file, sources_folder):
    without_ext = os.path.splitext(report_file)[0]
    json_report = f"{without_ext}.json"
    # input_file   output_json_file source_folder   --extensions c cpp

    print(f"Cpp check json report: {json_report}")

    CPPCHECK_REPORT_CONVERTER = ["python3", "../CppCheck/cppcheck_converter.py", report_file, json_report, sources_folder, "--extensions", "c", "cpp", "cs"]
    # filename.rsplit( ".", 1 )[ 0 ]
    run_command(CPPCHECK_REPORT_CONVERTER)
    return json_report

def run_sarif_converter(report_file, sources_folder):
    without_ext = os.path.splitext(report_file)[0]
    json_report = f"{without_ext}.json"
    # input_file   output_json_file source_folder   --extensions c cpp

    print(f"Sarif converted json report: {json_report}")

    SARIF_REPORT_CONVERTER = ["python3", "../Sarif_To_MyErrorFormat/sarif_to_simple.py", report_file, json_report, sources_folder, "--extensions", "c", "cpp"]
    # filename.rsplit( ".", 1 )[ 0 ]
    run_command(SARIF_REPORT_CONVERTER)
    return json_report

def generate_grouped_report(report_file):
    group_key = "sharing"
    CMD = ["python3", "../Sarif_To_MyErrorFormat/print_grouped_error_log.py", report_file, "sharing"]

    without_ext = os.path.splitext(report_file)[0]
    grouped_log = f"{without_ext}_grouped_{group_key}.txt"
    output = run_command(CMD)
    save_text_to_file(output, grouped_log)

def run_intersections_script(timestamp):
    intersection_report_name = f"./intersections_{timestamp}.txt"
    CMD = ["python3", "../../Sarif_To_MyErrorFormat/sharings_intersections.py", ".", intersection_report_name]
    output = run_command(CMD)
    print(output)

    intersection_report_name = f"./intersections_fullpath_{timestamp}.txt"
    CMD = ["python3", "../../Sarif_To_MyErrorFormat/sharings_intersections.py", ".", intersection_report_name, "--full-path"]
    CMD.append("--full-path")
    output = run_command(CMD)
    print(output)

    intersection_report_name = f"./intersections_fullpath_linenumbers_{timestamp}.txt"
    CMD = ["python3", "../../Sarif_To_MyErrorFormat/sharings_intersections.py", ".", intersection_report_name, "--full-path", "--line-numbers"]
    output = run_command(CMD)
    print(output)

# ../Utils/get_unique_files.py  ./reports/unique_files.json
# ./reports/uniqie_info.txt reports/report_cppcheck_2024_10_27_17_58_41.json
# reports/report_flawfinder_2024_10_27_17_58_41.json
# reports/report_semgrep_2024_10_27_17_58_41.json
# reports/report_snyk_2024_10_27_17_58_41.json

# def run_uniqie_script(timestamp):



def parse_arguments():
    parser = argparse.ArgumentParser(description="Scan all supported files using scanners ")

    parser.add_argument("--input_folder", required=True, type=str, help="Path to file with prompt")
    parser.add_argument("--output_folder", required=True, type=str, help="Path to output folder")
    parser.add_argument('--git_add', action='store_true', help="Enable git add (default: False)")

    parser.add_argument(
        '--scanners',
        nargs='+',   # Ensures a list of values
        required=True,  # At least one scanner is required
        help="List of scanners to use (minimum one scanner required) (cppcheck, snyk, semgrep, flawfinder)"
    )

    args = parser.parse_args()
    return args


def run_scanners(input_folder, reports_folder, scanners, is_git_add = False):
    # global g_scanners
    timestamp = generate_timestamp()

    print(f"Reports folder: {reports_folder}")
    print(f"Current folder is : {os.getcwd()}")

    for scanner in scanners:

        if scanner in g_scanners:
            arguments = g_scanners[scanner]
        else:
            print(f"Unknown scanner: {scanner}")
            return

        cur_folder = os.getcwd()

        if scanner == "semgrep" and is_git_add:
            GIT_ADD.append(input_folder)
            git_add_out = run_command(GIT_ADD, True)
            print(f"git add out: {git_add_out}")

        # chang current folders
        os.chdir(input_folder)

        ext = "sarif"
        if scanner == "cppcheck":
            ext = "txt"

        report_name = generate_report_name(scanner, timestamp, ext)

        report_full_path = os.path.join(reports_folder, report_name)

        if scanner == "snyk" or scanner == "semgrep":
            arguments[-1] += report_full_path

        print(f"Scanner: {scanner}")
        print(f"Args: {arguments}")
        print(f"Report name: {report_name}")

        print_command(arguments)

        is_err = False
        if scanner == "semgrep" or scanner == "cppcheck":
            is_err = True

        output = run_command(arguments, is_err )

        if scanner == "flawfinder" or scanner == "cppcheck":
            save_text_to_file(output, report_full_path)

        os.chdir(cur_folder)

        if scanner=="cppcheck":
            json_report = run_cpp_check_converter(report_full_path, input_folder)
        else:
            json_report = run_sarif_converter(report_full_path, input_folder)

        generate_grouped_report(json_report)

        if scanner == "semgrep":
            log_path = os.path.join(reports_folder, f"semgrep_log_{timestamp}.txt")
            save_text_to_file(output, log_path)
            if is_git_add:
                GIT_RESET.append(input_folder)
                run_command(GIT_RESET)

    # after all scanners tun intersection script
    cur_folder = os.getcwd()
    os.chdir(reports_folder)
    run_intersections_script(timestamp)
    os.chdir(cur_folder)

def main():

    start_time = time.time()
    args = parse_arguments()

    print(f"Input folder: {args.input_folder}")
    print(f"Output folder: {args.output_folder}")

    print(f"Scanners: {args.scanners}")

    # Example usage:
    # output = run_command("echo", "Hello, World!")
    # print("Command Output:", output)

    absolute_report_path = os.path.abspath(args.output_folder)
    run_scanners(args.input_folder, absolute_report_path, args.scanners, args.git_add)

    end_time = time.time()

    elapsed = end_time-start_time
    print(f"Elapsed time is: {elapsed:.2f} sec")

if __name__ == "__main__":
    main()