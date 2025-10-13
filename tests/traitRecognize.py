import os
from openai import OpenAI
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

trait_image_base64 = encode_image("./app/trait.jpg")
case_image_base64 = encode_image("./app/case.png")

trait_image_url = f"data:image/jpeg;base64,{trait_image_base64}"
case_image_url = f"data:image/png;base64,{case_image_base64}"

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


completion = client.chat.completions.create(
    model="qwen3-vl-plus",
    messages=[
        {
            "role": "system",
            "content": "请你按照{}的格式返回结果".format(
                {"reason": "string", "class": "string"}
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": trait_image_url}},
                {"type": "image_url", "image_url": {"url": case_image_url}},
                {"type": "text", "text": "请你根据第一张图片的分类信息，得到第二张图片属于哪一个类并说明理由。"},
            ],
        }
    ],
    response_format={"type": "json_object"}
)

print(completion.choices[0].message.content)

