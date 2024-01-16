import pandas as pd
import os
import subprocess
from tqdm import tqdm

data = pd.read_csv('kaggle_hidden_gems.csv')

for x in tqdm(data['notebook']):

    kaggle_p = x.replace('https://www.kaggle.com/', '')
    # output = os.system(f'kaggle kernels pull {kaggle_p} -p ../../tests/kaggle')
    print(kaggle_p)
    try:
        output = subprocess.check_output(f'kaggle kernels pull {kaggle_p} -p ../../tests/kaggle', shell=True)
    except:
        print('error encountered')
        continue
    text_string = output.decode('utf-8')

    if 'Rmd' in text_string:

        # Convert bytes to string
        # text_string = output.decode('utf-8')
        # Extract path from the string
        start_index = text_string.find('../../')  # Find the start of the path
        end_index = text_string.find('.Rmd') + 4  # Find the end of the path (including '.Rmd')
        path = text_string[start_index:end_index]

        # Display the extracted path
        print("Removing: ", path)
        os.system('rm ' + path)
