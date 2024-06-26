import pandas as pd
import chardet
import io
import yaml
import streamlit as st
import base64
import mimetypes
from PIL import Image
import numpy as np
from io import BytesIO

# @st.cache_data
# def display_data(st, data):
#
#     if isinstance(data, dict):
#         if len(data) < 10: # in case of its not a dataframe lets iterate over its elements and check its values
#             for key, value in data.items():
#                 st.chat_message("assistant").write(f"**{key}**:")
#                 display_data(st, value)
#         else:
#             st.chat_message("assistant").write(data)
#     elif isinstance(data, list):
#         for item in data:
#             display_data(st, item)
#     elif isinstance(data, str):
#         if 'png' in data:
#             st.chat_message("assistant").image(data)
#         else:
#             st.chat_message("assistant").text(data)
#     elif isinstance(data, bytes) or isinstance(data, Image.Image) or isinstance(data, np.ndarray) or isinstance(data, BytesIO):
#         st.chat_message("assistant").image(data)  # Assuming data is a byte representation of an image
#     else:
#         st.chat_message("assistant").write(data)  # Handle other data types





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
    #
    # file_content = uploaded_file.read()
    # # Detect the encoding
    # encoding = detect_encoding(file_content)
    # # Read the CSV file using the detected encoding
    # df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
    # return df

    file_content = uploaded_file.read()

    # Detect the file type using mimetypes
    file_type, _ = mimetypes.guess_type(uploaded_file.name)

    # Check if the file type is CSV
    if file_type and 'csv' in file_type:
        # Detect the encoding for CSV files
        encoding = detect_encoding(file_content)
        # Read the CSV file using the detected encoding
        df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
    else:
        # Assume Excel file format if not CSV
        # Read the Excel file using pandas
        df = pd.read_excel(io.BytesIO(file_content))

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

def print_welcome_page():
    # st.title('Welcome to TableGPT!', )

    font_size = "24px"
    st.markdown(
        '<p style="font-size: 30px; color: #020F59; font-weight: 600;font-weight: 700;">Data analysis made easy!</p>',
        unsafe_allow_html=True)

    # Horizontal line
    st.markdown('<hr style="border-top: 2px solid #000000;">', unsafe_allow_html=True)

    # Explanation of the app with customized font size and color
    st.markdown(
        '<p style="font-size: 24px; color: #020F59; font-weight: 600;">What is it?</p>',
        unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size: 20px; color: #020F59; font-weight: normal;">TableGPT allows You to perform data analysis using simple text questions. '
        'No coding. Upload your datasets and use plain English queries to gain valuable insights.</p>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size: 24px; color: #020F59; font-weight: 600;">For whom?</p>',
        unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size: 20px; color: #020F59; font-weight: normal;">Data analytics, product and project managers, marketing professionals, finance experts, business owners and anyone with an Excel file to analyse.</p>',
        unsafe_allow_html=True
    )

    # Horizontal line
    st.markdown('<hr style="border-top: 2px solid #000000;">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size: 24px; color: #020F59; font-weight: 600;">How to use it</p>',
        unsafe_allow_html=True)
    st.image("./app/frontend/app_images/demo.gif", caption='', use_column_width=True)

