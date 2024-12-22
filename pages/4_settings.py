import streamlit as st
import pandas as pd
import ssl
from openai import OpenAI
import re
from datetime import date
import json
import os
from dotenv import load_dotenv





# Load environment variables from .env
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is available
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")

# Set your OpenAI API key
client = OpenAI(api_key=api_key)




# Fetch data from Google Sheets
def fetch_google_sheet_data(sheet_url):
    df = pd.read_csv(sheet_url, header=None)
    df = df.transpose()
    return df

# Define the URLs of the Google Sheet tabs (CSV export links)
primary_sheet_url = "https://docs.google.com/spreadsheets/d/13fGf2XoDKuuY-95UchkgNkkwXVv2_YxcKjR9p2cknZg/export?format=csv&gid=78226312"

# Fetch data from both sheets
primary_df = fetch_google_sheet_data(primary_sheet_url)

# Extract variables from dataframes
business_name_primary = primary_df.iloc[1, 0]


# Define functions to save and load data
def save_data(data, filename='sessiondata.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_data(filename='sessiondata.json'):
    if not os.path.exists(filename):
        # Create an empty JSON file if it doesn't exist
        with open(filename, 'w') as file:
            json.dump({}, file)
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()  # Read file content and strip any whitespace
            if content:
                return json.loads(content)  # Load JSON data if the content is not empty
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {}  # Return an empty dictionary if the file is not found or if there's a JSON decode error

# Load existing data
data = load_data()

# Initialize inputs
if 'inputs' not in st.session_state:
    st.session_state.inputs = data.get('inputs', {})

def auto_save_inputs():
    data['inputs'] = st.session_state.inputs
    save_data(data)

# Retrieve values from session state
input_goals = st.session_state.inputs.get('input_goals', '')
input_keydates = st.session_state.inputs.get('input_keydates', '')
input_uniqueness = st.session_state.inputs.get('input_uniqueness', '')
input_media = st.session_state.inputs.get('input_media', '')
input_uniqueness = st.session_state.inputs.get('input_uniqueness', '')
userinputsummary_pastsuccesses = st.session_state.inputs.get('userinputsummary_pastsuccesses', '')
userinputsummary_partnerships = st.session_state.inputs.get('userinputsummary_partnerships', '')
userinputsummary_sminsights = st.session_state.inputs.get('userinputsummary_sminsights', '')
input_success = st.session_state.inputs.get('input_success', '')
input_partnerships = st.session_state.inputs.get('input_partnerships', '')
input_stats = st.session_state.inputs.get('input_stats', '')



st.set_page_config(page_title="Settings", page_icon="👾")

logo_large = "images/Riplo Beta Text Logo 1.svg"
logo_small = "images/Riplo Beta Text Logo Small.svg"
st.logo(logo_large, size="large", icon_image=logo_small)


st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #38493a !important;
        height: 100vh;  /* Ensure full height */
    }
    [data-testid="stSidebarContent"] * {
        color: #f6f2e8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Settings")

st.text("")
st.text("")

# Summarise User Inputs
prompt_template_1 = """
Your task:
Summarize key inputs where necessary.

Your Instructions:
1) Summary of Partnerships/Collaborations: If the text is not consice, summarize the current and past partnerships or collaborations relevant to the business.

The Output:
Your output should only include the line of text. Do not include any other text preceding or following the summary.

The schema of your output should be as follows:

Partnerships/Collaborations: [Summarised partnerships and collaborations]

Below is the information to be summarised.

Partnerships/Collaborations:
{input_partnerships}
"""


# Function to get response from OpenAI's Chat API and handle response extraction
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are part of a prompt chain sequence. You should follow the instructions and generate the output as instructed. This is not a conversation. Your outputs should not include any introductory or explanatory text. Your outputs should be in plain text with a line break on the first line. Ensure that the output is strictly limited to the content requested."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


# Collect user inputs and store them in session state

st.session_state.inputs['input_media'] = st.text_input('Media Capabilities', value=st.session_state.inputs.get('input_media'), on_change=auto_save_inputs)
st.caption("Describe the types of media you can capture or create for your social media posts. Examples include iPhone photos, reel-style videos, or graphics made with Canva.")
st.text("")
st.session_state.inputs['input_partnerships'] = st.text_input('Partnerships and Collaborations:', value=st.session_state.inputs.get('input_partnerships', ''), on_change=auto_save_inputs)
st.caption("List any partnerships or collaborations with other businesses or creatives.")
st.text("")

# Manually trigger auto_save to store the initial values
auto_save_inputs()


# Conditional logic for running LangChain and extracting summaries
if st.button('Save'):
    # Run first prompt
    full_prompt_1 = prompt_template_1.format(input_success=input_success, input_partnerships=input_partnerships, input_stats=input_stats)
    userinputsummary_partnerships = get_chatgpt_response(full_prompt_1)
    
    # Store the summaries in the session state
    st.session_state.inputs['userinputsummary_partnerships'] = userinputsummary_partnerships

    # Automatically save summaries
    auto_save_inputs()
