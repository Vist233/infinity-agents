import os
import base64
from openai import OpenAI
import csv
from PIL import Image
import io

API_BASE = "{API_BASE}"
API_KEY = "{API_KEY}"
Model = "{Model}"

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

def resize_image_to_480p_base64(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width > 854 or height > 480:
                ratio = min(854/width, 480/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return "data:image/jpeg;base64," + img_str
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return None

def extract_result(text):
    if '$' in text:
        start = text.find('$') + 1
        end = text.rfind('$')
        if start < end:
            return text[start:end]
    return text  

standard_image = resize_image_to_480p_base64("./Strandard.png")

with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename', 'result'])

    for filename in os.listdir('.'):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = resize_image_to_480p_base64(filename)
                if not image:
                    continue

                completion = client.chat.completions.create(
                    model=Model,  # Changed from "{Model}" to Model
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请你根据第一张图片中的判断标准，判断第二张图片所归属的类型。第一段输出描述，第二段输出判断结果并在判断结果的左右添加$符号。按照以下格式填写：$判断结果$"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": standard_image
                                    }
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image
                                    }
                                }
                            ]
                        }
                    ]
                )
                
                full_result = completion.choices[0].message.content
                result = extract_result(full_result)
                print(f"Result for {filename}: {result}")
                writer.writerow([filename, result])
            
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                writer.writerow([filename, f"Error: {str(e)}"])

input("Press Enter to exit...")