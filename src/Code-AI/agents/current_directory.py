import os
import sys

# Get the current directory
current_dir = os.getcwd()

# Open a text file in the current directory for writing
with open(os.path.join(current_dir, 'current_directory.txt'), 'w') as file:
    file.write(current_dir)

variable_to_return = 'File saved successfully.'
variable_to_return