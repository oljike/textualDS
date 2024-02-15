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
                                explore_function, process_user_input, handle_execution, set_bg_hack, display_app_header
from chatdev.flow import Flow
from app.database import init_connection, create_user, deduce_quota, extract_quota
from memory_profiler import profile

# @profile
async def main():
    set_bg_hack('dqw_background.png')
    df = None
    # Sidebar
    with st.sidebar:

        st.sidebar.image('logo3.png', use_column_width=True)
        # st.sidebar.title("Textual data analysis app")
        # display_app_header("Textual data analysis app", '', True)

        st.sidebar.markdown(
            """
            <div style="display: flex; justify-content: center;">
                <h2 style="color: #FF5733; font-size: 24px;">Textual data analysis app</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        from app.auth_form import auth_button
        auth_output = await auth_button()
        # auth_output = 'kek', 'Olzhas'
        if auth_output is not None:
            email, name = auth_output
            # st.subheader("Welcome " + name + "!")
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <h3>Welcome {name}!</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Function to toggle documentation visibility
            with st.expander("Documentation"):
                st.markdown(
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
            # if st.button("New Chat"):
            #     clear_results()

            # client = init_connection()
            # create_user(client, email, quota=2)
            # if 'current_quota' not in st.session_state:
            #     st.session_state.current_quota = extract_quota(client, email)
            # st.info("Your current free credit is $" + str(round(st.session_state.current_quota, 2)))
            st.info("Your current free credit is $" + str(2))

            # st.write(st.session_state["auth"])
            # st.subheader("OpenAI Key")
            openai_api_key = 'lolkek'
            openai_api_key = st.text_input("Enter the OpenAI API key (optional)", openai_api_key, type="password")

            # Dataset selection
            # st.subheader("Dataset")
            st.markdown(
                """
                <div style="display: flex; justify-content: center;">
                    <h3>Dataset</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
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
    if auth_output:




        # st.title(":orange[**Data Exploration**]")
        st.title(":blue[**Data Exploration**]")
        # st.info("Press the 'Explore' button to enable chat.")
        explore_button = st.button("Start chat", help="The Explore button perform initial exploration the data")

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
            st.title(":blue[**Ask you question**]")
            if "messages" not in st.session_state:
                st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

            for msg in st.session_state["messages"]:
                st.chat_message(msg["role"]).write(msg["content"])
            if prompt := st.chat_input():
                # if not openai_api_key:
                #     st.info("Please add your OpenAI API key to continue.")
                #     st.stop()

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
                    bot_response, dynamic_function, flow = await handle_execution(flow, prompt) #process_user_input(prompt, flow)
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

                if st.button('Show code'):
                    st.code(dynamic_function)

if __name__=="__main__":
    asyncio.run(main())