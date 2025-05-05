from flask import Flask, request, send_file, render_template, jsonify
import os
from openai import OpenAI
try:
    from autoGenerateApp import packageFunc
except ImportError:
    import packageFunc

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FILE = "spade.exe"   # spade n.铲子
# 配置固定程序目录
FIXED_PROG_DIR = os.path.abspath("../fixedQuantityProg")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API配置
API_KEY = "sk-e82df05b5c9443cab084419078b31c32"
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
Model = "qwen2.5-vl-72b-instruct"

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    # 清理旧文件
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
        except Exception as e:
            return f"删除旧文件失败: {str(e)}", 500

    # 处理上传文件
    if "file" not in request.files:
        return "请选择文件", 400
    file = request.files["file"]
    if file.filename == "":
        return "无效的文件名", 400

    # 保存上传文件
    input_image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_image_path)

    try:
        # 处理图片并生成EXE
        with open(input_image_path, "rb") as input_image_file:
            standard_image = packageFunc.resize_image_to_480p_base64(input_image_file)

        # Generate process_images.py
        process_images_code = f"""
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
        print(f"Error when processing image.")
        return None

def extract_result(text):
    try:
        text = text.encode('utf-8').decode('utf-8')
        if '$' in text:
            start = text.find('$') + 1
            end = text.rfind('$')
            if start < end:
                return text[start:end]
    except Exception as e:
        print(f"Error extracting result")
    return "None"  

def process_image(client, model, standard_image, image):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {{
                    "role": "user",
                    "content": [
                        {{
                            "type": "text",
                            "text": "请你根据第一张图片中的判断标准，判断第二张图片所归属的类型。第一段输出描述，第二段输出判断结果并在判断结果的左右添加$符号。按照以下格式填写：$判断结果$"
                        }},
                        {{
                            "type": "image_url",
                            "image_url": {{
                                "url": standard_image
                            }}
                        }},
                        {{
                            "type": "image_url",
                            "image_url": {{
                                "url": image
                            }}
                        }}
                    ]
                }}
            ]
        )

        full_result = completion.choices[0].message.content
        result = extract_result(full_result)
        return result
    except Exception as e:
        print(f"Error when processing image")
        return "Error"

standard_image = "{standard_image}"

with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename', 'result']) 

    for filename in os.listdir('.'):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = resize_image_to_480p_base64(filename)
                if not image:
                    continue

                result = process_image(client, Model, standard_image, image)
                print(f"One image has been processed.")
                writer.writerow([filename, result])

            except Exception as e:
                print(f"Error when processing")
                writer.writerow([filename, f"Error"])

input("Press Enter to exit...")
        """
        packageFunc.package_to_exe(process_images_code, 'spade.py')

        # 验证生成结果
        if not os.path.exists(OUTPUT_FILE):
            return "生成exe失败", 500

        return send_file(OUTPUT_FILE, as_attachment=True)
    except Exception as e:
        return f"处理过程中发生错误: {str(e)}", 500

@app.route('/get_fixed_programs')
def get_fixed_programs():
    try:
        # 获取目录中所有.exe文件（按修改时间倒序）
        programs = sorted(
            [f for f in os.listdir(FIXED_PROG_DIR) if f.endswith('.exe')],
            key=lambda x: os.path.getmtime(os.path.join(FIXED_PROG_DIR, x)),
            reverse=True
        )
        return jsonify({
            "success": True,
            "programs": programs
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/download_fixed/<filename>')
def download_fixed(filename):
    # 安全验证文件名
    if not filename.endswith('.exe'):
        return "无效文件类型", 400
    file_path = os.path.join(FIXED_PROG_DIR, filename)
    if not os.path.exists(file_path):
        return "文件不存在", 404
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)