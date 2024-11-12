import os
from openai import OpenAI
import base64
import httpx
API_BASE = "https://api.lingyiwanwu.com/v1"
API_KEY = "1352a88fdd3844deaec9d7dbe4b467d5"
client = OpenAI(
  api_key=API_KEY,
  base_url=API_BASE
)

# Accept input image from user
input_image_path = input("Enter the path of the input image: ")
with open(input_image_path, "rb") as input_image_file:
    input_image = "data:image/jpeg;base64," + base64.b64encode(input_image_file.read()).decode('utf-8')

# Generate process_images.py
process_images_code = f"""
import os
import base64
import httpx
from openai import OpenAI

API_BASE = "{API_BASE}"
API_KEY = "{API_KEY}"
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

input_image = "{input_image}"

for filename in os.listdir('.'):
    if filename.endswith('.png'):
        with open(filename, 'rb') as img_file:
            image = "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="yi-vision",
            messages=[
                {{
                    "role": "user",
                    "content": [
                        {{
                            "type": "text",
                            "text": "请你根据第一张的图片抱合类型标准，判断第二张图片的抱合类型。并按照\"[<第一张图片的抱合类型>,<第二张图片的抱合类型>]\"输出"
                        }},
                        {{
                            "type": "image_url",
                            "image_url": {{
                                "url": input_image
                            }}
                        }},
                        {{
                            "type": "image_url",
                            "image_url": {{
                                "url": image
                            }}
                        }}
                    ]
                }},
            ]
        )
        print(f"Result for {{filename}}: {{completion}}")
"""

with open("process_images.py", "w") as f:
    f.write(process_images_code)

# Approach 1: use image URL
# image1 = "https://platform.lingyiwanwu.com/assets/LLMquality.jpg"
# image2 = "https://platform.lingyiwanwu.com/assets/LLMspeed.jpg"
# image3 = "https://platform.lingyiwanwu.com/assets/LLMprice.jpg"
# Approach 2: use image URL and encode it to base64
# image_url = "https://platform.lingyiwanwu.com/assets/sample-table.jpg"
# image_media_type = "image/jpeg"
# image = "data:image/jpeg;base64," + base64.b64encode(httpx.get(image_url).content).decode("utf-8")
# Approach 3: use local image and encode it to base64
image_path1 = "./Strandard.png"
image_path2 = "./22A-T-34-5球形侧视图.JPG"
image_path3 = "./22A-T-34-2球形侧视图.JPG"

with open(image_path1, "rb") as image_file1:
  image1 = "data:image/jpeg;base64," + base64.b64encode(image_file1.read()).decode('utf-8')
with open(image_path2, "rb") as image_file2:
  image2 = "data:image/jpeg;base64," + base64.b64encode(image_file2.read()).decode('utf-8')
with open(image_path3, "rb") as image_file3:
  image3 = "data:image/jpeg;base64," + base64.b64encode(image_file3.read()).decode('utf-8')

# Make a request, can be multi round
completion = client.chat.completions.create(
  model="yi-vision",
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "请你根据第一张的图片抱合类型标准，判断第二张、第三张图片的抱合类型。并按照\"[<第一张图片的抱合类型>,<第二张图片的抱合类型>]\"输出"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": image1
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url": image2
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url": image3
          }
        }
      ]
    },
  ]
)
print(completion)
