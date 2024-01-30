import streamlit as st
from PIL import Image
import matplotlib
matplotlib.use('agg')
import sys
import asyncio
from os.path import abspath, join, dirname
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)
from app.app_functions import process_uploaded_file, get_predefined_ds, load_predefined_ds, get_tasks, \
                                explore_function, process_user_input, handle_execution
from chatdev.flow import Flow


def main():

    df = None
    # Sidebar
    with st.sidebar:

        # Initialize session state variable for documentation visibility
        if "show_documentation" not in st.session_state:
            st.session_state["show_documentation"] = False  # Set to False initially

        # Sidebar content
        st.sidebar.title("Welcome to Data Exploration and Chatbot")

        # Function to toggle documentation visibility
        def toggle_documentation():
            st.session_state["show_documentation"] = not st.session_state.get("show_documentation", True)

        # Button to toggle documentation visibility
        if st.sidebar.button("Documentation: Please, Press to see"):
            toggle_documentation()

        # Show documentation if visibility is enabled
        if st.session_state.get("show_documentation", False):  # Check if it's True, not None
            st.sidebar.markdown(
                """
                This application allows you to explore datasets and interact with a chatbot for analysis tasks. Follow the steps below:
        
                **1. OpenAI API Key:**
                Enter your OpenAI API Key in the text box provided.
        
                **2. Dataset Selection:**
                Choose either to upload your own dataset or select from predefined datasets.
        
                **3. Explore:**
                Click the "Explore" button to analyze the dataset. You'll see potential analysis tasks and insights.
        
                **4. Chat with Buddy Analyst:**
                After exploration, you can chat with the chatbot to ask questions or get further analysis.
        
                **Note:**
                - Make sure to upload or select a dataset before exploring.
                - If you have any questions, feel free to ask @oljike in Telegram!
        
                """
            )

        def clear_results():
            st.session_state.pop("explore_result", None)
            st.session_state.pop("predefined_tasks", None)
            st.session_state.pop("messages", None)

        if st.button("Clear Chat"):
            clear_results()

        st.subheader("OpenAI Key")
        openai_api_key = 'lolkek'
        openai_api_key = st.text_input("Enter the key", openai_api_key, type="password")

        # Dataset selection
        st.subheader("Dataset")
        dataset_option = st.radio("Select Dataset Option", ["Upload Dataset", "Choose from Predefined Datasets"])
        if dataset_option == "Upload Dataset":
            clear_results()
            uploaded_file = st.file_uploader("Upload your dataset (if applicable)", type=["csv", "txt"])
            if uploaded_file:
                df = process_uploaded_file(uploaded_file)
                predefined_tasks = []
                st.sidebar.subheader("Uploaded Data:")
                st.sidebar.write(df)
                st.success("Dataset uploaded successfully!")
                # flow = Flow(df, explore_result)

        else:
            # clear_results()
            # st.session_state.pop("explore_result", None)
            predefined_datasets = get_predefined_ds()
            selected_dataset = st.selectbox("Choose a predefined dataset", predefined_datasets)
            st.subheader(f"Selected dataset: {selected_dataset}")
            df = load_predefined_ds(predefined_datasets, selected_dataset)
            predefined_tasks = get_tasks(selected_dataset)
            st.sidebar.subheader("Uploaded Data:")
            st.sidebar.write(df)
            st.success("Dataset uploaded successfully!")
            # flow = Flow(df, explore_result)

    # Button to explore
    # user_pressed_explore_button = False
        # Create a button to clear the chat

    st.title("Data Exploration and Chatbot")
    st.info("Press the 'Explore' button to enable chat.")
    explore_button = st.button("Explore")

    # Execute explore function when button is pressed
    if explore_button:
        # user_pressed_explore_button = True
        if df is not None:
            explore_result = explore_function(df)
            st.session_state["explore_result"] = explore_result
            st.session_state["predefined_tasks"] = predefined_tasks
            st.session_state["flow"] = Flow(df, explore_result)
        else:
            st.warning("Please choose or upload a dataset before exploring.")

    if "explore_result" in st.session_state:
        if len(st.session_state["predefined_tasks"]) > 0:
            st.markdown("### Analysis Tasks: ".format())
            st.markdown("\n".join([f"- {item.strip('.').lower()}" for item in st.session_state["predefined_tasks"][:5]]))

    # Disable chat if Explore button is not pressed
    if "explore_result" in st.session_state:
        st.title("Chat with buddy analyst")
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])
        if prompt := st.chat_input():
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()

            # explore_result = st.session_state.get("explore_result", "")
            st.session_state["messages"].append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            # bot_response = [Image.open('./figure.png'),Image.open('./figure.png')] #{'a': 'b', 'img': Image.open('./figure.png')}#process_user_input(prompt, flow)
            with st.spinner("Analyst is thinking..."):
                stop_execution = st.button("Stop Execution", key="stop_execution_button")
                if stop_execution:
                    st.warning("Execution stopped by user.")
                    st.stop()

                flow = st.session_state["flow"]
                bot_response, flow = asyncio.run(handle_execution(flow, prompt)) #process_user_input(prompt, flow)
                st.session_state["flow"] = flow

            # save the history of bot responses and display in the chat.
            st.session_state["messages"].append({"role": "assistant", "content": bot_response})
            # st.chat_message("assistant").write(bot_response)

            if isinstance(bot_response, Image.Image):
                st.chat_message("assistant").image(bot_response, caption="Generated Plot", use_column_width=True)
            elif isinstance(bot_response, list):
                for v in bot_response:
                    if isinstance(v, Image.Image):
                        st.chat_message("assistant").image(v)
                    else:
                        st.chat_message("assistant").write(v)
            elif isinstance(bot_response, dict):
                # Iterate through key-value pairs and display each value
                imgs_to_remove = []
                for k, v in bot_response.items():
                    if isinstance(v, Image.Image):
                        st.chat_message("assistant").write(k)
                        st.chat_message("assistant").image(v)
                        imgs_to_remove.append(k)

                for k in imgs_to_remove:
                    del bot_response[k]

                st.chat_message("assistant").json(bot_response)
            else:
                st.chat_message("assistant").write(bot_response)

            st.session_state["messages"].append({"role": "assistant", "content": bot_response})


if __name__=="__main__":
    main()