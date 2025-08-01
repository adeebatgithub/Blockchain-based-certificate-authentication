import base64
import json
import os
from io import BytesIO

import requests
import streamlit as st
from PIL import Image
from connection import contract
from utils.pinata_utils import get_metadata_from_pinata

def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def view_certificate(certificate_id, user_email=None):
    # Smart Contract Call
    result = contract.functions.getCertificate(certificate_id).call()
    ipfs_hash = result[4]
    metadata = get_metadata_from_pinata(ipfs_hash)
    if user_email is not None and metadata and metadata.get("keyvalues", {}).get("user_email") != str(user_email):
        raise Exception("User email does not match")

    pinata_gateway_base_url = 'https://gateway.pinata.cloud/ipfs'
    content_url = f"{pinata_gateway_base_url}/{ipfs_hash}"
    response = requests.get(content_url)
    with open("temp.pdf", 'wb') as pdf_file:
        pdf_file.write(response.content)
    displayPDF("temp.pdf")
    os.remove("temp.pdf")


def hide_icons():
    hide_st_style = """
				<style>
				#MainMenu {visibility: hidden;}
				footer {visibility: hidden;}
				</style>"""
    st.markdown(hide_st_style, unsafe_allow_html=True)


def hide_sidebar():
    st.markdown("""
    <style>
        .st-emotion-cache-1jicfl2 {display: none !important;}
        section[data-testid="stSidebar"] {display: none !important;}
        .stSidebar {display: none !important;}
        button[kind="header"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)


def remove_whitespaces():
    st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>""", unsafe_allow_html=True)


def get_image_base64(img_path):
    img = Image.open(img_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def get_next_uid(file_path="last_uid.json", start_uid=1000):
    """Reads last UID from JSON file, increments it, saves new UID with timestamp."""
    if not os.path.exists(file_path):
        data = {
            "last_uid": start_uid,
            "created": False
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return str(start_uid)

    with open(file_path, "r") as f:
        data = json.load(f)

    new_uid = data["last_uid"] + 1 if data["created"] else data["last_uid"]
    data = {
        "last_uid": new_uid,
        "created": False
    }

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    return str(new_uid)


def uid_created(uid, file_path="last_uid.json"):
    """Marks the given UID as created by setting the flag to True in the JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError("UID file does not exist.")

    with open(file_path, "r") as f:
        data = json.load(f)

    if str(data["last_uid"]) != str(uid):
        raise ValueError(f"UID {uid} does not match the current UID ({data['last_uid']}).")

    data["created"] = True

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
