import streamlit as st
import pandas as pd
import ssl
from openai import OpenAI
import re
from datetime import date
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import textwrap




# Load environment variables from .env
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is available
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")

# Set your OpenAI API key
client = OpenAI(api_key=api_key)





# Function to get today's date
def get_today_date():
    return datetime.today().date()




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

# Initialize SessionState for inputs
if 'inputs' not in st.session_state:
    st.session_state.inputs = data.get('inputs', {})


# Initialize SessionState for repo
if 'repo' not in st.session_state:
    st.session_state.repo = data.get('repo', {})




# Initialize Outputs + Check if this is the first load of a new session
if 'session_active' not in st.session_state:
    # Mark session as active
    st.session_state.session_active = True

    # Initialize session state for outputs
    if 'outputs' not in st.session_state:
        st.session_state.outputs = {}

    # Clear the postidea_ variables in outputs for a fresh session
    for key in list(st.session_state.outputs.keys()):
        if key.startswith('postidea_'):
            del st.session_state.outputs[key]




def auto_save_inputs():
    # Directly assign the entire inputs dictionary to the data dictionary
    data['inputs'] = st.session_state.inputs
    save_data(data)
    

def auto_save_outputs():
    # Directly assign the entire outputs dictionary to the data dictionary
    data['outputs'] = st.session_state.outputs
    save_data(data)


def auto_save_repository():
    # Directly assign the entire repo dictionary to the data dictionary
    data['repo'] = st.session_state.repo
    save_data(data)



# Callback function to update `outputs` in session state and auto-save
def update_and_save_outputs(key):
    # Save the current value of the key in `outputs`
    st.session_state.outputs[key] = st.session_state[key]
    # Trigger auto-save after updating
    auto_save_outputs()



    

# Function to store an individual post idea to the repository
def store_single_post_to_repository(index):
    post_idea = st.session_state.outputs.get(f'postidea_{index}', '')

    # Shift existing posts in the repo back by 1 position
    for i in range(40, 1, -1):
        st.session_state.repo[f'repopostidea_{i}'] = st.session_state.repo.get(f'repopostidea_{i - 1}', "")

    # Store the selected post idea in the first position of the repository
    st.session_state.repo['repopostidea_1'] = post_idea

    # Reorganize the repository to ensure no blank slots in between
    non_empty_data = [v for v in st.session_state.repo.values() if v.strip()]
    for i in range(1, 41):
        st.session_state.repo[f'repopostidea_{i}'] = non_empty_data[i - 1] if i <= len(non_empty_data) else ""

    # Save the compacted repo to sessiondata.json
    data['repo'] = st.session_state.repo
    save_data(data)



def extract_contextual_information(response_text):
    # Match 'Contextual Information' with optional bolding (**) and flexible formatting
    pattern = re.compile(r'\*?\*?Contextual Information\*?\*?:?\s*(.*)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(response_text)
    return match.group(1).strip() if match else ""




# Initialize the flags in session state
if 'ideas_generated' not in st.session_state:
    st.session_state.ideas_generated = False

if 'show_transfer_button' not in st.session_state:
    st.session_state.show_transfer_button = False


# Fetch data from Google Sheets
def fetch_google_sheet_data(sheet_url):
    df = pd.read_csv(sheet_url, header=None)
    df = df.transpose()
    return df

# Define the URLs of the Google Sheet tabs (CSV export links)
primary_sheet_url = "https://docs.google.com/spreadsheets/d/1saYSGXsYJqnGQ5jIoH_feXgBKk41aDEMZIRuQEQXl6c/export?format=csv&gid=78226312"
questionnaire_sheet_url = "https://docs.google.com/spreadsheets/d/1saYSGXsYJqnGQ5jIoH_feXgBKk41aDEMZIRuQEQXl6c/export?format=csv&gid=470780055"
summaries_sheet_url = "https://docs.google.com/spreadsheets/d/1saYSGXsYJqnGQ5jIoH_feXgBKk41aDEMZIRuQEQXl6c/export?format=csv&gid=1055847394"

# Fetch data from both sheets
primary_df = fetch_google_sheet_data(primary_sheet_url)
questionnaire_df = fetch_google_sheet_data(questionnaire_sheet_url)
summaries_df = fetch_google_sheet_data(summaries_sheet_url)

# Extract variables from dataframes
business_name_primary = primary_df.iloc[1, 0]
industry_primary = primary_df.iloc[1, 1]
locations_primary = primary_df.iloc[1, 2]
uvp_primary = primary_df.iloc[1, 4]
usp_primary = primary_df.iloc[1, 5]
products_overview_primary = primary_df.iloc[1, 6]
products_details_primary = primary_df.iloc[1, 7]
ta_specific_primary = primary_df.iloc[1, 8]
company_history_primary = primary_df.iloc[1, 10]
employee_details_primary = primary_df.iloc[1, 11]
org_structure_primary = primary_df.iloc[1, 12]
seasonality_primary = primary_df.iloc[1, 13]
customer_journey_primary = primary_df.iloc[1, 14]
sales_process_primary = primary_df.iloc[1, 15]
sustainability_primary = primary_df.iloc[1, 18]
community_primary = primary_df.iloc[1, 19]
customer_feedback_primary = primary_df.iloc[1, 21]
pricing_strategy_primary = primary_df.iloc[1, 23]
marketing_strategies_primary = primary_df.iloc[1, 24]
loyalty_primary = primary_df.iloc[1, 25]
competetive_advantage_primary = primary_df.iloc[1, 26]
problems_solved_primary = primary_df.iloc[1, 27]
needs_fulfilled_primary = primary_df.iloc[1, 28]
impact_customers_primary = primary_df.iloc[1, 29]
brand_visual_elements = primary_df.iloc[1, 30]
caption_style_primary = primary_df.iloc[1, 31]
caption_examples_primary = primary_df.iloc[1, 32]
key_publicdates_primary = primary_df.iloc[1, 33]
opening_hours_primary = primary_df.iloc[1, 34]


values_form = questionnaire_df.iloc[1, 0]
brand_personality_form = questionnaire_df.iloc[1, 1]
brand_voice_form = questionnaire_df.iloc[1, 2]
company_purpose_form = questionnaire_df.iloc[1, 3]
positioning_form = questionnaire_df.iloc[1, 4]
ta_general_form = questionnaire_df.iloc[1, 5]
competitors_general_form = questionnaire_df.iloc[1, 6]
customer_psychographics_form = questionnaire_df.iloc[1, 7] 
marketing_budget_form = questionnaire_df.iloc[1, 10]
customer_experience_form = questionnaire_df.iloc[1, 19]
resources_form = questionnaire_df.iloc[1, 20]
contentpillars_form = questionnaire_df.iloc[1, 22]
key_tone_form = questionnaire_df.iloc[1, 23]


company_overview_summary = summaries_df.iloc[1, 0]
products_overview_summary = summaries_df.iloc[1, 1]
market_audience_summary = summaries_df.iloc[1, 2]
marketing_summary = summaries_df.iloc[1, 3]
brand_essence_summary = summaries_df.iloc[1, 9]
audience_summary = summaries_df.iloc[1, 10]
content_style_summary = summaries_df.iloc[1, 11]




# Function to get response from OpenAI's Chat API and handle response extraction
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are part of a prompt chain sequence. You should follow the instructions and generate the output as instructed. This is not a conversation. Your outputs should not include any introductory or explanatory text. Your outputs should be in plain text with a line break on the first line. Ensure that the output is strictly limited to the content requested."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


# Extract individual post ideas
def extract_post_outputs(response_text):
    pattern = re.compile(r'Post \d+\n\n(.*?)(?=Post \d+|\Z)', re.DOTALL)
    matches = pattern.findall(response_text)
    
    post_ideas = {}
    post_titles = {}
    for i, match in enumerate(matches, start=1):
        var_name = f'postidea_{i}'
        post_ideas[var_name] = match.strip()
        
        # Extract the "Title" description
        title_match = re.search(r'Title:\s*(.*?)\s*\n', match, re.DOTALL)
        if title_match:
            post_titles[f'posttitle_{i}'] = title_match.group(1).strip()
        else:
            post_titles[f'posttitle_{i}'] = 'None'
    
    # Assign the extracted post ideas and titles to the outputs attribute in session state
    st.session_state.outputs.update(post_ideas)
    st.session_state.outputs.update(post_titles)
    
    return (
        post_ideas.get('postidea_1', ''), post_ideas.get('postidea_2', ''), post_ideas.get('postidea_3', ''),
        post_ideas.get('postidea_4', ''), post_ideas.get('postidea_5', ''), post_ideas.get('postidea_6', ''),
        post_ideas.get('postidea_7', ''), post_ideas.get('postidea_8', ''), post_ideas.get('postidea_9', ''),
        post_ideas.get('postidea_10', ''), post_titles.get('posttitle_1', ''), post_titles.get('posttitle_2', ''),
        post_titles.get('posttitle_3', ''), post_titles.get('posttitle_4', ''), post_titles.get('posttitle_5', ''),
        post_titles.get('posttitle_6', ''), post_titles.get('posttitle_7', ''), post_titles.get('posttitle_8', ''),
        post_titles.get('posttitle_9', ''), post_titles.get('posttitle_10', '')
    )


# Streamlit Page Config
st.set_page_config(page_title="Idea Generator", page_icon="📣")


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
        color: #f2eee7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app layout
st.caption(f"{business_name_primary}")
st.title("Idea Generator")
st.text("")



# Retrieve input values from session state
input_goals = st.session_state.inputs.get('input_goals', '')
input_keydates = st.session_state.inputs.get('input_keydates', '')
input_media = st.session_state.inputs.get('input_media', '')
input_uniqueness = st.session_state.inputs.get('input_uniqueness', '')
userinputsummary_pastsuccesses = st.session_state.inputs.get('userinputsummary_pastsuccesses', '')
userinputsummary_partnerships = st.session_state.inputs.get('userinputsummary_partnerships', '')
userinputsummary_sminsights = st.session_state.inputs.get('userinputsummary_sminsights', '')
input_success = st.session_state.inputs.get('input_success', '')
input_partnerships = st.session_state.inputs.get('input_partnerships', '')
input_stats = st.session_state.inputs.get('input_stats', '')



# User Inputs (Saved)
st.session_state.inputs['input_goals'] = st.text_input('Content goals:', value=st.session_state.inputs.get('input_goals', ''), on_change=auto_save_inputs)
st.text("")
st.session_state.inputs['input_keydates'] = st.text_input('Key upcoming dates/events:', value=st.session_state.inputs.get('input_keydates', ''), on_change=auto_save_inputs)
st.text("")





# Conditional logic for running LangChain and extracting
if st.button('Generate Content Ideas'):


    # Post ideas stored as multi-line strings
    postidea_1 = textwrap.dedent("""\
        Title: Nutella Moments of Merry

        Idea: "Nutella Moments of Merry" - Imagine gifting these Nutella-filled treats to loved ones. Each doughnut becomes a shared nibble of festive delight, inviting warmth and smiles amidst holiday preparations.

        Call-to-Action: "Swing by to grab a dozen doughnuts to share the merry!"

        Creative Focus: Visual-Focused

        Purpose: Increase Foot Traffic

        Media: A cosy, inviting video showing a fresh batch of Nutella doughnuts being dusted with powdered sugar. Capture the process of wrapping these doughnuts in a simple, festive box tied with a ribbon. Overlay text reads, “Share the warmth with a Nutella surprise!” Use warm lighting and festive decorations.
    """)

    postidea_2 = textwrap.dedent("""\
        Title: Coffee with a Cause

        Idea: "Coffee with a Cause" - Each cup supports initiatives that better the community. Experience your coffee as not just a morning wake-up but a small act of kindness that contributes to larger community efforts.

        Call-to-Action: "Join us for a cup that cares—visit us today and support local initiatives!"

        Creative Focus: Concept-Focused

        Purpose: Promote Awareness

        Media: A designed graphic showcasing a steaming cup of coffee with community-focused symbols (handshakes, hearts, etc.). Text overlays the image, reading, “Every cup helps our community. Sip with purpose!” Use warm tones and incorporate natural wood textures for a comforting visual.
    """)

    postidea_3 = textwrap.dedent("""\
        Title: Sip Back in Time

        Idea: "Sip Back in Time" - Relive childhood Christmas mornings with each indulgent sip. This hot chocolate, topped with fluffy marshmallows, offers a cosy embrace on chilly winter evenings.

        Call-to-Action: "Pop in to warm up with a cup full of nostalgia!"

        Creative Focus: Visual-Focused

        Purpose: Drive Engagement

        Media: A fun, short video clip capturing a marshmallow floating atop hot chocolate slowly melting into creamy swirls. Overlay text reads, “Childhood in a cup this Christmas!” Include subtle sound effects of crackling winter fires to evoke a sense of warmth and nostalgia.
    """)

    postidea_4 = textwrap.dedent("""\
        Title: Pancake Paradise

        Idea: "Pancake Paradise" - After the bustling festivities, unwind with a stack of fluffy pancakes, perfect for a lazy morning with family, where syrupy sweetness marks the bliss of a slow day.

        Call-to-Action: "Treat yourself—stop by for a lazy morning pancake feast!"

        Creative Focus: Visual-Focused

        Purpose: Increase Foot Traffic

        Media: A photo carousel featuring stacks of golden pancakes drenched in syrup, butter melting on top, set against a beautifully laid-back breakfast table. Use morning light to give a homely, serene feel and add wooden cutlery.
    """)

    postidea_5 = textwrap.dedent("""\
        Title: Sunset Suppers

        Idea: "Sunset Suppers" - Pack a couple of toasted sandwiches for your beach outing, where they become the staple of your picnic, blending sumptuous flavours with ease and mobility.

        Call-to-Action: "Grab a toasty favourite for your next beach picnic!"

        Creative Focus: Visual-Focused

        Date/Event: Summer Holidays

        Purpose: Drive Engagement

        Media: Capture a lifestyle TikTok-style video of a beach picnic featuring a diverse selection of toasted sandwiches being unpacked and enjoyed at sunset. Show hands reaching for sandwiches, with waves gently crashing in the background.
    """)

    postidea_6 = textwrap.dedent("""\
        Title: Adventure Fuel

        Idea: "Adventure Fuel" - Nuggets and fries become the backdrop of laughter and play during summer holidays, effortlessly satisfying kids after an action-packed day by the pool.

        Call-to-Action: "Refuel those summer adventures—treat the kids to their favourites!"

        Creative Focus: Concept-Focused

        Date/Event: Summer Holidays

        Purpose: Increase Foot Traffic

        Media: A playful photo of a colourful poolside scene, showcasing a kids' tray with nuggets and fries artfully arranged, surrounded by pool toys. Use vibrant colours to capture the essence of fun and summer.
    """)

    postidea_7 = textwrap.dedent("""\
        Title: Boxing Day Bliss

        Idea: "Boxing Day Bliss" - This organic coffee helps ease the transition from festive celebrations to everyday calm, offering a tranquil morning brew that revitalises and refreshes.

        Call-to-Action: "Join us for a breather with our organic brews!"

        Creative Focus: Concept-Focused

        Purpose: Build Community

        Media: A serene early morning photo capturing a steaming cup of organic fair-trade coffee on a wooden table by the window, with natural light pouring in. Use earthy tones.
    """)

    postidea_8 = textwrap.dedent("""\
        Title: Wrap and Roll

        Idea: "Wrap and Roll" - Perfect for spontaneous summer picnics, these wraps provide a satisfying bite without weighing you down, embodying the lightness and zest of the season.

        Call-to-Action: "Ready, set, wrap! Grab yours for the perfect picnic bite!"

        Creative Focus: Visual-Focused

        Date/Event: Summer Holidays

        Purpose: Increase Foot Traffic

        Media: A dynamic video showcasing different wraps being rolled and sliced, set against a backdrop of picnic essentials like a blanket and a wicker basket. The video ends with a hand grabbing the wraps.
    """)


    st.text("")
    st.text("")
    st.divider()
    st.text("")




# Loop to display up to 10 editable post ideas with auto-save functionality
for i in range(1, 11):
    # Define the session key for each post idea in outputs
    postidea_key = f'postidea_{i}'

    if f"postidea_{i}" in globals() and globals()[f"postidea_{i}"].strip():
        # Display editable text area with auto-save on edit
        st.text_area(
            f"Post Idea {i}",
            value=globals()[f"postidea_{i}"],
            key=f"postidea_{i}",
            height=280,
            on_change=update_and_save_outputs,  # Auto-save when edited
            args=(f"postidea_{i}",)  # Pass the key to the callback
        )

        # Button to delete the specific post idea
        if st.button(f"Delete Post Idea {i}"):
            del st.session_state.outputs[postidea_key]  # Remove the data
            st.session_state[f'post_saved_{i}'] = False  # Reset save status
            st.experimental_rerun()  # Refresh the page to update the UI

        # Button to save the specific post idea
        if st.button(f"Save Post Idea {i}"):
            st.session_state[f'post_saved_{i}'] = True

        # Check if the save status for this post idea is True
        if st.session_state.get(f'post_saved_{i}', False):
            store_single_post_to_repository(i)
            st.success(f"Post Idea {i} saved to Idea Vault.")
            auto_save_repository()  # Save the repository state after updating

            # Reset the save status to avoid repeated execution
            st.session_state[f'post_saved_{i}'] = False
    
    st.text("")



# Button to clear all postidea_ variables in outputs
if st.button("Wipe All"):
    # Iterate over keys in outputs and delete those that start with 'postidea_'
    for key in list(st.session_state.outputs.keys()):
        if key.startswith('postidea_'):
            del st.session_state.outputs[key]
    
    st.success("All post ideas cleared.")





