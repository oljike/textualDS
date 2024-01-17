import pandas as pd

import pandas as pd
import chardet

# Replace 'your_file.csv' with the actual file path
with open('../datasets/dataanalytics/Instagram data.csv', 'rb') as f:
    encoding = chardet.detect(f.read())['encoding']

df = pd.read_csv('../datasets/dataanalytics/Instagram data.csv', encoding=encoding)
