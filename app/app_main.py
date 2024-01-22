import streamlit as st
import pandas as pd
from PIL import Image
import sys
import io
import chardet
from os.path import abspath, join, dirname

# Add the parent directory (APP) to the Python path
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)
from chatdev.flow import Flow
from chatdev.explorer import Explorer
from chatdev.database import get_desc_from_db, save_to_db, get_file_hash
# import engine  # Replace 'engine' with the actual module or function that processes user queries

# Streamlit app logic
def main():
    # Set the title of the app
    st.title("Personal business data analyst")

    # File upload section
    st.sidebar.header("File upload")
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])


    # Check if a file is uploaded
    if uploaded_file is not None:
        # Process the uploaded file
        df = process_uploaded_file(uploaded_file)

        with st.spinner("Making initial data exploration..."):

            # hash_ = get_file_hash(uploaded_file.read())
            # db_desc = get_desc_from_db(hash_)
            # if db_desc:
            #     init_desc = db_desc
            # else:
            #     explorer = Explorer(df)
            #     init_desc = explorer.init_desc()
            #     save_to_db(hash_, init_desc)
            explorer = Explorer(df)
            init_desc = explorer.init_desc()

        # Display the uploaded data
        st.sidebar.subheader("Uploaded Data:")
        st.sidebar.write(df)

        # Chatbot section
        st.header("Analyst chat")

        # Ask the user for input
        user_input = st.text_input("What can I do for you?")

        # Process user input and get the response
        if user_input:

            flow = Flow(df, user_input, init_desc)
            # bot_response = Image.open('figure.png')

            # Convert PIL image to NumPy array
            # bot_response = np.array(pil_image)
            bot_response = process_user_input(user_input, flow)

            # Display the bot's response
            if isinstance(bot_response, Image.Image):
                st.image(bot_response)
            elif isinstance(bot_response, dict):
                for k, v in bot_response:
                    if isinstance(v, Image.Image):
                        st.write(k)
                        st.image(v)
                        bot_response.pop(k, None)
                st.json(bot_response)
            else:
                st.write(bot_response)


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



# Function to process user input using the engine
def process_user_input(user_input, flow):
    # this function is done seperately in case of future modification
    return flow.flow(user_input)


# Run the Streamlit app
if __name__ == "__main__":
    main()
