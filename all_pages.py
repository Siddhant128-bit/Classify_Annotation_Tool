import streamlit as st
import os
import shutil
import zipfile
import json

def dump_current_frame(choice):
    """Dump the current frame (choice) to a JSON file."""
    with open('current_frame.json', 'w') as f:
        json.dump({'current_frame': choice}, f)

def root_data_folder(folder_name='0'):
    """Create the 'data' folder and a subfolder based on the batch number."""
    try:
        os.mkdir('data')
    except FileExistsError:
        pass

    try:
        os.mkdir(f'data/{folder_name}')
    except FileExistsError:
        pass

def load_data(uploaded_file, batch_number):
    """Load data from a ZIP file to the specified batch folder."""
    if not batch_number:
        batch_number = '0'

    root_data_folder(batch_number)
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall('uploaded_folder')

    dest_folder_path = os.path.join("data", batch_number)
    original_folder_path = os.path.join('uploaded_folder', os.listdir('uploaded_folder')[0])

    for file in os.listdir(original_folder_path):
        shutil.move(os.path.join(original_folder_path, file), os.path.join(dest_folder_path, file))

    st.success(f'Successfully Created here {dest_folder_path}')

    # Remove the uploaded_folder
    [os.rmdir(os.path.join(os.path.abspath('uploaded_folder'), file)) for file in os.listdir(os.path.abspath('uploaded_folder'))]
    os.rmdir('uploaded_folder')

    total_batches = os.listdir('data')
    
    # Attempt to load the last selected option
    try:
        with open('loaded_option.json', 'r') as f:
            chosen_option = json.load(f)['chosen_option'].split('/')[-1]
        index_val = total_batches.index(chosen_option)
    except (FileNotFoundError, KeyError, ValueError):
        index_val = 0

    option = st.selectbox(
        "Load Dataset",
        total_batches,
        index=index_val,
        placeholder="Loaded_Dataset",
    )
    load_button = st.button('Load Data')
    if load_button:
        # Save the selected option to a JSON file
        selected_option_path = os.path.join(os.path.abspath('data'), option)
        with open('loaded_option.json', 'w') as json_file:
            json.dump({'chosen_option': selected_option_path, 'status': 'todo'}, json_file)
        st.success(f'Successfully Loaded data {selected_option_path}')

def user_operations():
    """Perform user operations based on the loaded dataset."""
    with open('loaded_option.json', 'r') as f:
        dataset_dictionary = json.load(f)

    dataset_status = dataset_dictionary.get('status', 'todo')
    if dataset_status == 'todo':
        dataset_path = dataset_dictionary.get('chosen_option', '')
        if dataset_path:
            all_files = os.listdir(dataset_path)
            total_files = len(all_files)
            progress_text = st.empty()
            my_bar = st.progress(0)

            try:
                with open('current_frame.json', 'r') as f:
                    choice = json.load(f)['current_frame']
            except (FileNotFoundError, KeyError):
                choice = 0

            st.text(f'{choice + 1} / {total_files}')

            next_btn = st.button('Next Button')
            if next_btn:
                choice += 1
                dump_current_frame(choice)
                print(choice)
                my_bar.progress(choice / total_files)

            if len(all_files) <= choice:
                my_bar.empty()
                progress_text.empty()
                choice = 0
                dump_current_frame(choice)
                dataset_dictionary['status'] = 'complete'
                with open('loaded_option.json', 'w') as json_file:
                    json.dump(dataset_dictionary, json_file)
    else:
        st.write('No Task Allocated !!')

def render_admin_pages(name):
    """Render admin pages."""
    st.title(f'Welcome {name}')
    batch_number = st.text_input('Enter Batch Number')
    uploaded_file = st.file_uploader('Choose Zip File (all images)', type=['zip'])
    if uploaded_file is not None:
        load_data(uploaded_file, batch_number)

def render_user_pages(name):
    """Render user pages."""
    st.title(f'Welcome {name}')
    try:
        user_operations()
    except:
        st.write('No Task Allocated !!')