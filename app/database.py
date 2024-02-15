import streamlit as st
from supabase import Client, create_client


__version__ = "0.2.2"
@st.cache_resource
def init_connection() -> Client:
    try:
        return create_client(
            st.secrets["connections"]["supabase"]["SUPABASE_URL"],
            st.secrets["connections"]["supabase"]["SUPABASE_KEY"],
        )
    except KeyError:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def create_user(client, username, quota=2):

    new_user_data = {'username': username, 'quota': quota}  # Adjust as needed

    data_ex, _ = client.table("user_quota").select("username").eq('username', username).execute()

    print(data_ex)
    if len(data_ex[-1]) == 0:
        try:
            data_ins, _ = client.table("user_quota").insert(new_user_data).execute()
        except Exception as e:
            print(e)
        else:
            print('Successfully created')
    else:
        print("User already created")


def deduce_quota(client, username, cost=0.1):

    user_response, _ = client.table("user_quota").select('quota').eq('username', username).execute()
    # Check if the user exists
    if len(user_response[-1]) > 0:
        current_quota = user_response[-1][0]['quota']

        if current_quota < 0:
            print("Quota is used!")
            return

        # Update the quota value by subtracting the deduction
        new_quota = current_quota - cost
        print('new quoate is: ', new_quota)

        try:
            update_response, _ = client.table("user_quota").update({'quota': new_quota}).eq('username', username).execute()
        except Exception as e:
            print("Error updating quota for user:", username)

    else:
        print(f"User {username} not found.")


def extract_quota(clint, username):
    user_response, _ = client.table("user_quota").select('quota').eq('username', username).execute()
    if len(user_response[-1]) > 0:
        current_quota = user_response[-1][0]['quota']
        return current_quota
    else:
        print(f"User {username} not found.")

client = init_connection()
create_user(client, "akm22", quota=2)
deduce_quota(client, "akm2232", 0.1)

