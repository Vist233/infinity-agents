import os
from openai import OpenAI
import base64
import httpx
import subprocess
import tempfile

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
import csv

API_BASE = "{API_BASE}"
API_KEY = "{API_KEY}"
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

input_image = "{input_image}"

with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename', 'result'])

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
                                "text": "请你根据第二张的图片所展示的植物某一性状的标准，判断第一张图片的该形状属于什么类型。并按照，第一段输出自己思考的详细内容，第二段只输出判断的结果来输出。"
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
            result = completion  # 根据实际情况提取需要的结果
            print(f"Result for {{filename}}: {{result}}")
            writer.writerow([filename, result])

"""

# Save process_images_code to temporary file
temp_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
with open(temp_file.name, 'w', encoding='utf-8') as f:
    f.write(process_images_code)

try:
    # Run pyinstaller
    subprocess.run(['pyinstaller', '--onefile', temp_file.name], check=True)
    print(f"Successfully created executable from {temp_file.name}")
    
    # Move executable from dist to current directory
    exe_name = os.path.splitext(os.path.basename(temp_file.name))[0] + '.exe'
    dist_exe_path = os.path.join('dist', exe_name)
    if os.path.exists(dist_exe_path):
        os.replace(dist_exe_path, exe_name)
        print(f"Moved executable to current directory: {exe_name}")
    
    # Clean up dist and build directories
    for cleanup_dir in ['dist', 'build']:
        if os.path.exists(cleanup_dir):
            for root, dirs, files in os.walk(cleanup_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(cleanup_dir)
            print(f"Cleaned up {cleanup_dir} directory")
            
    # Remove spec file
    spec_file = temp_file.name.replace('.py', '.spec')
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print("Cleaned up spec file")
        
except subprocess.CalledProcessError as e:
    print(f"Error during packaging: {e}")
except FileNotFoundError:
    print("pyinstaller not found. Please install it using 'pip install pyinstaller'")
finally:
    # Cleanup temporary file
    os.unlink(temp_file.name)
    print("Temporary file cleaned up")


