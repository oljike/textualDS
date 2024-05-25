import streamlit as st
st.set_page_config(page_title="TableGPT", page_icon="./app/frontend/app_images/icon.ico", layout="centered", initial_sidebar_state="auto", menu_items=None)

from PIL import Image
import matplotlib
import base64
matplotlib.use('agg')
import sys
import asyncio
from os.path import abspath, join, dirname
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)
from app.app_functions import process_uploaded_file, get_predefined_ds, load_predefined_ds, get_tasks, \
                                explore_function, print_welcome_page, handle_execution, set_bg_hack, display_app_header
from chatdev.flow import Flow
# from app.app_functions import display_data
from app.auth_form import auth_button
from app.database import init_connection, extract_quota, create_user, deduce_quota
client = init_connection()

with open("app/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>', unsafe_allow_html=True)

def nav_to(url):
    nav_script = """
        <meta http-equiv="refresh" content="0; url='%s'">
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)


@st.cache_data
def display_data(bot_response):

    for task, data in bot_response.items():
        print('data', data)
        # with st.chat_message("assistant"):
        #     st.markdown(f"Task: {task}")
    # add new llm here?

        # display plots
        if 'plots' in data['result'] and len(data['result']['plots']) > 0:
            for plot in data['result']['plots']:
                with st.chat_message("assistant"):
                    st.image(plot)

        with st.chat_message("assistant"):
            if 'analysisvis' in data:
                st.markdown(f"Interpretation of plots: {data['analysisvis']}")
            if 'analysis' in data:
                st.markdown(f"Short summary: {data['analysis']}")
            if 'offtopic' in data:
                st.markdown(data['offtopic'])


async def main():

    query_params = st.query_params
    user_email = query_params.get("email", [""])
    if user_email == "":
        nav_to("https://www.tablegpt.app")
    user_email = base64.b64decode(user_email).decode("utf-8")
    print(user_email)


    # Check if the user is logged in (email is present)
    if not user_email:
        # Redirect the user to lol.com
        nav_to("https://www.tablegpt.app")

    set_bg_hack('./app/frontend/app_images/background.jpg')
    with st.sidebar:

        st.sidebar.image('./app/frontend/app_images/logo.png', use_column_width=True)

        # auth_output = 'kek', 'Olzhas'
        if user_email is not None:
            email = user_email
            st.subheader("Hello!")

            def clear_results():
                st.session_state.pop("explore_result", None)
                st.session_state.pop("predefined_tasks", None)
                st.session_state.pop("messages", None)
            # if st.button("New Chat"):
            #     clear_results()


            create_user(client, email, quota=3)
            if 'current_quota' not in st.session_state:
                st.session_state.current_quota = extract_quota(client, email)

            # Generate the message with custom formatting
            # message = f"<span style='color: blue;'>Your current free credit is {st.session_state.current_quota} requests.</span>"

            # Display the message using st.markdown with st.info()
            # st.markdown(f'<div class="stInfo">{message}</div>', unsafe_allow_html=True)

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
                uploaded_file = st.file_uploader("Upload your dataset (if applicable)", type=["csv", "xlsx", "xls"], accept_multiple_files=False)

                if uploaded_file:
                    # st.sidebar.write("Filename: ", )
                    file_name = uploaded_file.name
                    df = process_uploaded_file(uploaded_file)

                    if 'df' not in st.session_state or file_name != st.session_state.file_name:
                        print("Initilising FLOW FUKIN AGAIN upload!")
                        st.session_state.df = df
                        st.session_state.file_name = file_name
                        explore_result = explore_function(df)
                        st.session_state["explore_result"] = explore_result
                        st.session_state["flow"] = Flow(df, st.session_state["explore_result"])
                    predefined_tasks = []
                    st.success("Dataset uploaded successfully!")


            elif dataset_option == "Choose a toy dataset":
                # clear_results()
                # st.session_state.pop("explore_result", None)
                predefined_datasets = get_predefined_ds()
                selected_dataset = st.selectbox("", predefined_datasets)
                st.subheader(f"Selected dataset: {selected_dataset}")
                df = load_predefined_ds(predefined_datasets, selected_dataset)

                if 'df' not in st.session_state or selected_dataset != st.session_state.file_name:

                    if 'df' in st.session_state:
                        print(df.shape, st.session_state.df.shape)

                    print("Initilising FLOW FUKIN AGAIN toy!!!!")
                    st.session_state.df = df
                    st.session_state.file_name = selected_dataset
                    print('df' in st.session_state)
                    explore_result = explore_function(df)
                    st.session_state["explore_result"] = explore_result
                    st.session_state["flow"] = Flow(df, st.session_state["explore_result"])

                predefined_tasks = get_tasks(selected_dataset)
                st.success("Dataset uploaded successfully!")
                # explore_result = explore_function(df)
                # st.session_state["explore_result"] = explore_result
                # st.session_state["flow"] = Flow(df, st.session_state["explore_result"]

        st.sidebar.markdown("<br>", unsafe_allow_html=True)

        # Add contact information with percentage-based positioning
        st.sidebar.markdown(
            """<footer style="position: fixed; bottom: 0; width: 15%; background-color: #f5f5f5; padding: 10px; text-align: left;">
               Contact Information:
               <br>
               olzhaskabdolov@gmail.com<br>
               </footer>""",
            unsafe_allow_html=True
        )

    if user_email:

        st.subheader("")

        if 'df' in st.session_state:

            df = st.session_state.df
            st.subheader('Data snapshot:')
            st.write(df.iloc[:100])

            st.session_state["predefined_tasks"] = predefined_tasks
            explore_button = st.button("Generate queries for me",
                                       help="We help you to come up with new analysis ideas")

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
            st.stop()


        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                if isinstance(message["content"], str):
                    with st.chat_message("assistant"):
                        st.markdown(message["content"])
                else:
                    display_data(message["content"])


        st.markdown("""
            <style> 
            .stChatInputContainer > div {
                color: #c82d2d;
            }
            </style>
            """, unsafe_allow_html=True)


        if prompt := st.chat_input(placeholder="Type your message here..."):

            # try:
            # if not openai_api_key:
            #     st.info("Please add your OpenAI API key to continue.")
            #     st.stop()

            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            current_quota = extract_quota(client, email)
            if current_quota > 0:

                # with st.chat_message(""):
                with st.spinner("Analyst is thinking..."):
                    flow = st.session_state["flow"]
                    bot_response, dynamic_function, flow = await handle_execution(flow, prompt) #process_user_input(prompt, flow)
                # bot_response = {'task': {'result':{'plots': ['./plots/AQI_O3.png']}, 'analysis': 'lol', 'analysisvis': 'kek'}}
                st.session_state["flow"] = flow
            else:
                st.info("You are out of credits! We will add you to the waitlist.")
                st.stop()

            new_quota = deduce_quota(client, email)
            st.session_state.current_quota = new_quota
            # if st.session_state.current_quota == 0:


            # save the history of bot responses and display in the chat.
            st.session_state["messages"].append({"role": "assistant", "content": bot_response})
            display_data(bot_response)

            # if st.button('Show code'):
            #     st.code(dynamic_function[0])

            # except Exception as e:
            #     st.error(f"Failed to process the request: {str(e)}")

if __name__=="__main__":
    asyncio.run(main())