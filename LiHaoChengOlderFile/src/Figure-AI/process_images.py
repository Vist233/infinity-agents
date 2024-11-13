
import os
import base64
import httpx
from openai import OpenAI

API_BASE = "https://api.lingyiwanwu.com/v1"
API_KEY = "1352a88fdd3844deaec9d7dbe4b467d5"
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

input_image = "data:image/jpeg;base64,{input_image}"

for filename in os.listdir('.'):
    if filename.endswith('.png'):
        with open(filename, 'rb') as img_file:
            image = "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="yi-vision",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请你根据第二张的图片抱合类型标准，判断第一张图片的抱合类型。并按照\"[<第一张图片的抱合类型>,<第二张图片的抱合类型>]\"输出"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": input_image
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            }
                        }
                    ]
                },
            ]
        )
        print(f"Result for {filename}: {completion}")