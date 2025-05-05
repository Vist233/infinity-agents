import subprocess
import os
import shutil
from PIL import Image
import base64
import io

def package_to_exe(code_str, file_name, output_exe_name):
    """Packages a Python code string into a standalone executable."""
    py_file_path = file_name + '.py'
    exe_file_path = output_exe_name + '.exe'
    spec_file_path = output_exe_name + '.spec'

    # Write the code string to a .py file
    with open(py_file_path, 'w', encoding='utf-8') as file:
        file.write(code_str)

    # Use pyinstaller to package the .py file into an .exe
    # --noconsole can be added if no console window is needed
    subprocess.run(['pyinstaller', '--onefile', '--console', '--name', output_exe_name, py_file_path], check=True)

    # Move the generated .exe file from ./dist to the current directory
    dist_path = os.path.join('dist', exe_file_path)
    if os.path.exists(dist_path):
        # Ensure the target directory exists (optional, depending on where you want the exe)
        # os.makedirs(os.path.dirname(exe_file_path), exist_ok=True) # Use if exe_file_path includes a directory
        shutil.move(dist_path, exe_file_path)
        print(f"Successfully created and moved {exe_file_path}")
    else:
        print(f"Error: Expected executable not found at {dist_path}")
        raise FileNotFoundError(f"PyInstaller did not create the expected file: {dist_path}")


    # Clean up build directories and files
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists(spec_file_path):
        os.remove(spec_file_path)
    if os.path.exists(py_file_path):
        os.remove(py_file_path)

    return exe_file_path # Return the final path of the exe

def resize_image_to_480p_base64(image_path_or_stream):
    """Resizes an image to fit within 854x480 and returns base64 string."""
    try:
        with Image.open(image_path_or_stream) as img:
            width, height = img.size
            if width > 854 or height > 480:
                # Calculate the aspect ratio and resize to fit within 854x480
                ratio = min(854.0 / width, 480.0 / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                # Use LANCZOS for better quality resizing
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if img.mode == 'RGBA':
                # Convert RGBA to RGB for JPEG compatibility
                img = img.convert('RGB')

            buffered = io.BytesIO()
            img.save(buffered, format="JPEG") # Save as JPEG
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return "data:image/jpeg;base64," + img_str
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

# Example usage (optional, for testing)
if __name__ == "__main__":
    code = """
import sys
print("Hello from packaged app!")
input("Press Enter to exit...") # Keep console open
"""
    try:
        exe_path = package_to_exe(code, 'temp_hello', 'hello_world_app')
        print(f"Executable created at: {exe_path}")
    except Exception as e:
        print(f"Failed to package: {e}")

    # Example for image resizing (requires a test image named 'test.jpg')
    # if os.path.exists('test.jpg'):
    #     base64_img = resize_image_to_480p_base64('test.jpg')
    #     if base64_img:
    #         print("Image resized and converted to base64.")
    #         # print(base64_img[:100] + "...") # Print start of base64 string
    #     else:
    #         print("Failed to resize image.")
    # else:
    #     print("Test image 'test.jpg' not found.")
