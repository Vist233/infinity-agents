import requests
import base64

# 设置您的API密钥
api_key = 'sk-KwXB98bGnjCFyohs9841D7084aC040C4B43d307dDdA42d54'

# 图片文件路径
image_path1 = "./Strandard.png"
image_path2 = "./22A-T-34-5球形侧视图.JPG"
image_path3 = "./22A-T-34-2球形侧视图.JPG"

# 读取并编码图片文件
with open(image_path1, "rb") as image_file1:
    image1 = base64.b64encode(image_file1.read()).decode('utf-8')
with open(image_path2, "rb") as image_file2:
    image2 = base64.b64encode(image_file2.read()).decode('utf-8')
with open(image_path3, "rb") as image_file3:
    image3 = base64.b64encode(image_file3.read()).decode('utf-8')

# API 端点
url = 'https://free.v36.cm/v1/'  # 根据实际 API 端点修改

# 提示词
prompt = '请你根据第一张的图片抱合类型标准，判断第二张、第三张图片的抱合类型。并按照"[<第一张图片的抱合类型>,<第二张图片的抱合类型>]"输出'

# 请求数据
data = {
    'model': 'gpt4o',
    'prompt': prompt,
    'images': [image1, image2, image3],
    'max_tokens': 150,
    'temperature': 0.7
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data)

# 检查响应状态和内容
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")

# 尝试解析 JSON 响应
if response.status_code == 200:
    try:
        json_response = response.json()
        print(json_response)
    except ValueError:
        print("响应内容不是有效的 JSON 格式。")
else:
    print("请求失败。")