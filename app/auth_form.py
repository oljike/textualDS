import streamlit as st
from app.streamlit_oauth import OAuth2Component
import os
import base64
import json
import asyncio

async def auth_button():

    CLIENT_ID = st.secrets["gauth"]["endpoints"]["GAUTH_ID"]
    CLIENT_SECRET = st.secrets["gauth"]["endpoints"]["GAUTH_SECRET"]
    AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"

    if "email" not in st.session_state:
        # create a button to start the OAuth2 flow
        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, TOKEN_ENDPOINT,
                                 REVOKE_ENDPOINT)
        result = await oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri="https://tablegpt-bupvssekaq-uc.a.run.app/",
            scope="openid email profile",
            key="google",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256',
        )

        if result:
            # st.write(result)
            # decode the id_token jwt and get the user's email address
            id_token = result["token"]["id_token"]
            # verify the signature is an optional step for security
            payload = id_token.split(".")[1]
            # add padding to the payload if needed
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            # st.write(payload)
            email = payload["email"]
            st.session_state["payload"] = payload
            st.session_state["email"] = email
            st.session_state["name"] = payload["name"]
            st.session_state["token"] = result["token"]
            st.rerun()
    else:
        # st.write("You are logged in!")
        # st.write(st.session_state["payload"])
        # del st.session_state["auth"]
        # del st.session_state["token"]
        return st.session_state["email"], st.session_state["name"]


