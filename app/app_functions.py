import pandas as pd
import chardet
import io
import yaml

async def handle_execution(flow, prompt):

    # Call the async flow method
    bot_response = await flow.flow(prompt)
    # Store the flow object in session state
    return bot_response, flow


def process_user_input(user_input, flow):
    # this function is done seperately in case of future modification
    return flow.flow(user_input)

def get_predefined_ds():

    with open('datasets/dataanalytics/val.yaml','r') as file:
        ds_meta = yaml.load(file, Loader=yaml.FullLoader)

    datasets = {}
    for ds, v in ds_meta.items():
        path = 'datasets/dataanalytics/' + v['path']
        datasets[ds] = path

    return datasets


def get_tasks(ds):

    with open('datasets/dataanalytics/val.yaml','r') as file:
        ds_meta = yaml.load(file, Loader=yaml.FullLoader)

    questions = ds_meta[ds]['questions']

    output = []
    for k, v in questions.items():
        output.append(v)

    return output


def load_predefined_ds(predefined_datasets, selected_option):
    path = predefined_datasets[selected_option]
    df = pd.read_csv(path)
    return df


# Function to process the uploaded CSV file
def detect_encoding(file_content):
    result = chardet.detect(file_content)
    return result['encoding']


def process_uploaded_file(uploaded_file):
    file_content = uploaded_file.read()
    # Detect the encoding
    encoding = detect_encoding(file_content)
    # Read the CSV file using the detected encoding
    df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
    return df


def explore_function(dataset):
    # Replace this with your explore function logic using the selected dataset
    return f"{', '.join(dataset.columns)}"
