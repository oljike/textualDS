import streamlit as st
st.set_page_config(page_title="TableGPT", page_icon="./app/frontend/app_images/icon.ico", layout="centered", initial_sidebar_state="auto", menu_items=None)

from PIL import Image
import matplotlib
matplotlib.use('agg')
import sys
import asyncio
from os.path import abspath, join, dirname
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)
from app.app_functions import process_uploaded_file, get_predefined_ds, load_predefined_ds, get_tasks, \
                                explore_function, print_welcome_page, handle_execution, set_bg_hack, display_app_header
from chatdev.flow import Flow
from app.app_functions import display_data
from app.auth_form import auth_button
from app.database import init_connection, extract_quota, create_user, deduce_quota
client = init_connection()

with open("app/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>', unsafe_allow_html=True)

async def main():

    set_bg_hack('./app/frontend/app_images/background.png')
    df = None
    with st.sidebar:

        st.sidebar.image('./app/frontend/app_images/logo.png', use_column_width=True)

        try:
            auth_output = await auth_button()
            print(auth_output)
        except Exception as e:
            st.error(f"Bad sign-in request. Please, refresh the page. Error: {e}")
            auth_output = None

        # auth_output = 'kek', 'Olzhas'
        if auth_output is not None:
            email, name = auth_output
            st.subheader("Hello " + name + "!")


            def clear_results():
                st.session_state.pop("explore_result", None)
                st.session_state.pop("predefined_tasks", None)
                st.session_state.pop("messages", None)
            # if st.button("New Chat"):
            #     clear_results()


            create_user(client, email, quota = 5)
            if 'current_quota' not in st.session_state:
                st.session_state.current_quota = extract_quota(client, email)
            st.info("Your current free credit is " + str(st.session_state.current_quota) + " requests.")
            if st.session_state.current_quota == 0:
                st.info("You are out of credits! We will add you to the waitlist.")
                st.stop()
            # st.info("Your current free credit is " + str(10) + " requests.")

            # st.write(st.session_state["auth"])
            # st.subheader("OpenAI Key")
            # openai_api_key = 'lolkek'
            # openai_api_key = st.text_input("Enter the OpenAI API key (optional)", openai_api_key, type="password")

            # Dataset selection
            # st.subheader("Dataset")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="display: flex; justify-content: left;">
                    <h3>Dataset</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            dataset_option = st.radio("Select one option", ["Upload Dataset", "Choose a toy dataset"])
            if dataset_option == "Upload Dataset":
                # clear_results()
                uploaded_file = st.file_uploader("Upload your dataset (if applicable)", type=["csv"], accept_multiple_files=False)

                if uploaded_file:
                    # st.sidebar.write("Filename: ", )
                    file_name = uploaded_file.name
                    st.session_state["file_name"] = file_name
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
                selected_dataset = st.selectbox("", predefined_datasets)
                st.subheader(f"Selected dataset: {selected_dataset}")
                st.session_state["file_name"] = selected_dataset
                df = load_predefined_ds(predefined_datasets, selected_dataset)
                predefined_tasks = get_tasks(selected_dataset)
                st.sidebar.subheader("Uploaded Data:")
                st.sidebar.write(df)
                st.success("Dataset uploaded successfully!")
                # flow = Flow(df, explore_result)

    if auth_output is None:
        print_welcome_page()

    if auth_output:

        st.subheader("")

        if df is not None:
            explore_result = explore_function(df)
            st.session_state["explore_result"] = explore_result
            st.session_state["predefined_tasks"] = predefined_tasks
            explore_button = st.button("Generate queries for me",
                                       help="We help you to come up with new analysis ideas")
            st.session_state["flow"] = Flow(df, st.session_state["explore_result"])
            if explore_button:
                if len(predefined_tasks) > 0:
                    st.markdown(
                        '<p style="font-size: 22px; color: #020F59; font-weight: 500;">Recommended queries: </p>',
                        unsafe_allow_html=True)
                    st.markdown("\n".join(
                        [f"- {item.strip('.').lower()}" for item in st.session_state["predefined_tasks"][:5]]))

                else:
                    import json
                    with st.spinner("Generating queries..."):
                        llm_metrics = await st.session_state["flow"].chatroom.explorer.astep("the columns are: " + f"{', '.join(df.columns)}")
                    llm_metrics = json.loads(llm_metrics)['list']
                    st.markdown(
                        '<p style="font-size: 22px; color: #020F59; font-weight: 500;">Recommended queries: </p>',
                        unsafe_allow_html=True)
                    st.markdown("\n".join(
                        [f"- {item.strip('.').lower()}" for item in llm_metrics]))
        else:
            st.warning("Please choose or upload a dataset before exploring.")

        if "explore_result" in st.session_state:
            if len(st.session_state["predefined_tasks"]) > 0:
                st.markdown(
                    '<p style="font-size: 22px; color: #020F59; font-weight: 500;">Recommended queries: </p>',
                    unsafe_allow_html=True)
                st.markdown("\n".join([f"- {item.strip('.').lower()}" for item in st.session_state["predefined_tasks"][:5]]))


        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])


        st.markdown("""
            <style> 
            .stChatInputContainer > div {
                background-color: #fff;
            }
            </style>
            """, unsafe_allow_html=True)


        if prompt := st.chat_input(placeholder="Type your message here..."):
            print(prompt)
            try:
                # if not openai_api_key:
                #     st.info("Please add your OpenAI API key to continue.")
                #     st.stop()

                st.session_state["messages"].append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                current_quota = extract_quota(client, email)
                if current_quota > 0:
                    with st.spinner("Analyst is thinking..."):
                        flow = st.session_state["flow"]
                        bot_response, dynamic_function, flow = await handle_execution(flow, prompt) #process_user_input(prompt, flow)
                        st.session_state["flow"] = flow
                else:
                    st.info("You are out of credits! We will add you to the waitlist.")
                    st.stop()

                new_quota = deduce_quota(client, email)
                st.session_state.current_quota = new_quota
                # if st.session_state.current_quota == 0:


                # save the history of bot responses and display in the chat.
                st.session_state["messages"].append({"role": "assistant", "content": bot_response})

                for task, task_response in bot_response.items():
                    st.chat_message("assistant").write(f"Task: {task}")
                    display_data(st, task_response["result"])
                    st.chat_message("assistant").write(f"Short summary: {task_response['analysis']}")

                st.session_state["messages"].append({"role": "assistant", "content": bot_response})

                # if st.button('Show code'):
                #     st.code(dynamic_function[0])

            except Exception as e:
                st.error(f"Failed to process the request: {str(e)}")

if __name__=="__main__":
    asyncio.run(main())