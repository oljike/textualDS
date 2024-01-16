import nbformat
import os
import glob

# Specify the path to your .ipynb file
# file_path = '../../tests/kaggle/winning-solutions-of-kaggle-competitions.ipynb'
files = glob.glob('../../data/kaggle/*ipynb')

file_path = files[1]
print(file_path)
# Load the notebook
with open(file_path, 'r', encoding='utf-8') as f:
    notebook_content = nbformat.read(f, as_version=4)

# Access the cells in the notebook
cells = notebook_content['cells']
# print(notebook_content['cells'])
# Iterate through the cells and print the content of code cells

import re

def remove_blank_lines_regex(input_string):
    return re.sub(r'\n\s*\n', '\n', input_string)

def remove_image_markdown(input_string):
    # Define the pattern for the image markdown ![image](some_url)
    pattern = re.compile(r'!\[image\]\([^)]*\)')

    # Use sub to replace all occurrences with an empty string
    result = re.sub(pattern, '', input_string)

    return result

for cell in cells:

    code_source = cell['source']
    code_source = remove_blank_lines_regex(code_source)
    if cell['cell_type'] == 'markdown':
        code_source = remove_image_markdown(code_source)

    print(f"Code Cell Content:\n{code_source}\n---\n")