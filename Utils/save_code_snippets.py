#!/usr/bin/env python3

import json
import sys
import time
import os
from dataclasses import dataclass
import re
import argparse

@dataclass
class Stat:
    files:int = 0
    skipped_files_unknown_type:int = 0
    skipped_files_wrong_lang:int = 0
    sharings:int  = 0
    conversations:int = 0
    codes:int = 0
    source_data:int = 0

@dataclass
class SharingInfo:
    url:str = ""
    date:str = ""
    title:str = ""
    model:str=""
    num_of_prompts:int=0
    tokens_of_prompts:int=0
    tokens_of_answers:int=0
    num_of_conversations:int=0
    html_content_size:int = 0
    html_content:str = ""

@dataclass
class SourceInfo:
    type:str = ""
    id:str = ""
    url:str = ""
    author:str = ""
    points:str = ""
    title:str = ""
    story_text:str = ""
    created_date:str = ""
    number_of_sharings:int = 0
    number_of_comments:int = 0

# g_BASEFOLDER="d:\\GitHub\\DevGPT\\snapshot_20231012\\"

# By default we scan all json files in the DevGPT folder
#FILES=["20231012_230826_commit_sharings.json", "20231012_232232_hn_sharings.json", "20231012_233628_pr_sharings.json", "20231012_234250_file_sharings.json", "20231012_235128_issue_sharings.json", "20231012_235320_discussion_sharings.json"]
FILES=["20231012_232232_hn_sharings.json"]

# Supported extensions
# File extension for each language type
ALL_SUPPORTED_EXTENSIONS= {"cpp":"cpp", "c++":"cpp",  "c":"c", "csharp":"cs", "c#":"cs", "java":"java", "python":"py"}
REQUESTED_EXTENSIONS = {}

# support languages in command line arguments
# for each command line aguments we have possible languages types from DevGPT dataset
COMMAND_LINE_LANGUAGES = { "cpp":["cpp", "c++", "c"], "csharp":["csharp", "c#"], "java":["java"], "python":["python"] }

g_langs = dict()
g_code_folder = "Code"
g_stat = Stat()

def load_json(file_path):
    """
    Loads a JSON file and returns its content.
    
    :param file_path: The path to the JSON file.
    :return: The content of the JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            start = time.process_time()
            print(f"Started loading file: {file_path}")
            elapsed = time.process_time() - start
            print(elapsed)
            print(f"Time elapsed: {elapsed}")
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
    return None

def get_all_json_files(folder):
    """
    Recursively searches the given folder and returns a list of paths to all JSON files.

    :param folder: The path to the folder to search
    :return: A list of file paths to JSON files
    """
    json_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))

    return json_files

def load_all_files(sourceFolder, file_names = None):

    if file_names is None:
        all_files = get_all_json_files(sourceFolder)
    else:
        all_files = file_names

    devGPT = dict()
    for current_file in all_files:

        if file_names is None:
            full_name = current_file
        else:
            full_name = sourceFolder + current_file

        print(f"Current file is: {full_name}")
        json_data = load_json(full_name)
        devGPT[current_file] = json_data
    return devGPT 

def display_lang_stat(lstat):
    print(f"\nLanguage statistics collection size: {len(lstat)}")
    sorted_lang = sorted(lstat.items(), key=lambda item: item[1], reverse=True)

    total = 0
    for lang, lnum in sorted_lang:
        # lnum = sorted_lang[lang]
        print(f"[{lang}] - [{lnum}]")
        total += lnum
    print(f"Total: {total}")


# check that folders are available
def ensure_directories(file_path):
    # Get the directory part of the file path
    directory = os.path.dirname(file_path)

    # Check if the directory exists
    if not os.path.exists(directory):
        # If the directory doesn't exist, create it and all intermediate directories
        os.makedirs(directory)
        print(f"Directories created for the path: {directory}")
    else:
        print(f"All directories already exist for the path: {directory}")

# get source file from data set and save it as separate file
def save_text_file(file_name, data):
    # print(f"Full name is: {file_name} ")
    if data is None:
        return

    ensure_directories(file_name)
    try:
        with open(file_name,"w+", encoding='utf-8') as f:
            f.write(data)
    except Exception as e:
        print(e)

def get_name_for_item(item):
    name = ""
    if "Author" in item:
        name = name + "_" + item["Author"]

    if "RepoLanguage" in item and item["RepoLanguage"] != None:
        name = name + "_" + item["RepoLanguage"]

    if "Sha" in item:
        name = name + "_" + item["Sha"]

    if name == "":
        name = "NoName_" + str(hash(item))

    return name

def merge_string(input_string):
    modified_string = input_string.replace(" ", "_")
    modified_string = re.sub(r'[^\w_]', '', modified_string)
    return modified_string

def get_value_with_check(data, property_name, default_value):
    value = default_value
    if property_name in data:
        value = data[property_name]
    return value

def update_lang_stat(lang):
    global g_langs
    if lang in g_langs:
        g_langs[lang] = g_langs[lang] + 1
    else:
        g_langs[lang] = 1


def get_sharing_info(sharing):
    info = SharingInfo()
    info.url = get_value_with_check(sharing, "URL", "No Url")
    info.date = get_value_with_check(sharing, "DateOfConversation", "No date")
    info.title = get_value_with_check(sharing, "Title", "No title")
    info.num_of_prompts = get_value_with_check(sharing, "NumberOfPrompts",0)
    info.tokens_of_prompts = get_value_with_check(sharing, "TokenOfPrompts",0)
    info.tokens_of_answers = get_value_with_check(sharing, "TokenOfAnswers",0)
    info.model = get_value_with_check(sharing, "Model","No model")

    conv = get_value_with_check(sharing, "Conversations",None)
    if conv is not None:
        info.num_of_conversations = len(conv)

    html = get_value_with_check(sharing, "HTMLContent","");
    info.html_content_size = len(html)
    info.html_content = html
    return info

def get_sharing_info_string(sinfo):
    r = "Sharing info: \n"
    r += f"Title:{sinfo.title}\nDate:{sinfo.date}\n"
    r += f"Url:{sinfo.url}\nModel name:{sinfo.model}"
    r += f"Number of prompts:{sinfo.num_of_prompts}\nTokens of prompts:{sinfo.tokens_of_prompts}\n"
    r += f"Tokens of answers:{sinfo.tokens_of_answers}\nNumber of conversations:{sinfo.num_of_conversations}\n"
    r += f"HTML content size:{sinfo.html_content_size}"
    return r

def save_sharing_info(folder_path, sharing_info):
    text = get_sharing_info_string(sharing_info)
    save_text_file(os.path.join(folder_path, "sharing_info.txt"), text)
    save_text_file(os.path.join(folder_path, "html_content.html"), sharing_info.html_content)


def check_if_sharing_has_any_code_for_us(sharing):

    conversations = get_value_with_check(sharing, "Conversations", None)
    if conversations is None:
        return False

    for cnv in conversations:
        list_of_code = get_value_with_check(cnv, "ListOfCode", None)
        if list_of_code is None:
            continue

        for code in list_of_code:
            type = get_value_with_check(code, "Type", None)

            if type is None:
                continue

            # true if we have at least one file in this sharing
            if type in REQUESTED_EXTENSIONS:
                return True

    return False


def proceed_source_code(filename, item, source_folder):
    global g_code_folder, g_total_files, g_langs
    num = get_value_with_check(item, "ID", 0)

    if "ChatgptSharing" not in item:
        print (f"No chat gpt interaction in {filename} Num: {num}")
        return

    is_any_data_saved = False
    # proceed code
    sharings = item["ChatgptSharing"]
    for sharing in sharings:
        if "Conversations" not in sharing:
            print (f"No chat gpt interaction in {filename} Num: {num}")
            return

        if not check_if_sharing_has_any_code_for_us(sharing):
            print (f"No chat gpt interaction in {filename} with languages we want.")
            continue

        date_of_sharing = merge_string(get_value_with_check(sharing, "DateOfConversation", "NoDate"))
        title = get_value_with_check(sharing, "Title", "NoTitle")
        sharing_folder = os.path.join(source_folder, "Sharing_" + merge_string(title) + "_" + date_of_sharing)
        conversations = sharing["Conversations"]

        cnv_index = 1
        for cnv in conversations:
            list_of_code = cnv["ListOfCode"]
            if list_of_code is None:
                continue

            conversation_folder = os.path.join(sharing_folder, "Conversation_" + str(cnv_index).zfill(3))

            code_index = 1
            for code in list_of_code:
                ext = None

                if "Type" in code:
                    lang = code["Type"]

                    if lang is None:
                        g_stat.skipped_files_unknown_type += 1
                        continue

                    lang = str.lower(lang)

                    if lang in REQUESTED_EXTENSIONS:
                        ext = REQUESTED_EXTENSIONS[lang]
                    else:
                        print(f"Programming language is not requested : {lang}")
                        g_stat.skipped_files_wrong_lang += 1
                        continue

                code_file_name = os.path.join(conversation_folder, "Code_" + str(code_index).zfill(3))
                current_file_name = code_file_name + "." + ext
                print(f"current_file_name: {current_file_name} ")

                if "Content" in code:
                    content = code["Content"]
                    save_text_file(current_file_name, content)
                    update_lang_stat(ext)
                    code_index += 1
                    g_stat.codes += 1
                    g_stat.files += 1
                    is_any_data_saved = True

            prompt = get_value_with_check(cnv, "Prompt", "")
            prompt_file_name = os.path.join(conversation_folder, "Prompt.txt")
            save_text_file(prompt_file_name, prompt)

            answer = get_value_with_check(cnv, "Answer", "")
            answer_file_name = os.path.join(conversation_folder, "Answer.txt")
            save_text_file(answer_file_name, answer)
            code_index += 1
            g_stat.conversations += 1

            cnv_index += 1

        sinfo = get_sharing_info(sharing)
        save_sharing_info(sharing_folder, sinfo)
        g_stat.sharings += 1

    return is_any_data_saved

def get_source_info(sdata):
    info = SourceInfo()
    info.type = get_value_with_check(sdata, "Type", "No type")
    info.id = get_value_with_check(sdata, "ID", "No id")
    info.url = get_value_with_check(sdata, "URL", "No url")
    info.author = get_value_with_check(sdata, "Author", "No author")
    info.points = get_value_with_check(sdata, "Points", "No points")
    info.title = get_value_with_check(sdata, "Title", "No title")
    info.story_text = get_value_with_check(sdata, "StoryText", "")
    info.created_date = get_value_with_check(sdata, "CreatedAt", "No creation date")
    info.number_of_comments = get_value_with_check(sdata, "CommentsTotalCount", "No comment numbers")

    sharings = get_value_with_check(sdata, "ChatgptSharing", None)
    if sharings is not None:
        info.number_of_sharings = len(sharings)

    return info

def get_source_info_text(sinfo):
    r = "Source data info: \n"
    r += f"Title: {sinfo.title}\nDate: {sinfo.created_date}\n"
    r += f"Url: {sinfo.url}\nType: {sinfo.type}\nID: {sinfo.id}\n"
    r += f"Author: {sinfo.author}\nNumber of points: {sinfo.points}\n"
    r += f"Number of comments: {sinfo.number_of_comments}\n"
    r += f"Number of sharings: {sinfo.number_of_sharings}\n"
    r += f"\nStory text:\n{sinfo.story_text}\n"
    return r

def save_source_info(folder_path, source_data):
    info_data = get_source_info(source_data)
    info_text = get_source_info_text(info_data)
    save_text_file(os.path.join(folder_path, "source_data_info.txt"), info_text)

    if info_data.story_text is not None and len(info_data.story_text) > 0:
        save_text_file(os.path.join(folder_path, "source_data_story.html"), info_data.story_text)

# loop for files
def process_data(dataset, output_folder):

    for filedata in dataset:
        print(f"\n --- File: {filedata} ---")
        sources = dataset[filedata]["Sources"]
        print(f"File name: {filedata}   Sources len : {len(sources)}")

        file_output_folder = os.path.join(output_folder, g_code_folder, merge_string( os.path.basename(filedata)))

        langs = dict()
        # iteration for records in file
        for source_data in sources:

            g_stat.source_data += 1
            date_of_source = merge_string(get_value_with_check(source_data, "CreatedAt", "NoDate"))
            title = get_value_with_check(source_data, "Title", "NoId")
            output_source_folder = os.path.join(file_output_folder, "Source_" + merge_string(title) + "_" + date_of_source)

            if "RepoLanguage" in source_data:
                lang = source_data["RepoLanguage"]
                if lang in langs:
                    langs[lang] = langs[lang] + 1
                else:
                    langs[lang] = 1

            data_saved = proceed_source_code(filedata, source_data, output_source_folder)

            if data_saved:
                save_source_info(output_source_folder, source_data)

        display_lang_stat(langs)

def print_statistics(st):
    print(f"--- Stats ---\nFiles saved with requested languages: {st.files}")
    print(f"Files with language we don't need: {st.skipped_files_wrong_lang}")
    print(f"Files with unknown language: {st.skipped_files_unknown_type}")
    print(f"Number of source data in json files: {st.source_data}")
    print(f"Sharings saved: {st.sharings}")
    print(f"Conversations in these sharings: {st.conversations}")
    print(f"Code files in these conversations: {st.codes}")

def parse_arguments():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Process dev GPT data set folder and output folder with optional language filters.')

    # Positional arguments
    parser.add_argument('dataset_folder', type=str, help='Path to the dev GPT data set folder')
    parser.add_argument('output_folder', type=str, help='Path to the output folder')

    # Optional arguments for languages,
    parser.add_argument('--lang', action='append', choices=['cpp', 'csharp', 'java', 'python'], help='Programming languages to process')

    # Parse the arguments
    args = parser.parse_args()

    # Check if at least one language is specified
    if not args.lang:
        parser.error("At least one --lang option must be specified.")

    return args


def generate_requested_extensions(requested_langs):
    global REQUESTED_EXTENSIONS

    for lan in requested_langs:
        cmd_lang_types = COMMAND_LINE_LANGUAGES[lan]
        for lang_type in cmd_lang_types:
            extension = ALL_SUPPORTED_EXTENSIONS[lang_type]
            # now update REQUESTED_EXTENSIONS
            REQUESTED_EXTENSIONS[lang_type] = extension

    print(f"REQUESTED_EXTENSIONS : {REQUESTED_EXTENSIONS}")

def main():
    global g_langs
    args = parse_arguments()

    # Example usage
    print(f"Dataset Folder: {args.dataset_folder}")
    print(f"Output Folder: {args.output_folder}")

    if args.lang:
        print(f"Languages: {', '.join(args.lang)}")
    else:
        print("No languages specified")

    generate_requested_extensions(args.lang)

    print(f"SUPPORTED_EXTENSIONS main : {REQUESTED_EXTENSIONS}")

    start_time = time.time()

    devgpt_folder = args.dataset_folder
    output_folder = args.output_folder

    print(f"Output folder is: {output_folder}")

    if os.path.isdir(output_folder):
        print(f"Folder exists: {output_folder}")
    else:
        print(f"Folder NOT exists: {output_folder}")

    # debug version
    #dt = load_all_files(devgpt_folder, FILES)
    dt = load_all_files(devgpt_folder)
    print(f"Files loaded: {len(dt)}")

    # iterate all data in dataset
    process_data(dt, output_folder)
    print_statistics(g_stat)
    display_lang_stat(g_langs)

    end_time = time.time()
    print(f"Elapsed time is: {end_time-start_time:.2f} sec")

if __name__ == "__main__":
    main()
