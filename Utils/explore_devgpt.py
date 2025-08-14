#!/usr/bin/env python3
import json
import sys
import os
import time
from dataclasses import dataclass
import argparse

SUPPORTED_LANGUAGES=["C", "C++", "Java", "Python", "C#", "Swift"]

@dataclass
class Stat:
    files:int = 0
    sources: int = 0
    sharings: int = 0
    conversations: int = 0
    code_items: int = 0

g_langs = dict()
g_code_folder = "Code"
g_st = Stat()

# models statistics for sharings
g_models = dict()

def load_json(file_path):
    """
    Loads a JSON file and returns its content.
    
    :param file_path: The path to the JSON file.
    :return: The content of the JSON file.
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            start = time.process_time()
            # print(f"Started loading file: {file_path}")
            elapsed = time.process_time() - start
            # print(f"Time elapsed: {elapsed}")
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
    return None

def get_json_files(folder_path):
    """
    Returns a list of all JSON file paths in the specified folder.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Provided path is not a valid directory: {folder_path}")

    return [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.lower().endswith(".json") and os.path.isfile(os.path.join(folder_path, file))
    ]

#
# def print_data_structure(data, indent=0):
#     """
#     Prints the data structure of the JSON content.
#
#     :param data: The data to print.
#     :param indent: The current indentation level.
#     """
#     indent_space = ' ' * indent
#     if isinstance(data, dict):
#         for key, value in data.items():
#             print(f"{indent_space}{key} (type: {type(value).__name__})")
#             print_data_structure(value, indent + 2)
#     elif isinstance(data, list):
#         print(f"{indent_space}Array of {len(data)} elements:")
#         if len(data) > 0:
#             print_data_structure(data[0], indent + 2)
#         else:
#             print(f"{indent_space}  Empty Array")

def load_all_files(fileNames):
    devGPT = dict()
    for filePath in fileNames:
        # print(f"Current file is: {filePath}")
        json_data = load_json(filePath)
        devGPT[filePath] = json_data
    return devGPT 

def display_lang_stat(lstat, st, models):
    print(f"Language statistics collection size: {len(lstat)}")
    sorted_lang = sorted(lstat.items(), key=lambda item: item[1], reverse=True)

    for lang, lnum in sorted_lang:
        if lnum > 50:
            print(f"[{lang}] - [{lnum}]")

    print(f"Models statistics collection size: {len(models)}")
    sorted_models = sorted(models.items(), key=lambda item: item[1], reverse=True)

    total_md = 0
    for md, mdnum in sorted_models:
        print(f"[{md}] - [{mdnum}]")
        total_md = total_md + mdnum

    print(f"\nTotal number of models: {total_md}")
    printStat(st)

def get_value_with_check(data, property_name, default_value):
    value = default_value
    if property_name in data:
        value = data[property_name]
    return value

def process_data(dt):
    global g_st, g_langs, g_models

    for d in dt:
        # print(f"\n --- File: {d} ---")
        src = dt[d]["Sources"]

        g_st.sources += len(src)
        # print(f"File name: {d}   Sources len : {len(src)}")

        # now in sources
        firstType = src[0]["Type"]
        # print(f"Expected data type for file: {firstType}")

        for source_item in src:

            sharings = get_value_with_check(source_item,"ChatgptSharing", None)
            if sharings is None:
                continue

            g_st.sharings += len(sharings)

            for sharing in sharings:
                conversations = get_value_with_check(sharing,"Conversations", None)

                if conversations is None:
                    continue

                g_st.conversations += len(conversations)

                model = get_value_with_check(sharing,"Model", "Unknown")
                # print(f"Model : {model}")
                if model in g_models:
                    g_models[model] = g_models[model] + 1
                else:
                    g_models[model] = 1

                for conversation in conversations:

                    list_of_code = get_value_with_check(conversation,"ListOfCode", None)
                    if list_of_code is None:
                        continue

                    g_st.code_items += len(list_of_code)

                    for code in list_of_code:

                        content = get_value_with_check(code,"Content", None)
                        if content is None:
                            continue

                        # now detect language
                        lang = get_value_with_check(code,"Type", None)
                        if lang is None:
                            lang = "unknown"

                        lang = str.lower(lang)

                        # language names fix
                        if lang == "c#":
                            lang = "csharp"

                        if lang == "c++":
                            lang = "cpp"

                        # only if we have something here
                        if len(content) > 0:
                            if lang in g_langs:
                                g_langs[lang] = g_langs[lang] + 1
                            else:
                                g_langs[lang] = 1

        # print(f"For file {d}: data type is: {firstType}")

def printStat(st):
    print(f"Code statistics: code_items:[{st.code_items}] in conversations: [{st.conversations}] in sharings: [{st.sharings}] in sources: [{st.sources}] in json files:[{st.files}]")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scan all supported files using scanners ")
    parser.add_argument("--dataset_folder", required=True, type=str, help="Path to DevGPT spanshot folder")
    return parser.parse_args()

def main():
    global g_langs, g_st, g_models
    args = parse_arguments()

    print(f"Dataset folder: {args.dataset_folder}")
    json_files = get_json_files(args.dataset_folder)

    g_st.files = len(json_files)

    print(f"Json files loaded: [{len(json_files)}] :: {json_files}  ")

    dt = load_all_files(json_files)
    # print(f"Files loaded: {len(dt)}")

    process_data(dt)

    print("\nGlobal language statistics:")
    display_lang_stat(g_langs, g_st, g_models)

if __name__ == "__main__":
    main()
