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



# Load environment variables from .env
load_dotenv()






# Define functions to save and load data
def save_data(data, filename='sessiondata.json'):
    with open(filename, 'w') as file:
        json.dump(data, file)

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

def auto_save_inputs():
    # Directly assign the entire inputs dictionary to the data dictionary
    data['inputs'] = st.session_state.inputs
    save_data(data)




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
key_tone_form = questionnaire_df.iloc[1, 23]

company_overview_summary = summaries_df.iloc[1, 0]
products_overview_summary = summaries_df.iloc[1, 1]
market_audience_summary = summaries_df.iloc[1, 2]
marketing_summary = summaries_df.iloc[1, 3]
brand_essence_summary = summaries_df.iloc[1, 9]
audience_summary = summaries_df.iloc[1, 10]
content_style_summary = summaries_df.iloc[1, 11]




# Streamlit Page Config
st.set_page_config(page_title="Post Builder", page_icon="📣")

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


# Streamlit app layout
st.caption(f"{business_name_primary}")
st.title("Post Builder")
st.text("")


# Retrieve values from session state
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




# User Input
input_postidea = st.text_input('Post Idea')
st.text("")
input_specificinfo = st.text_input('Specific Information For The Post')
st.text("")


# Conditional logic for running LangChain and extracting summaries
if st.button('Create Post'):


    post_filetitle = "Wrap and Roll"
    
    caption_final_output = """Who's ready for a summer of wrap-and-roll adventures? 🌞🌯 Our zesty, freshly made Chicken Caesar or Falafel & Hummus wraps are your picnic’s perfect plus one. Light, satisfying, and full of flavour - they won't weigh down your summer fun! Ready, set, wrap! Drop by for your perfect picnic bite today. Bon Appétit! 🍽️"""

    mediadescription_final_output = """Media Type: Short Video

    Media Overview: A joyful and dynamic summer video showcasing the rolling and slicing of Short Black Café’s signature wraps against a backdrop of a vibrant summer picnic scene. The video aims to draw viewers in with its playful, light-hearted tone, highlighting the cafe's mouth-watering wraps as the ideal food choice for a summer picnic.

    Detailed Description:

    Scene 1: Close-up shot of the pristine, fresh ingredients for the Chicken Caesar and Falafel & Hummus wraps laid out on a wooden tabletop. Overlaid text reads "Wrap and Roll: Your Perfect Picnic Starts Here!" The FONT should be a modern sans-serif, such as Helvetica or Open Sans, aligned centrally.

    Scene 2: A pair of hands expertly start assembling the wraps one by one, first the Chicken Caesar, then the Falafel & Hummus, on a wooden cutting board. The camera follows every move, giving off a feel of genuine warmth, and locally sourced ingredients.

    Scene 3: Both wraps get rolled tightly, and the hands slice them diagonally with a large knife. The inner layers of the wraps, featuring a perfect blend of ingredients, are visible and look tempting. Overlay text reads "Freshly Made Just for You!" in the same modern sans-serif font, aligned centrally.

    Scene 4: A quick transition to a sunny outdoor setting: a laid-out picnic blanket, a vintage wicker basket, and a pair of sunglasses. The cut wraps land gently on a plate next to the basket.

    Scene 5: A hand reaches out to grab a wrap slice, lifting it towards the camera. The frame freezes for a moment, and overlay text appears: "Ready, Set, Wrap! Grab Yours for the Perfect Picnic Bite!" Once again, use the sans-serif font, aligned centrally.

    The video ends with a fade to a black frame carrying the White Short Black Café logo and the store address in a clean, modern sans-serif font.

    Throughout the video, a light-hearted and charming tune, epitomising summer holidays, plays in the background, enhancing the narrative's vibrancy and energy.

    The video's tone and aesthetics should match Short Black Café's visual style - a balance between minimalism and approachability using a monochrome palette of black and white, complemented by natural brown wood textures for warmth. The playful and engaging brand voice, along with the authentic local charm, should resonate in each frame."""
    
    mediainstructions_final_output = """Preparation:  
    - Gather fresh ingredients for Chicken Caesar and Falafel & Hummus wraps. Have a wooden table or cutting board available, which will be your working area.
    - Ensure you have a set for the picnic scene, including a picnic blanket, vintage wicker basket, a pair of sunglasses and plates.
    - Prepare your smartphone camera or a digital camera equipped. 
    - For the background tune, select a royalty-free light-hearted, charming tune that symbolizes summer holidays.

    Capturing the Media:  
    - Scene 1: Arrange ingredients on the wooden table/cutting board and capture a close-up shot. Point the camera downwards and keep everything in focus. 
    - Scene 2: Hands should assemble wraps as the camera films from the side-view, close enough to capture the process, yet not too close to obscure the movement. Keep movement smooth and precise.
    - Scene 3: After rolling the wraps, slice them diagonally in full view of the camera. The camera should be positioned to capture the delicious layers within the wrap.
    - Scene 4: After slicing, move the scene to an outdoor setting. Place the plate with wrap slices on the picnic blanket and capture the whole scene including the basket and sunglasses. 
    - Scene 5: Have a hand reach for a wrap slice and lift it towards the camera. Freeze this frame for a moment before closing the shot.

    Editing and Final Touches:
    - Import video clips into a video editing app on your smartphone or computer. Trim each clip to keep only the necessary footage and connect scenes smoothly.
    - In Scene 1, add the text "Wrap and Roll: Your Perfect Picnic Starts Here!" in a modern sans-serif font (e.g., Helvetica or Open Sans). Place the text centrally in the frame.
    - After Scene 3 completes, overlay the text "Freshly Made Just for You!" in the same sans-serif font as before, centrally aligned with the existing footage.
    - When the frame freezes in Scene 5, add the final overlay text: "Ready, Set, Wrap! Grab Yours for the Perfect Picnic Bite!" in the same style as previous scenes.
    - Continue with the black frame carrying the Short Black Café logo and the store address in a clean, modern, and centered sans-serif font.
    - Add the light-hearted and charming background tune, making sure it is properly synchronized with the footage's movement and change of scenes.

    Tips:  
    - Ensure there is ample natural light, especially when filming food. This will help your ingredients look vibrant. If natural light is not available, use a good quality artificial light source.
    - Keep all movements in the shot slow and deliberate to make them easier to follow for your audience.
    - Experiment with the volume levels of the background music to ensure it harmonizes with, rather than detracts from, the video footage.
    - If overlay text seems to blend with the scene, try adding a subtle shadow or outline for improved readability."""



    st.divider()

    # Final Output
    st.text_area("Caption", caption_final_output, height=280)
    st.text("")
    st.text_area("Media Description", mediadescription_final_output, height=280)
    st.text("")
    st.text_area("Media Instructions", mediainstructions_final_output, height=280)


    # Download Post Idea As File
    download_file = (
        f"{post_filetitle}\n\n"
        f"Caption:\n\n{caption_final_output}\n\n"
        f"Media Description:\n\n{mediadescription_final_output}\n\n"
        f"Media Instructions:\n\n{mediainstructions_final_output}\n"
    )



    # Download button
    st.text("")
    st.divider()
    st.text("")
    st.download_button(
        label=f"Download Post – {post_filetitle}",
        data=download_file,
        file_name=f"{post_filetitle}.txt",
        mime="text/plain"
    )
