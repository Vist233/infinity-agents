import openai

API_BASE = "https://api.lingyiwanwu.com/v1"
API_KEY = "1352a88fdd3844deaec9d7dbe4b467d5"

openai.api_key = API_KEY

openai.api_base = API_BASE

messages = [
    {"role": "system", "content": "You could respond yes or no"}
]

def chat_with_memory(user_input):
   
    messages.append({"role": "user", "content": user_input})

   
    completion = openai.ChatCompletion.create(
        model="yi-lightning",
        messages=messages
    )

   
    assistant_reply = completion.choices[0].message['content']

   
    messages.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply

user_input = "Is sun a circle?"
print("User:", user_input)
assistant_reply = chat_with_memory(user_input)
print("Assistant:", assistant_reply)

user_input = "What can you do?"
print("User:", user_input)
assistant_reply = chat_with_memory(user_input)
print("Assistant:", assistant_reply)

