import streamlit as st
import pandas as pd

import sys
from os.path import abspath, join, dirname

# Add the parent directory (APP) to the Python path
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)
from chatdev.flow import Flow
from chatdev.explorer import Explorer
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

        explorer = Explorer(df)
        init_desc = explorer.init_desc()
        flow = Flow(df, init_desc)

        # Display the uploaded data
        st.sidebar.subheader("Uploaded Data:")
        st.sidebar.write(df)

        # Chatbot section
        st.header("Analyst chat")

        # Ask the user for input
        user_input = st.text_input("What can I do for you?")

        # Process user input and get the response
        if user_input:
            bot_response = process_user_input(user_input, flow)

            # Display the bot's response
            st.write("Bot:", bot_response)

            # If the response is an image, display it
            if isinstance(bot_response, str) and bot_response.startswith("image:"):
                image_path = bot_response.split(":", 1)[1]
                st.image(image_path, caption="Bot's Response", use_column_width=True)

# Function to process the uploaded CSV file
def process_uploaded_file(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df

# Function to process user input using the engine
def process_user_input(user_input, flow):
    # Replace 'engine.process_query' with the actual function or method that processes user queries
    # The engine should return the response, and it may include images if needed
    # return engine.process_query(user_input)
    return flow.flow(user_input)


# Run the Streamlit app
if __name__ == "__main__":
    main()
