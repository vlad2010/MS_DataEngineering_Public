import os
from openai import OpenAI
import openai_api_common
import json
import sys
from datetime import datetime

api_key = openai_api_common.read_file_content("..\api-key.txt")
client = OpenAI(api_key=api_key)
g_chat = [{"role": "system", "content": "You are a helpful assistant."}]

def print_responce(responce):
    json_object = json.loads(responce)
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

def create_folder(substring, directory):
    # Get the current date and time in the format "_DD_MM_YYYY_HH_MM"
    current_time = datetime.now().strftime("_%d_%m_%Y_%H_%M")

    # Create the folder name by appending the date and time to the substring
    folder_name = f"{substring}{current_time}"
    full_path = os.path.join(directory, folder_name)

    # Create the folder
    os.makedirs(full_path, exist_ok=True)

    # Return the folder name for confirmation
    return full_path


def save_to_file(filename, text):
    # Open the file in write mode (this will create the file if it doesn't exist)
    with open(filename, 'w') as file:
        # Write the provided text to the file
        file.write(text)
    # Return confirmation message
    return f"Text saved to {filename}"


def send_message_to_gpt(prompt):
    global g_chat
    try:

        g_chat.append({"role": "user", "content": prompt})

        # Send a request to the OpenAI API
        response = client.chat.completions.create(
          model="gpt-4o-mini",
          messages = g_chat,
          seed = 1000
        )

        # Extract the response text
        message = response.choices[0].message.content
        print(f"Answer: {message}")

        # update chat list immediately with new answer
        g_chat.append({"role": "assistant", "content": message})

        return message

    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    # parameters
    if(len(sys.argv) < 3):
        print("Usage: exe <iterations> <prompt file> <path_to_output_folder>")
        sys.exit(-1)

    try:
        iters = int(sys.argv[1])
        prompt_file = sys.argv[2]
        output_folder = sys.argv[3]

        user_prompt = openai_api_common.read_file_content(prompt_file)

        # iters = int(user_input)
        print(f"Number of iterations: {iters}")
        print(f"Prompt: {user_prompt}")
        print(f"Output folder: {output_folder}")

        folder_name = create_folder("openai_reproductive_results", output_folder)

        for i in range(iters):
            # Send the message to the GPT API

            response = send_message_to_gpt(user_prompt)
            filename = os.path.join(folder_name, f"answer_{str(i).zfill(3)}.txt")
            print(f"Next file name is: {filename}")
            save_to_file(filename, response)

        # Print the response
        # print("GPT Response:", response)
        # print(g_chat)
    except Exception as e:
        print(f"An error occurred: {e}")
        