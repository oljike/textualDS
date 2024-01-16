import nbformat
import glob
import re
import os
import json


def remove_blank_lines_regex(input_string):
    return re.sub(r'\n\s*\n', '\n', input_string)


def remove_image_markdown(input_string):
    # Define the pattern for the image markdown ![image](some_url)
    pattern = re.compile(r'!\[image\]\([^)]*\)')

    # Use sub to replace all occurrences with an empty string
    result = re.sub(pattern, '', input_string)

    return result

def remove_enclosed_chars(input_string):
    # Define a regular expression pattern to match content inside angle brackets
    pattern = r'<.*?>'

    # Use re.sub to replace all matches with an empty string
    result_string = re.sub(pattern, '', input_string)

    return result_string



if __name__=="__main__":
    # Specify the path to your .ipynb file

    files = glob.glob('../../data/kaggle/*ipynb')
    all_mds = {}
    for fen, file_path in enumerate(files):
        # file_path = files[1]
        print(fen, file_path)
        # Load the notebook
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)

        # Access the cells in the notebook
        cells = notebook_content['cells']

        md_en = 0
        mds = []
        for cell in cells:

            code_source = cell['source']
            # code_source = remove_blank_lines_regex(code_source)
            if cell['cell_type'] == 'markdown':
                code_source = remove_image_markdown(code_source)
                code_source = remove_enclosed_chars(code_source)
                code_source = remove_blank_lines_regex(code_source)
                mds.append(code_source)
                md_en += 1


        all_mds[os.path.basename(file_path).replace('.ipynb', '')] = mds
    # all_mds.append('\n'.join(mds))

    with open('../../data/kaggle_meta/all_task_raw.json', 'w') as f:
        json.dump(all_mds, f)
