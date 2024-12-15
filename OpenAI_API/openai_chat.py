from openai import OpenAI
import openai_api_common
import json

api_key = openai_api_common.read_file_content("..\api-key.txt")
client = OpenAI(api_key=api_key)
g_chat = [{"role": "system", "content": "You are a helpful assistant."}]

def print_responce(responce):
    json_object = json.loads(responce)
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

def send_message_to_gpt(prompt):
    global g_chat
    try:

        g_chat.append({"role": "user", "content": prompt})

        # Send a request to the OpenAI API
        response = client.chat.completions.create(
          model="gpt-4o-mini",
          messages = g_chat
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
    while True:
        # Get user input
        user_input = input("Enter your message (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        # Send the message to the GPT API
        response = send_message_to_gpt(user_input)

        # Print the response
        # print("GPT Response:", response)
        # print(g_chat)