import streamlit as st
import pandas as pd
import ssl
from openai import OpenAI
import re
from datetime import date
import json
import os
from datetime import datetime, timedelta, timezone
from dateutil import parser
from icalendar import Calendar, Event
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





# Function to get today's date
def get_today_date():
    return datetime.today().date()

# Function to determine if a year is a leap year
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# Function to determine the current season and next season in New Zealand
def get_seasons(today=None):
    if today is None:
        today = get_today_date()
    
    # Convert today to a datetime object with time components for comparison
    today_datetime = datetime.combine(today, datetime.min.time())
    
    # Adjust February dates based on whether the current year is a leap year
    february_last_day = 29 if is_leap_year(today.year + 1) else 28
    
    # Define the start dates of the seasons
    seasons = {
        "Summer": (datetime(today.year, 12, 1), datetime(today.year + 1, 2, february_last_day, 23, 59, 59)),
        "Autumn": (datetime(today.year, 3, 1), datetime(today.year, 5, 31, 23, 59, 59)),
        "Winter": (datetime(today.year, 6, 1), datetime(today.year, 8, 31, 23, 59, 59)),
        "Spring": (datetime(today.year, 9, 1), datetime(today.year, 11, 30, 23, 59, 59)),
    }
    
    current_season = None
    next_season = None
    
    # Identify the current season
    for season, (start_date, end_date) in seasons.items():
        if start_date <= today_datetime <= end_date:
            current_season = season
            break
    
    # Determine the next season
    next_season_start = {
        "Summer": datetime(today.year, 3, 1),
        "Autumn": datetime(today.year, 6, 1),
        "Winter": datetime(today.year, 9, 1),
        "Spring": datetime(today.year, 12, 1),
    }
    next_season = {
        "Summer": "Autumn",
        "Autumn": "Winter",
        "Winter": "Spring",
        "Spring": "Summer"
    }[current_season]
    
    # Check if the next season starts within one month
    one_month_later = today_datetime + timedelta(days=30)
    if next_season_start[current_season] <= one_month_later:
        return current_season, next_season
    else:
        return current_season, None

# Calculate today's date and determine the current and next seasons
today_date = get_today_date()
current_season, next_season = get_seasons(today_date)



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

# # Initialize SessionState for inputs
# st.session_state.inputs = data.get('inputs', {})

# Initialize SessionState for inputs
if 'inputs' not in st.session_state:
    st.session_state.inputs = data.get('inputs', {})
    

# Initialize SessionState for outputs
if 'outputs' not in st.session_state:
    st.session_state.outputs = data.get('outputs', {})

# Initialize SessionState for repo
if 'repo' not in st.session_state:
    st.session_state.repo = data.get('repo', {})


# Initialize SessionState for cal
if 'cal' not in st.session_state:
    st.session_state.cal = data.get('cal', {})

# Ensure calpost_ variables from sessiondata.json are properly initialized in session state
for i in range(1, 11):
    calpost_key = f'calpost_{i}'
    
    # If the key exists in sessiondata.json, it will be loaded, otherwise initialize to empty string
    if calpost_key not in st.session_state.cal:
        st.session_state.cal[calpost_key] = ""


# Initialize 'uid_counter' within 'cal' only if it doesn't already exist in sessiondata.json or session state
if 'uid_counter' not in st.session_state.cal:
    st.session_state.cal['uid_counter'] = data.get('cal', {}).get('uid_counter', 1)



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
    
    
def auto_save_cal():
    # Directly assign the entire cal dictionary to the data dictionary
    data['cal'] = st.session_state.cal
    save_data(data)
    
    
def reorganize_calposts():
    # Create a list to hold the current calpost values
    calposts = [st.session_state['cal'].get(f'calpost_{i}', "") for i in range(1, 11)]

    # Extract all non-empty values and store them in a list
    non_empty_cal_data = [v for v in calposts if v.strip()]

    # Reorganize the calpost values, filling the upper slots with non-empty data
    for i in range(1, 11):
        if i <= len(non_empty_cal_data):
            st.session_state['cal'][f'calpost_{i}'] = non_empty_cal_data[i-1]
        else:
            st.session_state['cal'][f'calpost_{i}'] = ""



def store_to_repository():
    # Retrieve new post ideas from the outputs attribute
    new_post_ideas = [st.session_state.outputs.get(f'postidea_{i}', '') for i in range(1, 11)]
    
    # Shift existing posts in the repo back by 10 positions
    for i in range(30, 0, -1):
        st.session_state.repo[f'repopostidea_{i + 10}'] = st.session_state.repo.get(f'repopostidea_{i}', None)
    
    # Add new post ideas to the first 10 positions in the repo
    for i in range(10):
        st.session_state.repo[f'repopostidea_{i + 1}'] = new_post_ideas[i]

    # Automatically save the state
    auto_save_repository()
    



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
primary_sheet_url = "https://docs.google.com/spreadsheets/d/13fGf2XoDKuuY-95UchkgNkkwXVv2_YxcKjR9p2cknZg/export?format=csv&gid=78226312"

# Fetch data from both sheets
primary_df = fetch_google_sheet_data(primary_sheet_url)

# Extract variables from dataframes
business_name_primary = primary_df.iloc[1, 0]



# Retrieve From Cal
calpost_1 = st.session_state.cal.get('calpost_1', '')
calpost_2 = st.session_state.cal.get('calpost_2', '')
calpost_3 = st.session_state.cal.get('calpost_3', '')
calpost_4 = st.session_state.cal.get('calpost_4', '')
calpost_5 = st.session_state.cal.get('calpost_5', '')
calpost_6 = st.session_state.cal.get('calpost_6', '')
calpost_7 = st.session_state.cal.get('calpost_7', '')
calpost_8 = st.session_state.cal.get('calpost_8', '')
calpost_9 = st.session_state.cal.get('calpost_9', '')
calpost_10 = st.session_state.cal.get('calpost_10', '')

# Retrieve Inputs
input_startdate = st.session_state.inputs.get('input_startdate', '')
input_freq = st.session_state.inputs.get('input_freq', '')




# Define the prompt templates

# Generate Dates
prompt_template_1 = """
Your Job: Provide the following list of post ideas in a calendar format to form a content calendar.

Your Instructions
1. Organise the posts into a logical order.
2. Assign logical dates and times to each post.
3. Summarise the Content Theme, Purpose, and Media info into a super concise "Description"
4. Output the content calendar in a single text output.

Consider the following when ordering and assigning dates/times:

1. The first post should be assigned the date: {input_startdate} 2024.
2. All other posts should be assigned a date following the first post with a posting frequecy of {input_freq} posts per week.
2. The times should be in the early evening.
3. You should consider the following when generating the order:
3.1 Post Theme/Topic: Ensure varying themes/topics. Avoid posting about the same topic/theme consecutively where possible.
3.2 Media Difficulty: Ensure the first two posts have "easy to produce" media. For example, a single photo is easy to produce, wheras a short video is harder to produce.

The Output:

Your output should have the following schema for each post idea;

Post Number: [POST 1 NUMBER (EG. '1')]
Title: [POST 1 TITLE]
Description: [POST 1 DESCRIPTION]
Date: [POST 1 DATE EG. "5th December 2025"]
Time: [POST 1 TIME EG. 7pm]

You should separate each post idea with two line breaks. Do not use any formatting such as bold text, bullet points, or numbering lists.

You must include all information from the Post Ideas as below. Do not alter the Post Ideas in any way.

You should only include posts that contain data. Skip any posts that do not have any data.

Here are the post ideas.

Post 1:
{calpost_1}

Post 2:
{calpost_2}

Post 3:
{calpost_3}

Post 4:
{calpost_4}

Post 5:
{calpost_5}

Post 6:
{calpost_6}

Post 7:
{calpost_7}

Post 8:
{calpost_8}

Post 9:
{calpost_9}

Post 10:
{calpost_10}


"""



# Format to JSON
prompt_template_2 = """
Format the following data in JSON format:

{caledartext_output}


The data provided above is one or more post ideas. You must include all of the post ideas in the output.


You need to provide the data in valid JSON format like so:

{{
  "titleone": "<title of Post 1>",
  "description1": "<description of Post 1>",
  "datetime1": "<date/time of Post 1>",
  
  "title2": "<title of Post 2>",
  "description2": "<description of Post 2>",
  "datetime2": "<date/time of Post 2>",
  
  "title3": "<title of Post 3>",
  "description3": "<description of Post 3>",
  "datetime3": "<date/time of Post 3>"
}}


Here is an example output:
{{
  "title1": "Sample Event Title",
  "description1": "Sample event description."
  "datetime1": "2025-12-05T19:00:00+12:00",
}}


Handling Dat/Time: Convert the provided date and time into an ISO 8601 format in New Zealand timezone (UTC+12:00). Use this format: "YYYY-MM-DDTHH:MM:SS+12:00". For example, "5th December 2025 at 7pm" would become "2025-12-05T19:00:00+12:00".

Handling Various Number of Posts: You will be given up to 10 post ideas. You must only include the number of posts that are provided in the JSON output.

Separating Key Value Pairs With Commas: It is imperative that you separate each key value pair with a comma. For example, note the comma in this line of the example JSON: "titleone": "Sample Event Title",

Make sure the JSON is properly structured, including commas, and does not contain any extraneous text.


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





# Streamlit Page Config
st.set_page_config(page_title="Content Calendar", page_icon="📣")

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
st.title("Content Calendar Generator")
st.text("")



# Check if all calpost values are empty
all_empty = all(not st.session_state.cal.get(f'calpost_{i}', '').strip() for i in range(1, 11))

# Display "Add from Idea Vault" if all calpost slots are empty
if all_empty:
    st.info("No post ideas in calendar.")
    st.info("Add post ideas to the calendar from the Idea Vault.")
    

st.text("")
st.text("")

# User Inputs (Saved)
st.session_state.inputs['input_startdate'] = st.text_input('Start Date:', value=st.session_state.inputs.get('input_startdate', ''), on_change=auto_save_inputs)
st.text("")
st.session_state.inputs['input_feq'] = st.text_input('Posting Frequency:', value=st.session_state.inputs.get('input_freq', ''), on_change=auto_save_inputs)
st.text("")
st.text("")



# Conditional logic for running LangChain and extracting
if st.button('Create Calendar'):
    
    # Generate Times
    full_prompt_1 = prompt_template_1.format(
        calpost_1 = calpost_1,
        calpost_2 = calpost_2,
        calpost_3 = calpost_3,
        calpost_4 = calpost_4,
        calpost_5 = calpost_5,
        calpost_6 = calpost_6,
        calpost_7 = calpost_7,
        calpost_8 = calpost_8,
        calpost_9 = calpost_9,
        calpost_10 = calpost_10,
        input_startdate = input_startdate,
        input_freq = input_freq
        
    )
    caledartext_output = get_chatgpt_response(full_prompt_1).strip()
    st.write("Output after Prompt Template 1:", caledartext_output)


    # Format to JSON
    full_prompt_2 = prompt_template_2.format(
        caledartext_output = caledartext_output
    )
    fullcalendar_ical = get_chatgpt_response(full_prompt_2).strip()
    st.write("Output after Prompt Template 2:", fullcalendar_ical)
    
    
    # Parse the JSON output
    try:
        json_calendar = json.loads(fullcalendar_ical)
        st.write("Formatted JSON Output:")
        st.json(json_calendar)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON: {e}")
    

    st.divider()
    
    # Set the flags to show the transfer button
    st.session_state.ideas_generated = True
    st.session_state.show_transfer_button = True

    
if st.session_state.show_transfer_button:
    
    # Convert JSON data to iCalendar format
    def create_icalendar(json_calendar):
        cal = Calendar()
        nz_time = timezone(timedelta(hours=12))
        
        # Retrieve UID counter
        uid_counter = data['cal'].get("uid_counter", 1)

        for i in range(1, 11):  # Loop through potential 10 events
            datetime_key = f'datetime{i}'
            title_key = f'title{i}'
            description_key = f'description{i}'

            # Check for required fields and skip if any are missing
            if datetime_key in json_calendar and title_key in json_calendar and description_key in json_calendar:
                datetime_str = json_calendar[datetime_key]
                
                # Try parsing the datetime string, with a fallback
                try:
                    dtstart = datetime.fromisoformat(datetime_str)
                except ValueError:
                    dtstart = parser.parse(datetime_str).replace(tzinfo=nz_time)

                # Create the event
                event = Event()
                event.add('uid', str(uid_counter))  # Use the current UID counter value
                event.add('dtstamp', datetime.now().astimezone())
                event.add('dtstart', dtstart)
                event.add('summary', json_calendar[title_key])
                event.add('description', json_calendar[description_key])
                cal.add_component(event)
                
                # Increment the UID counter in session state for the next event
                st.session_state.cal['uid_counter'] += 1
                auto_save_cal()

        return cal.to_ical()

    # Assuming you have already parsed your JSON object into `json_calendar`
    ical_content = create_icalendar(json_calendar)

    # Allow user to download iCalendar file using Streamlit
    st.download_button(
        label="Download Calendar",
        data=ical_content,
        file_name="calendar.ics",
        mime="text/calendar"
    )
    
        
    # Reset the flag after transferring ideas
    st.session_state.show_transfer_button = False
    st.session_state.ideas_generated = False


st.divider()

st.subheader("Calendar Post Ideas")

st.text("")

if st.button("Wipe All Calendar Posts"):
    # Set all calpost variables to empty strings
    for i in range(1, 11):
        st.session_state['cal'][f'calpost_{i}'] = ""
    
    auto_save_cal()  # Optionally save the changes
    st.success("All calendar posts have been wiped.")
    st.text("")
    st.rerun()  # Refresh the page to reflect changes
    
st.text("")




# Loop through the calpost data and create text areas with delete buttons below each
for i in range(1, 11):
    # Define the key for each calpost
    key = f'calpost_{i}'
    
    # Get the value of the current calpost
    calpost_value = st.session_state.cal.get(key, '')

    # Only display the text area and delete button if the calpost contains data
    if calpost_value.strip():  # Check if the post is not empty or just whitespace
        # Display the text area for each calpost
        st.session_state.inputs[key] = st.text_area(
            f'Post {i}:', 
            height=300, 
            value=calpost_value,
            key=f'text_area_{i}'
        )

        # Display the delete button below each text area
        if st.button(f"Remove Post Idea", key=f"delete_cal_button_{i}"):
            # Set the corresponding post idea to an empty string when delete is clicked
            st.session_state.cal[f'calpost_{i}'] = ""
            reorganize_calposts()
            auto_save_cal()
            st.text("")
            # Display success message after deletion
            st.success(f"Post {i} deleted. Click 'Save' to save the deletion.")
            st.text("")
            st.rerun()

        st.text("")  # Add some spacing between items


