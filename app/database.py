import streamlit as st
from supabase import Client, create_client
import os

__version__ = "0.2.2"
@st.cache_resource
def init_connection() -> Client:
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    if SUPABASE_KEY is None or SUPABASE_URL is None:
        SUPABASE_URL = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]

    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except KeyError as e:
        print(e)
        print("Supabase cpnnection errot")


def create_user(client, username, quota=5):

    new_user_data = {'username': username, 'quota': quota}  # Adjust as needed

    data_ex, _ = client.table("user_quota").select("username").eq('username', username).execute()

    if len(data_ex[-1]) == 0:
        try:
            data_ins, _ = client.table("user_quota").insert(new_user_data).execute()
        except Exception as e:
            print(e)
        else:
            print('Successfully created')
    else:
        print("User already created")


def deduce_quota(client, username, cost=1):

    user_response, _ = client.table("user_quota").select('quota').eq('username', username).execute()
    # Check if the user exists
    if len(user_response[-1]) > 0:
        current_quota = user_response[-1][0]['quota']

        if current_quota <= 0:
            print("Quota is used!")
            return 0

        # Update the quota value by subtracting the deduction
        new_quota = current_quota - cost
        print('new quota is: ', new_quota)


        if new_quota == 0:

            update_response, _ = client.table("user_quota").update({'quota': new_quota}).eq('username', username).execute()
            return new_quota
        if new_quota < 0:
            return 0

        try:
            update_response, _ = client.table("user_quota").update({'quota': new_quota}).eq('username', username).execute()
        except Exception as e:
            print(e)
            print("Error updating quota for user:", username)

        return new_quota
    else:
        print(f"User {username} not found.")
        return 0


def extract_quota(client, username):
    user_response, _ = client.table("user_quota").select('quota').eq('username', username).execute()
    if len(user_response[-1]) > 0:
        current_quota = user_response[-1][0]['quota']
        return current_quota
    else:
        print(f"User {username} not found.")
        return 0

# client = init_connection()
# create_user(client, "akm22", quota=2)
# deduce_quota(client, "akm22", 1)