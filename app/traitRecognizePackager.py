import os
from openai import OpenAI
import base64
import json
import csv


DASHSCOPE_API_KEY = input("Please enter your DASHSCOPE_API_KEY: (OR press Enter to use environment variable)") or os.environ.get("DASHSCOPE_API_KEY", "")
trait_image_url = f"data:image/jpeg;base64,aaaaa"  # Replace with your actual base64 string
WORKSPACE = input("Please enter your image directory (default is current directory): ") or "./"
WORKSPACE = os.path.abspath(WORKSPACE)

def judge_image_type(trait_image_url):
    lower_url = trait_image_url.lower()
    if(lower_url.endswith((".jpg", ".jpeg", ".jpe"))):
        return "jpeg"
    elif(lower_url.endswith(".png")):
        return "png"
    elif(lower_url.endswith(".bmp")):
        return "bmp"
    elif(lower_url.endswith(".webp")):
        return "webp"
    elif(lower_url.endswith(".heic")):
        return "heic"
    elif(lower_url.endswith((".tif", ".tiff"))):
        return "tiff"
    else:
        return ""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_image_url(image_path):
    image_base64 = encode_image(image_path)
    image_type = judge_image_type(image_path)
    if(image_type == ""):
        raise ValueError("Unsupported image type")
    return f"data:image/{image_type};base64,{image_base64}"

def getClassify(trait_image_url, case_image_url):
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
    result = json.loads(completion.choices[0].message.content)
    return result.get("class", ""), result.get("reason", "")



client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 创建CSV文件并写入表头
csv_filename = "image_classification_results.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['filename', 'class', 'reason']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for root, dirs, files in os.walk(WORKSPACE):
        for filename in files:
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tif", ".tiff")):
                image_url = get_image_url(os.path.join(root, filename))
                
                try:
                    class_result, reason = getClassify(trait_image_url, image_url)
                    
                    writer.writerow({
                        'filename': filename,
                        'class': class_result,
                        'reason': reason
                    })
                    
                    print(f"Processed: {filename} -> Class: {class_result}")
                    
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    writer.writerow({
                        'filename': filename,
                        'class': 'ERROR',
                        'reason': str(e)
                    })

print(f"Results saved to {csv_filename}")

if __name__ == "__main__":
    pass

