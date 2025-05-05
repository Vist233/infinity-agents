import subprocess
import os
import shutil
from PIL import Image
import base64
import io

def package_to_exe(code_str, file_name):
    # Write the code string to a .py file
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(code_str)
    
    # Use pyinstaller to package the .py file into an .exe
    subprocess.run(['pyinstaller', '--onefile', '--console', file_name])
    
    # Move the generated .exe file from ./dist to the current directory
    exe_file = os.path.splitext(file_name)[0] + '.exe'
    dist_path = os.path.join('dist', exe_file)
    if os.path.exists(dist_path):
        shutil.move(dist_path, exe_file)
    
    # Clean up build directories and files
    shutil.rmtree('build')
    shutil.rmtree('dist')
    spec_file = os.path.splitext(file_name)[0] + '.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
    if os.path.exists(file_name):
        os.remove(file_name)

def resize_image_to_1080p(image_path, output_path):
    with Image.open(image_path) as img:
            width, height = img.size
            if width > 1920 or height > 1080:
                img = img.resize((1920, 1080), Image.LANCZOS)
            img.save(output_path)

def resize_image_to_480p(image_path, output_path):
    with Image.open(image_path) as img:
            width, height = img.size
            if width > 640 or height > 480:
                img = img.resize((640, 480), Image.LANCZOS)
            img.save(output_path)
            
# def resize_image_to_480p_base64(image_path):
#     with Image.open(image_path) as img:
#         width, height = img.size
#         if width > 640 or height > 480:
#             img = img.resize((640, 480), Image.LANCZOS)
        
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG")
#         img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
#         return "data:image/jpeg;base64," + img_base64


def resize_image_to_480p_base64(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        if width > 854 or height > 480:
            img = img.resize((854, 480))  # Resize to 480p
        if img.mode == 'RGBA':
            img = img.convert('RGB')  # Convert RGBA to RGB
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return "data:image/jpeg;base64," + img_str
            

# Example usage
if __name__ == "__main__":
    code = """
print("Hello, World!")
    """
    package_to_exe(code, 'hello.py')
    # resize_image_to_1080p('input_image.jpg', 'output_image.jpg')