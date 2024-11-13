import os
import openai
import base64
import httpx
import subprocess
import tempfile

# # Approach 1: use image URL
# # image1 = "https://platform.lingyiwanwu.com/assets/LLMquality.jpg"
# # image2 = "https://platform.lingyiwanwu.com/assets/LLMspeed.jpg"
# # image3 = "https://platform.lingyiwanwu.com/assets/LLMprice.jpg"
# # Approach 2: use image URL and encode it to base64
# # image_url = "https://platform.lingyiwanwu.com/assets/sample-table.jpg"
# # image_media_type = "image/jpeg"
# # image = "data:image/jpeg;base64," + base64.b64encode(httpx.get(image_url).content).decode("utf-8")
# # Approach 3: use local image and encode it to base64
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
