import streamlit as st
import ssl
import json
import os



# Define functions to save and load data
def save_data(data, filename='sessiondata.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_data(filename='sessiondata.json'):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({}, file)
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()
            if content:
                return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {}

# Load existing data
data = load_data()


# Initialize SessionState for inputs
st.session_state.inputs = data.get('inputs', {})

# Initialize SessionState for repo
if 'repo' not in st.session_state:
    st.session_state.repo = data.get('repo', {})
    
    
# Initialize 'cal' in session state if not present
if 'cal' not in st.session_state:
    st.session_state['cal'] = data.get('cal', {f'calpost_{i}': '' for i in range(1, 11)})

    

def auto_save_cal():
    # Save all 'cal' data from session state into 'cal' in the data dictionary and save it to file
    data['cal'] = st.session_state['cal']
    save_data(data)
    


def save_repo():
    # Update the `data` dictionary to reflect changes in repo
    data['repo'] = st.session_state.repo
    save_data(data)


# Callback function to update `repo` in session state and auto-save
def update_and_save_repo(key):
    # Save the current value of the key in `repo`
    st.session_state.repo[key] = st.session_state[key]
    # Trigger auto-save after updating
    save_repo()




def auto_save_repo():
    # Extract all non-empty values and store them in a list
    non_empty_data = [v for v in st.session_state.repo.values() if v.strip()]
    
    # Create a new organized dictionary with compacted data
    # Fill the upper slots with non-empty data, and the rest with empty strings
    for i in range(1, 41):
        if i <= len(non_empty_data):
            # Assign non-empty data to the top variables (repopostidea_1, repopostidea_2, etc.)
            st.session_state.repo[f'repopostidea_{i}'] = non_empty_data[i-1]
        else:
            # Assign empty strings to the remaining slots
            st.session_state.repo[f'repopostidea_{i}'] = ""

    # Save the compacted repo to sessiondata.json
    data['repo'] = st.session_state.repo
    save_data(data)



def add_to_calpost(repopostidea_key):
    # Get the data from the specified repopostidea variable
    repopostidea_value = st.session_state.get(repopostidea_key, "")

    # Create a list to hold the current calpost values
    calposts = [st.session_state['cal'].get(f'calpost_{i}', "") for i in range(1, 11)]

    # Extract all non-empty values and store them in a list
    non_empty_data = [v for v in calposts if v.strip()]

    # Reorganize the calpost values, filling the upper slots with non-empty data
    for i in range(1, 11):
        if i <= len(non_empty_data):
            st.session_state['cal'][f'calpost_{i}'] = non_empty_data[i-1]
        else:
            st.session_state['cal'][f'calpost_{i}'] = ""

    # Shift existing calpost data down by one slot, from calpost_10 to calpost_2
    for i in range(10, 1, -1):
        st.session_state['cal'][f'calpost_{i}'] = st.session_state['cal'].get(f'calpost_{i-1}', "")

    if repopostidea_value:
        # Insert the new data into calpost_1
        st.session_state['cal']['calpost_1'] = repopostidea_value
        st.success(f"Post idea added to Calendar.")
    else:
        st.warning(f"No data found in {repopostidea_key} to add.")

    # Save the updated calpost variables
    auto_save_cal()




# Streamlit Page Config
st.set_page_config(page_title="Idea Vault", page_icon="📣")


logo_path = "/Users/samwilletts/Echo/dunno/images/Modus Logo.png"
st.logo(logo_path)


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

# Display the full repository of post ideas on page load
st.title("Idea Vault")
st.text("")
st.text("")
st.info("Add post ideas to the Idea Vault from the Idea Generator.")


# if st.button('Save Changes'):
#     auto_save_repo()
#     st.success("Changes saved successfully!")
#     st.rerun()  # Force page reload to reflect the changes


st.text("")


# Display and capture user input in the text_area fields
for i in range(1, 41):
    post_key = f'repopostidea_{i}'

    # Display the text area only if the key exists in repo
    if post_key in st.session_state.repo:
        # Display the text area and allow the user to edit the value
        st.text_area(
            f"Post Idea {i}",
            value=st.session_state.repo[post_key],
            key=post_key,
            label_visibility="visible",
            height=300,
            on_change=update_and_save_repo,  # Trigger auto-save when text changes
            args=(post_key,)
        )

        # Create two columns for buttons
        col1, col2 = st.columns([1, 1])

        # Add a delete button in the first column
        with col1:
            if st.button("Add to Calendar", key=f"add_cal_button_{i}"):
                add_to_calpost(post_key)  # Call your function to add to calendar repo

        # Add an "Add to Calendar" button in the second column
        with col2:
            if st.button("Delete", key=f"delete_button_{i}"):
                # Set the post idea to an empty string on delete and auto-save
                st.session_state.repo[post_key] = ""
                auto_save_repo()
                st.success(f"Post {i} deleted.")
                st.rerun()  # Force page reload to reflect the changes
        st.text("")
        st.text("")

