import streamlit as st
import os
import shutil
import zipfile
import json
from streamlit_shortcuts import add_keyboard_shortcuts
from streamlit_autorefresh import st_autorefresh

def remove_completed_task_from_db(path_of_folder):
    """Remove completed task from the database."""
    try:
        for file in os.listdir(path_of_folder):
            os.remove(os.path.join(path_of_folder, file))
    
        os.rmdir(path_of_folder)
    except:
        pass

def get_action_name(string_val):
    if '/' not in string_val:
        return string_val
    
    else: 
        string_val=string_val.split('/')
        if 'touch' in string_val:
            return 'touch'
        elif 'noball' in string_val:
            return 'noball'
        elif 'notouch' in string_val:
            return 'notouch'

def create_class_folder(choice, dataset_path,meta_data, flag):
    """Dump the current frame (choice) to a JSON file."""
    folder_name = dataset_path.split('/')[-1]
    n_frame = choice + 1
    try:
        # Create necessary directories
        output_folder = f'data/Aug_{folder_name}/{flag}'
        os.makedirs(output_folder, exist_ok=True)

        # Copy the selected file to the output directory
        #shutil.copy(os.path.join(dataset_path, files_list[choice]), os.path.join(output_folder, files_list[choice]))
        
        meta_data[list(meta_data.keys())[choice]]=os.path.join(output_folder, list(meta_data.keys())[choice].split('/')[-1])
        
        with open('all_files_metadata.json','w') as f:
            json.dump(meta_data,f)
        
    except:
        pass
    
    # Save the current frame information to a JSON file
    with open('current_frame.json', 'w') as f:
        json.dump({'current_frame': n_frame}, f)

def root_data_folder(folder_name='0'):
    """Create the 'data' folder and a subfolder based on the batch number."""
    os.makedirs('data', exist_ok=True)
    os.makedirs(f'data/{folder_name}', exist_ok=True)

def load_data(uploaded_file, batch_number):
    """Load data from a ZIP file to the specified batch folder."""
    batch_number = batch_number or '0'

    root_data_folder(batch_number)

    # Extract files from the uploaded ZIP folder
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall('uploaded_folder')

    dest_folder_path = os.path.join("data", batch_number)
    original_folder_path = 'uploaded_folder'

    # Move files from the temporary folder to the destination folder
    for file in os.listdir(original_folder_path):
        shutil.copy(os.path.join(original_folder_path, file), os.path.join(dest_folder_path, file))

    st.success(f'Successfully Created here {dest_folder_path}')

    # Remove the uploaded_folder
    shutil.rmtree('uploaded_folder')

    total_batches = [file for file in os.listdir('data') if 'Aug_' not in file]

    try:
        with open('loaded_option.json', 'r') as f:
            chosen_option = json.load(f)['chosen_option'].split('/')[-1]
        index_val = total_batches.index(chosen_option)
    except (FileNotFoundError, KeyError, ValueError):
        index_val = 0

    # Display options to choose the loaded dataset
    st.write('Choose the data for annotators to annotate:')
    option = st.selectbox(
        "Load Dataset",
        total_batches,
        index=index_val,
        placeholder="Loaded_Dataset",
    )
    load_button = st.button('Load Data')
    
    if load_button:
        selected_option_path = os.path.join(os.path.abspath('data'), option)
        #Creating a metadata for putting all the jsons where it needs to be placed

        all_raw_files=os.listdir(selected_option_path)
        all_raw_files=[os.path.join(selected_option_path,i) for i in all_raw_files]
        to_move_locations=['not_decided' for i in range(len(all_raw_files))]
        all_files=dict(zip(all_raw_files,to_move_locations))
        with open('all_files_metadata.json','w') as json_file:
            json.dump(all_files,json_file)


        with open('loaded_option.json', 'w') as json_file:
            json.dump({'chosen_option': selected_option_path, 'status': 'todo', 'files_list': os.listdir(selected_option_path)}, json_file)
        st.success(f'Successfully Loaded data {selected_option_path}')

def dump_current_frame_info(frame_no):
    with open('current_frame.json', 'w') as f:
        json.dump({'current_frame': frame_no}, f)

def move_all_files_from_metadata(path_of_metadata):
    with open(path_of_metadata,'r') as f:
        metadata=json.load(f)
    
    for both_source_destination in metadata.items():
        shutil.move(both_source_destination[0],both_source_destination[1])

    #os.remove(path_of_metadata)
def user_operations():
    """Perform user operations based on the loaded dataset."""
    try:
        with open('loaded_option.json', 'r') as f:
            dataset_dictionary = json.load(f)
        
        with open('all_files_metadata.json','r') as f:
            all_files_metadata=json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        st.write("Error loading dataset.")
        return

    dataset_status = dataset_dictionary.get('status', 'todo')
    files_list = dataset_dictionary.get('files_list', [])
    dataset_path = dataset_dictionary.get('chosen_option', '')
    

    if not files_list or not dataset_path:
        st.write("Dataset information missing.")
        return

    total_files = len(files_list)
    completed = False
    if dataset_status=='todo':
        # Get the current frame choice
        try:
            with open('current_frame.json', 'r') as f:
                choice = json.load(f).get('current_frame', 0)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            choice = 0
        
        col1, col2, col3 = st.columns(3)

        # this will put a button in the middle column
        with col1:
            back_btn=st.button('Back(a)')
        
        with col3:
            forward_btn=st.button('Forward(d)')
        
        if back_btn:
            choice=choice-1
            if choice!=-1:
                dump_current_frame_info(choice)
            else:
                choice=0
                dump_current_frame_info(choice)

        if forward_btn:
            choice=choice+1
            dump_current_frame_info(choice)

        add_keyboard_shortcuts({
                'a': 'Back(a)',
                'd': 'Forward(d)',
                'A': 'Back(a)',
                'D': 'Forward(d)'
            })


        if choice < total_files:
            # Display progress information
            my_bar = st.progress(choice / total_files)
                
            st.text(f'{choice + 1} / {total_files}')
            try:
                file_name=list(all_files_metadata.keys())[choice].split('/')[-1]
                file_status=get_action_name(list(all_files_metadata.values())[choice])
                coll1,colr2=st.columns(2)
                with coll1:
                    st.subheader(f'file_no: {choice+1}',divider='rainbow')

                with colr2:
                    st.subheader(f'annotation: {file_status}',divider='rainbow'),
                #st.header(f'file: {file_name} <---------------------------->  annotation: {file_status}')
                st.image(list(all_files_metadata.keys())[choice])
            except:
                pass

            # Buttons for user interaction,
            # Make it such that we save the meta data in json format.
            col4,col5,col6=st.columns(3)
            with col4:
                notouch_btn = st.button('No Touch (Left)')
            with col6:
                touch_btn = st.button('Touch (Right)')
            with col5:
                noball_btn = st.button('No Ball (Down)')


            add_keyboard_shortcuts({
                'ArrowLeft': 'No Touch (Left)',
                'ArrowDown': 'No Ball (Down)',
                'ArrowRight': 'Touch (Right)',
            })

            if touch_btn or notouch_btn or noball_btn:
                if touch_btn:
                    flag = 'touch'
                elif notouch_btn:
                    flag = 'notouch'
                elif noball_btn:
                    flag = 'noball'

                # Update choice and dump the current frame
                create_class_folder(choice, dataset_path,all_files_metadata, flag)
                choice += 1
                st_autorefresh(interval=1,limit=2)
                if choice >= total_files:
                    completed = True
                else:
                    my_bar.progress(choice / total_files)
                    st.text(f'{choice + 1} / {total_files}')
                    st.write(files_list[choice])
                    st.image(list(all_files_metadata.keys())[choice])
        else:
            choice=total_files
            with open('current_frame.json', 'w') as f:
                json.dump({'current_frame': choice}, f)
            st.subheader('\n\nAnnotation Complete Please Review annotations then press save !!\n\n\n',divider='blue')
            col9,col10,col11=st.columns(3)
            with col10:
                save_and_end_all=st.button('Save Button')
            
            if save_and_end_all:
                dataset_dictionary['status'] = 'complete'
                with open('current_frame.json', 'w') as f:
                    json.dump({'current_frame': 0}, f)
                with open('loaded_option.json', 'w') as json_file:
                    json.dump(dataset_dictionary, json_file)
                
                st_autorefresh(interval=1,limit=2)
                move_all_files_from_metadata('all_files_metadata.json')
                remove_completed_task_from_db(dataset_path)
    else:
        st.balloons()
        st.write("All files have been covered. The task is complete.")

def render_admin_pages(name):
    """Render admin pages."""
    st.title(f'Welcome {name}')
    
    try:
        # Display completed batches and provide an option to download annotations
        completed_batches = [file for file in os.listdir('data') if 'Aug_' in file]
        st.subheader("Download Annotations: ")
        option_complete = st.selectbox(
            "Choose Annotated Data to Download",
            completed_batches,
            index=None,
            placeholder='Annotated Data',
        )

        if option_complete:
            selected_option_path = os.path.join(os.path.abspath('data'), option_complete)
            zip_file_path = option_complete
            zip_file_name = f'{zip_file_path}.zip'
            shutil.make_archive(zip_file_path, 'zip', selected_option_path)

            with open(zip_file_name, "rb") as fp:
                btn = st.download_button(
                    label=f"Download {zip_file_path}.zip",
                    data=fp,
                    key=f"download_button_{zip_file_path}",  # Ensure a unique key for each download button
                    file_name=f"{zip_file_path}.zip",  # Set the filename for the downloaded file
                )
            os.remove(zip_file_name)

    except Exception as e:
        pass
    
    # Display an input box for batch number and a file uploader for ZIP files
    st.subheader('Assign Task')
    batch_number = st.text_input('Enter Batch Number')
    uploaded_file = st.file_uploader('Choose Zip File (all images)', type=['zip'])
    
    if uploaded_file is not None:
        load_data(uploaded_file, batch_number)

def render_user_pages(name):
    """Render user pages."""
    st.subheader(f'Welcome {name}',divider='red')
    user_operations()
