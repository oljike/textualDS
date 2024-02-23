import pandas as pd
import chardet
import io
import yaml
import streamlit as st
import base64
from PIL import Image
import numpy as np

def display_data(st, data):

    if isinstance(data, dict):
        if len(data) < 10: # in case of its not a dataframe lets iterate over its elements and check its values
            for key, value in data.items():
                st.chat_message("assistant").write(f"**{key}**:")
                display_data(st, value)
        else:
            st.chat_message("assistant").write(data)
    elif isinstance(data, list):
        for item in data:
            display_data(st, item)
    elif isinstance(data, str):
        if 'png' in data:
            st.chat_message("assistant").image(data)
        else:
            st.chat_message("assistant").text(data)
    elif isinstance(data, bytes) or isinstance(data, Image.Image) or isinstance(data, np.ndarray) or isinstance(data, BytesIO):
        st.chat_message("assistant").image(data)  # Assuming data is a byte representation of an image
    else:
        st.chat_message("assistant").write(data)  # Handle other data types


def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
    The bg will be static and won't take resolution of device into account.
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"

    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

async def handle_execution(flow, prompt):

    # Call the async flow method
    bot_response, dynamic_function = await flow.flow(prompt)
    # Store the flow object in session state
    return bot_response, dynamic_function, flow


def process_user_input(user_input, flow):
    # this function is done seperately in case of future modification
    return flow.flow(user_input)

def get_predefined_ds():

    with open('data/dataanalytics/val.yaml','r') as file:
        ds_meta = yaml.load(file, Loader=yaml.FullLoader)

    datasets = {}
    for ds, v in ds_meta.items():
        path = 'data/dataanalytics/' + v['path']
        datasets[ds] = path

    return datasets


def get_tasks(ds):

    with open('data/dataanalytics/val.yaml','r') as file:
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


def display_app_header(main_txt, sub_txt, is_sidebar=False):
    """
    function to display major headers at user interface
    ----------
    main_txt: str -> the major text to be displayed
    sub_txt: str -> the minor text to be displayed
    is_sidebar: bool -> check if its side panel or major panel
    """

    html_temp = f"""
    <h2 style = "color:#FF7F50; text_align:center; font-weight: bold;"> {main_txt} </h2>
    <p style = "color:#BB1D3F; text_align:center;"> {sub_txt} </p>
    </div>
    """
    if is_sidebar:
        st.sidebar.markdown(html_temp, unsafe_allow_html = True)
    else:
        st.markdown(html_temp, unsafe_allow_html = True)
