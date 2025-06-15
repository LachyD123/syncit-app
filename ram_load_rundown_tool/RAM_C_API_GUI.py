import tkinter as tk

if __name__ == "__main__":
    try:
        from scripts.txt_settings import load_settings
    except:
        root = tk.Tk()
        root.title("RAM API GUI")
        from tkinter import messagebox
        messagebox.showerror("Error", "No 'scripts' folder found. \n\n Please ensure the 'scripts' folder is in the same directory as the RAM_C_API_GUI.py file, this folder can be forund in the T:\\Software Dev\\RAM C API\\scripts")
        root.destroy()
        quit()

if __name__ == "__main__":
    try:

        import ram_concept
    except:
        root = tk.Tk()
        root.title("RAM API GUI")
        from tkinter import messagebox
        messagebox.showerror("Error", "the RAM Concept API is not installed. \n\n Please install the RAM Concept API following the instructions in RAM C -> help -> API -> API Documentation -> getting started. Note: Run the setup.bat file 'as an administrator'.")
        root.destroy()
        quit()

def check_packages():
    missing_packages = []
    with open('scripts/requirements.txt', 'r') as file:
        for line in file:
            package = line.strip().split('==')[0]  # Assumes package names are followed by '==version'
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
    return missing_packages

if __name__ == "__main__":
    missing = check_packages()
    if missing:
        message = "The following external packages are not installed requiredto run this file: \n" + "\n".join(missing) + \
                  "\n\nPlease run the setup.bat file 'as an administrator' from within the T:\\Software Dev\\RAM C API\\scripts folder."
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        from tkinter import messagebox
        messagebox.showerror("Error", message)
        root.destroy()
        quit()

from tkinter import filedialog
import os
from scripts.default_settings import SETTINGS_DEFAULT, SettingsDict
import configparser
import json
from scripts.load_rundown_main import main_centroid_rundown_wrapped, run_click
import configparser
import tkinter as tk
from scripts.txt_settings import load_settings
import json
from tkinter import messagebox
import shutil
from scripts.txt_settings import validate_settings_wrapped
from scripts.yes_no_and_repeat import ask_yes_no_and_to_all
from datetime import datetime

SETTINGS_DEFAULT

def to_json_string(list_of_dicts) -> str:
    """Convert a list of dictionaries to a JSON string."""
    return json.dumps(list_of_dicts)

def from_json_string(json_string) -> list[dict]:
    """Convert a JSON string to a list of dictionaries."""
    if not json_string:
        return []
    return json.loads(json_string)

def to_list_string(list_of_strings) -> str:
    """Convert a list of strings to a string."""
    return str(",".join(list_of_strings))

def from_list_string(string) -> list[str]:
    """Convert a string to a list of strings."""
    if not string:
        return []
    return string.split(",")

root = tk.Tk()
root.title("RAM API GUI")

import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

def wrapped_run_click():

    settings = get_settings_dict()
    # settings['DO_LOADRUNDOWN'] = True
    # settings['DO CENTROIDS'] = False
    if settings:
        run_click(settings)

def wrapped_centroid_rundown():

    settings = get_settings_dict()
    if settings:
        main_centroid_rundown_wrapped(settings)

def wrapped_validate_settings():

    settings = get_settings_dict()
    if settings:

        validate_settings_wrapped(settings)

def _from_index():

    """Find the index of a string in the listbox."""
    _file_properties = from_json_string(files_properties_var.get())
    if not _file_properties:
        return None
    
    string = start_from_var.get()
        
    for file in _file_properties:
        if file['filename'] == string:
            return _file_properties.index(file)

    start_from_var.set(_file_properties[0]['filename'])

    return 0 

def _to_index():

    """Find the index of a string in the listbox."""
    _file_properties = from_json_string(files_properties_var.get())
    if not _file_properties:
        return None
    
    string = end_at_var.get()
        
    for file in _file_properties:
        if file['filename'] == string:
            return _file_properties.index(file)
        
    end_at_var.set(_file_properties[-1]['filename'])

    return len(_file_properties) - 1

def from_to_selected():
    _from = _from_index()
    _to = _to_index()
    
    if _from is not None and _to is not None:
        return min(_from, _to), max(_from, _to)
    
    if _from is not None and _to is None:
        return _from, len(listbox.get(0, tk.END)) - 1
    
    if _from is None and _to is not None:
        return 0, _to
    
    else: 
        return None, None

def update_from_selected():

    selected_index = listbox.curselection()
    
    if not selected_index:
        return
    else:
        selected_index = selected_index[0]
    
    from_index = listbox.curselection()[0]
    to_index = max(from_index,_to_index())

    _files_properties = from_json_string(files_properties_var.get())

    start_from_var.set(_files_properties[from_index]['filename'])
    end_at_var.set(_files_properties[to_index]['filename'])
    update_colors()


def update_to_selected():
    selected_index = listbox.curselection()[0]
    if not selected_index:
        return

    from_index = min(_from_index(),selected_index)
    to_index = selected_index

    _files_properties = from_json_string(files_properties_var.get())
    start_from_var.set(_files_properties[from_index]['filename'])
    end_at_var.set(_files_properties[to_index]['filename'])
    update_colors()

def update_colors():

    _from_index, _to_index =from_to_selected()
    

    for i in range(listbox.size()):

        if _from_index <= i and  (i <= _to_index or _to_index == -1):

            listbox.itemconfig(i, {'bg':'green'})
        else:
            listbox.itemconfig(i, {'bg':'red'})

def add_files():

    is_empty = listbox.size() == 0

    _filepaths = filedialog.askopenfilenames(filetypes=[("RAM Concept Flies", ".cpt")])
    
    if is_empty and not _filepaths:
        return
    
    if not _filepaths:
        return
    
    if is_empty and root_directory_var.get() == '':
        _updated = update_root(path = os.path.dirname(_filepaths[0]))
        if _updated == 'yes_and_load':
            return
    _files_properties = from_json_string(files_properties_var.get())
    current_filesnames = [file['filename'] for file in _files_properties]
    filepaths = [filepath for filepath in _filepaths if os.path.basename(filepath) not in current_filesnames]
    if len(_filepaths) != len(filepaths):
        overlap = [os.path.basename(filepath) for filepath in _filepaths if os.path.basename(filepath) in current_filesnames]
        messagebox.showwarning("WARNING", f"{', '.join(overlap)} files are alreading in list, these have not been added. if you would like to repeat floors, please use the 'Update Typical' tool.")
                               
    for filepath in reversed(filepaths):

        filename = os.path.basename(filepath)

        _files_properties.append({
            "filepath": filepath,
            "filename": filename,
            "typical": 1,
            "listpath": filepath
        })

    if is_empty and _files_properties:
        start_from_var.set(_files_properties[0]['filename'])
        end_at_var.set(_files_properties[-1]['filename'])

    files_properties_var.set(to_json_string(_files_properties))    
    update_list_box()

def update_list_box():

    _files_properties = from_json_string(files_properties_var.get())

    listbox.delete(0, tk.END)
    root_directory = root_directory_var.get()
    recurse = False
    yes_to_all = None
    delete_index = []
    for e,file in enumerate(_files_properties):
        filename = file["filename"]

        if root_directory:
            if os.path.isfile(os.path.join(root_directory,file["filename"])):
                listpath = file["filepath"].replace(root_directory, "root/")
                file['listpath'] = listpath
                listbox.insert(tk.END, f"{filename}, [typical{file['typical']}], {listpath}")

            elif os.path.isfile(file["filepath"]):
                if yes_to_all is None:
                    answer = ask_yes_no_and_to_all(root, file)
                else:
                    answer = ["yes" if yes_to_all else "no"]

                if "yes_to_all" in answer:
                    if "no" in answer:
                        yes_to_all = True
                    if "yes" in answer:
                        yes_to_all = False
    
                if "yes" in answer:
                    shutil.copy2(file["filepath"], root_directory)
                    file["filepath"] = os.path.join(root_directory, filename)
                    listpath =f"root/{filename}"
                    listbox.insert(tk.END, f"{filename}, [typical{file['typical']}], {listpath}")

                elif "no" in answer:
                    delete_index.insert(0,e)
                else:
                    delete_index.insert(0,e)


                    # raise Exception("Should not get here")

                recurse = True
        else:
            filepath = file["filepath"]
            listbox.insert(tk.END, f"{filename}, [typical{file['typical']}], {filepath}")

    for index in delete_index:
        _files_properties.pop(index)
    files_properties_var.set(to_json_string(_files_properties))

    update_colors()

def check_folders():
    path = root_directory_var.get()
        
    if not os.path.isdir(path + '/excel'):
        os.mkdir(path + '/excel')
    if not os.path.isdir(path + '/logs'):
        os.mkdir(path + '/logs')    
    if not os.path.isdir(path + '/backups'):
        os.mkdir(path + '/backups')    

def new_project():
    update_root(path = None,action= "new_project")

def open_project():
    update_root(path = None,action = "open_project")

# def save_inputs_this():
#     save_inputs()

# def save_inputs_as():
#     copy_directories()
#     save_inputs()

def save_project():

    # _root_directory = root_directory_var.get()

    # if not _root_directory:
    #     update_root(path = None, action='save_project_as')
    save_inputs()

def save_project_as():
    _root_directory = root_directory_var.get()
    if not _root_directory:
        messagebox.showerror('Error', "No project open to save.")
        return

    update_root(path = None,action = "save_project_as")

def load_last_saved_project():

    _root_directory = root_directory_var.get()
    
    if not _root_directory:
        return
    load_inputs()

def update_root_path(path):
        root_directory_var.set(path)
        root_box.delete(0, tk.END)
        root_box.insert(0, path)
        check_folders()
        update_list_box()

def update_root(path = None, action = None):
    if not path:
        path = filedialog.askdirectory()
    if not (path is None or path != ''):
        return
    # logging.basicConfig(filename=f'{path}/logs/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # logging.info(f"Root directory set to {path}")

    if not os.path.isfile(path + '/PROJECT_INPUTS.txt'):
        if action in ["new_project", None]:
            update_root_path(path)
            save_inputs()
        else:
            check_folders()
            shutil.copy2(SCRIPT_DIR + '/PROJECT_INPUTS.txt', path)
            return 'check_and_copy'
    else:
        if action  != "new_project":
            update_root_path(path)
            if action == "open_project":
                answer = True
            else:    
                answer = messagebox.askyesno("Warning", "A Project file already exists, would you like to load it?, if not a new one will overide with the current settings")
            if answer:
                load_inputs()
                return 'yes_and_load'
            else:
                if not os.path.isdir(path + '/backups'):
                    os.mkdir(path + '/backups')    
                shutil.copy2(path + '/PROJECT_INPUTS.txt', f"{path}/backups/PROJECT_INPUTS.txt.bak'{datetime.now().strftime('%Y_%m_%d@%H_%M_%S')}")
                save_inputs()
            return
        else:
            messagebox.showerror("Warning", "A Project file already exists, please select a new directory which a new project will be created")
            new_project()


def modify_list(lst, action, index, new_value=None):
    """
    Modify a list by moving an item up, down, or deleting it.

    Parameters:
    - lst: The list to be modified.
    - action: The action to be taken ('up', 'down', 'delete').
    - index: The index of the item to be moved or deleted.

    Returns:
    - Modified list or original list if an error occurs.
    """
    if index is None or not lst:
        return None

    if not 0 <= index < len(lst):
        return None

    if action == "up":
        if index == 0:
            return lst
        lst[index - 1], lst[index] = lst[index], lst[index - 1]

    elif action == "down":
        if index == len(lst) - 1:
            return lst
        lst[index + 1], lst[index] = lst[index], lst[index + 1]

    elif action == "delete":
        del lst[index]
        return lst

    elif action == "delete all":
        lst = []
        return lst

    elif action == "update":
        if new_value is None:
            return lst
        lst[index] = new_value

    else:
        return None


# def update_to_selected():
#     selected_index = listbox.curselection()[0]
#     if not selected_index:
#         return

#     from_index = min(_from_index(),selected_index)
#     to_index = selected_index

#     _files_properties = from_json_string(files_properties_var.get())
#     start_from_var.set(_files_properties[from_index]['filename'])
#     end_at_var.set(_files_properties[to_index]['filename'])
#     update_colors()

def edit_files(action, curser_add = 0):
    _selected_index = listbox.curselection()
    if not _selected_index:
        return
    _selected_index = _selected_index[0]
    _files_properties = from_json_string(files_properties_var.get())
    if _files_properties is None:
        return _selected_index
    modify_list(_files_properties, action, _selected_index)
    files_properties_var.set(to_json_string(_files_properties))
    update_list_box()
    return _selected_index

def move_up():

    old_curser = edit_files("up")
    if old_curser is None:
        return
    listbox.selection_set(max(old_curser-1,0))

def move_down():

    old_curser = edit_files("down")
    if old_curser is None:
        return
    listbox.selection_set(min(old_curser+1,listbox.size()-1))

def remove_file():

    old_cursser = edit_files("delete")

    if old_cursser is None:
        return
    listbox.selection_set(max(old_cursser-1,0))

def remove_all():
    files_properties_var.set(to_json_string([]))
    update_list_box()

def update_typical():

    _entry = entry.get()
    if _entry == '':
        messagebox.showerror("Error", "Please enter a interger value >= 1")
        return
    
    if not _entry.isdigit():
        messagebox.showerror("Error",f"Please enter a interger value >=, not {entry.get()}")
        return

    elif int(_entry) < 1:
        messagebox.showerror("Error",f"Please enter a interger >= 1 value value, not {entry.get()}")
        return

    _selected_index = listbox.curselection()
    if not _selected_index:
        messagebox.showerror("Error", "Please select a file in the list to update")
        return
    _selected_index = _selected_index[0]

    _files_properties = from_json_string(files_properties_var.get())
    if _files_properties is None:
        raise Exception('Should not get here')
    _files_properties[_selected_index]['typical'] =  entry.get()
    files_properties_var.set(to_json_string(_files_properties))
    
    update_list_box()
    # edit_files("update")

# Variables
from_index_var = tk.IntVar(value=0)
to_index_var = tk.IntVar(value = -1)
files_properties_var = tk.StringVar()
llr_plans_var = tk.StringVar(value=to_list_string(SETTINGS_DEFAULT["LLR_PLANS"]))
llur_plans_var = tk.StringVar(value=to_list_string(SETTINGS_DEFAULT["LLUR_PLANS"]))
file_var = tk.StringVar()
root_directory_var = tk.StringVar()
start_from_var = tk.StringVar()
end_at_var = tk.StringVar()
reinforced_concrete_density_var = tk.DoubleVar(value=SETTINGS_DEFAULT["REINFORCED_CONCRETE_DENSITY"])
drawing_scale_var = tk.DoubleVar(value=SETTINGS_DEFAULT["DRAWING_SCALE_1_TO"])
# wall_group_var = tk.BooleanVar(value=SETTINGS_DEFAULT["WALL_GROUP"])
attempt_restart_var = tk.BooleanVar(value=SETTINGS_DEFAULT["ATEMPT_RESTART_IF_ERROR"])
max_attempts_var = tk.IntVar(value=SETTINGS_DEFAULT["MAX_ATTEMPTS_IF_ERRORS_RAISED"])
exit_code_var = tk.IntVar(value=SETTINGS_DEFAULT["EXIT_CODE_AFTER_X_SECONDS"])
generate_mesh_var = tk.BooleanVar(value=SETTINGS_DEFAULT["GENERATE_MESH"])
debug_var = tk.BooleanVar(value=SETTINGS_DEFAULT["DEBUG"])
transfer_dead_var = tk.StringVar(value=SETTINGS_DEFAULT["TRANSFER_DEAD"])
transfer_ll_reducible_var = tk.StringVar(value=SETTINGS_DEFAULT["TRANSFER_LL_REDUCIBLE"])
transfer_ll_unreducible_var = tk.StringVar(value=SETTINGS_DEFAULT["TRANSFER_LL_UNREDUCIBLE"])
ll_unreducible_var = tk.StringVar(value=SETTINGS_DEFAULT["LL_UNREDUCIBLE"])
all_dead_lc_var = tk.StringVar(value=SETTINGS_DEFAULT["ALL_DEAD_LC"])

all_live_load_lc_var = tk.StringVar(value=SETTINGS_DEFAULT["ALL_LIVE_LOADS_LC"])
do_load_rundown_var = tk.BooleanVar(value=SETTINGS_DEFAULT['DO_LOAD_RUNDOWN'])
do_centroid_calcs_var = tk.BooleanVar(value=SETTINGS_DEFAULT['DO_CENTROID_CALCS'])
update_column_stiffness_calcs_var = tk.BooleanVar(value=SETTINGS_DEFAULT['UPDATE_COLUMN_STIFNESS_CALCS'])
max_column_stiffness_ratio_var = tk.DoubleVar(value=SETTINGS_DEFAULT["MAX_COLUMN_STIFFNESS_RATIO"])
min_column_stiffness_ratio_var = tk.DoubleVar(value=SETTINGS_DEFAULT["MIN_COLUMN_STIFFNESS_RATIO"])
eq_factors_dl_var = tk.DoubleVar(value = SETTINGS_DEFAULT['EQ_FACTORS_DL'])
eq_factors_llr_var = tk.DoubleVar(value = SETTINGS_DEFAULT['EQ_FACTORS_LLR'])
eq_factors_llur_var = tk.DoubleVar(value = SETTINGS_DEFAULT['EQ_FACTORS_LLUR'])
create_backup_files_var = tk.BooleanVar(value = SETTINGS_DEFAULT['CREATE_BACKUP_FILES'])
llr_add_var = tk.StringVar()
llur_add_var = tk.StringVar()

def copy_directories():
    _root_directory = root_directory_var.get()
    if _root_directory == '':
        messagebox.showerror("Error", "Please select a root directory to save the inputs to C://Windows is not a valid directory")
        return
    _files_properties = from_json_string(files_properties_var.get())
    if _files_properties is None:
        return
    for file in _files_properties:
        if os.path.isfile(file['filepath']):
            shutil.copy2(file['filepath'], _root_directory)
    messagebox.showinfo("Information", f"Files copied successfully to {_root_directory}")

def save_inputs():

    
    settings = get_settings_dict()
    
    files = settings["FILES"]

    _root_directory = root_directory_var.get()

    if not _root_directory:
        messagebox.showerror('Error', "No project open to save.")
        return

    _files = [file['filename'] for file in from_json_string(files_properties_var.get())]
    _typical = [f"{str(file['filename'])}:{file['typical']}" for file in from_json_string(files_properties_var.get()) if str(file['typical']) != "1"]
    _filepaths = [f"{str(file['filename'])}:{file['filepath']}" for file in from_json_string(files_properties_var.get()) if (not _root_directory or _root_directory not in str(file['filepath']))]

    files_str = '' if not _files else ','.join(_files)
    filepaths_str = '' if not _filepaths else ','.join(_filepaths)
    typical_str = '' if not _typical else ','.join(_typical)

    config = configparser.ConfigParser()

    # Adding the inputs
    config['PROJECT_INPUTS'] = {
        'FILES': files_str,
        'TYPICAL': typical_str , # Convert to int
        # 'FILEPATHS': filepaths_str,
        # 'ROOT_DIRECTORY': root_directory_var.get(),
        'START_FROM_LEVEL_OR_INDEX': str(from_index_var.get()), # Convert to int
        'END_AT_LEVEL_OR_INDEX': str(to_index_var.get()) # Convert to int``
    }
    
    # Adding the settings
    config['SETTINGS'] = {
        'REINFORCED_CONCRETE_DENSITY': str(reinforced_concrete_density_var.get()),
        'DRAWING_SCALE_1_TO': str(drawing_scale_var.get()),
        # 'WALL_GROUP': str(wall_group_var.get()),
        'ATEMPT_RESTART_IF_ERROR': str(attempt_restart_var.get()),
        'MAX_ATTEMPTS_IF_ERRORS_RAISED': str(max_attempts_var.get()),
        'EXIT_CODE_AFTER_X_SECONDS': str(exit_code_var.get()), 
        'GENERATE_MESH': str(generate_mesh_var.get()),
        'DEBUG': str(debug_var.get()),
        'MAX_COLUMN_STIFFNESS_RATIO': str(max_column_stiffness_ratio_var.get()),
        'MIN_COLUMN_STIFFNESS_RATIO': str(min_column_stiffness_ratio_var.get()),
    }

    # Adding the loadings names
    config['LOADINGS NAMES'] = {
        'TRANSFER_DEAD': transfer_dead_var.get(),
        'TRANSFER_LL_REDUCIBLE': transfer_ll_reducible_var.get(),
        'TRANSFER_LL_UNREDUCIBLE': transfer_ll_unreducible_var.get(),
        'LL_UNREDUCIBLE': transfer_ll_unreducible_var.get(),
        'LLR_PLANS': llr_plans_var.get(),
        'LLUR_PLANS': llur_plans_var.get()
    }

    # Adding the load combination names
    config['LOAD COMBINATION NAMES'] = {
        'ALL_DEAD_LC': all_dead_lc_var.get(),
        'ALL_LIVE_LOADS_LC': all_live_load_lc_var.get(),

    }

    # Adding the loadings names
    config['EQ COMBO FACTORS'] = {
        'EQ_FACTORS_DL': eq_factors_dl_var.get(),
        'EQ_FACTORS_LLR': eq_factors_llr_var.get(),
        'EQ_FACTORS_LLUR': eq_factors_llur_var.get()
    }

    config['RUN CALCS'] = {
        'DO_LOAD_RUNDOWN': do_load_rundown_var.get(),

        'DO_CENTROID_CALCS': do_centroid_calcs_var.get(),
        'UPDATE_COLUMN_STIFNESS_CALCS': update_column_stiffness_calcs_var.get()

    }

    # if _root_directory == '':
    #     _root_directory = os.getcwd()

        # if 'c:\\windows' in _root_directory.lower() or 'c:/windows' in _root_directory.lower():
        #     messagebox.showerror("Error", "Please select a root directory to save the inputs to C://Windows is not a valid directory")
        #     return
        # update_root(path = _root_directory)
        
    filepath = _root_directory + '/PROJECT_INPUTS.txt'

    if filepath:
        with open(filepath, 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("Information", f"Inputs saved successfully at {filepath}")

# from scripts.log_window_wrapper import log_window_wrapper


def load_inputs():

    # settings_filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    settings_filename = "PROJECT_INPUTS.txt"
    _root_directory = root_directory_var.get()
    if _root_directory == '':
        settings_filename = "PROJECT_INPUTS.txt"

    else:
        settings_filename = _root_directory + '/PROJECT_INPUTS.txt'

    if settings_filename:
        settings = load_settings(settings_filename, SETTINGS_DEFAULT)
        # Now, update your tkinter variables here based on the data in settings
        files_properties_var.set(to_json_string(settings["FILES"]))
        llr_plans_var.set(to_list_string(settings["LLR_PLANS"]))
        llur_plans_var.set(to_list_string(settings["LLUR_PLANS"]))
        # wall_group_var.set(settings["WALL_GROUP"])
        attempt_restart_var.set(settings["ATEMPT_RESTART_IF_ERROR"])
        reinforced_concrete_density_var.set(settings["REINFORCED_CONCRETE_DENSITY"])
        drawing_scale_var.set(settings["DRAWING_SCALE_1_TO"])
        max_attempts_var.set(settings["MAX_ATTEMPTS_IF_ERRORS_RAISED"])
        generate_mesh_var.set(settings["GENERATE_MESH"])
        debug_var.set(settings["DEBUG"])
        transfer_dead_var.set(settings["TRANSFER_DEAD"])
        transfer_ll_reducible_var.set(settings["TRANSFER_LL_REDUCIBLE"])
        transfer_ll_unreducible_var.set(settings["TRANSFER_LL_UNREDUCIBLE"])
        ll_unreducible_var.set(settings["TRANSFER_LL_UNREDUCIBLE"])
        all_dead_lc_var.set(settings["ALL_DEAD_LC"])
        all_live_load_lc_var.set(settings["ALL_LIVE_LOADS_LC"])
        exit_code_var.set(settings['EXIT_CODE_AFTER_X_SECONDS'])
        root_directory_var.set(settings['ROOT_DIRECTORY']) 
        end_at_var.set(settings['END_AT_LEVEL_OR_INDEX'])
        do_load_rundown_var.set(settings['DO_LOAD_RUNDOWN'])
        do_centroid_calcs_var.set(settings['DO_CENTROID_CALCS'])
        update_column_stiffness_calcs_var.set(settings['UPDATE_COLUMN_STIFNESS_CALCS'])
        max_column_stiffness_ratio_var.set(settings['MAX_COLUMN_STIFFNESS_RATIO']),
        min_column_stiffness_ratio_var.set(settings['MIN_COLUMN_STIFFNESS_RATIO']),
        eq_factors_dl_var.set(settings['EQ_FACTORS_DL'])
        eq_factors_llr_var.set(settings['EQ_FACTORS_LLR'])
        eq_factors_llur_var.set(settings['EQ_FACTORS_LLUR'])

        update_list_box()
        update_llr_listbox()
        update_llur_listbox()
        # validate_settings_wrapped(settings)
        # ... and so on for all other variables
        messagebox.showinfo("Information", "Inputs loaded successfully")

def reset_inputs():

    settings = SETTINGS_DEFAULT
    # Now, update your tkinter variables here based on the data in settings
    # wall_group_var.set(settings["WALL_GROUP"])
    attempt_restart_var.set(settings["ATEMPT_RESTART_IF_ERROR"])
    reinforced_concrete_density_var.set(settings["REINFORCED_CONCRETE_DENSITY"])
    drawing_scale_var.set(settings["DRAWING_SCALE_1_TO"])
    max_attempts_var.set(settings["MAX_ATTEMPTS_IF_ERRORS_RAISED"])
    generate_mesh_var.set(settings["GENERATE_MESH"])
    debug_var.set(settings["DEBUG"])
    transfer_dead_var.set(settings["TRANSFER_DEAD"])
    transfer_ll_reducible_var.set(settings["TRANSFER_LL_REDUCIBLE"])
    transfer_ll_unreducible_var.set(settings["TRANSFER_LL_UNREDUCIBLE"])
    ll_unreducible_var.set(settings["LL_UNREDUCIBLE"])
    all_dead_lc_var.set(settings["ALL_DEAD_LC"])
    all_live_load_lc_var.set(settings["ALL_LIVE_LOADS_LC"])
    exit_code_var.set(settings['EXIT_CODE_AFTER_X_SECONDS'])
    do_load_rundown_var.set(settings['DO_LOAD_RUNDOWN'])
    do_centroid_calcs_var.set(settings['DO_CENTROID_CALCS'])
    update_column_stiffness_calcs_var.set(settings['UPDATE_COLUMN_STIFNESS_CALCS'])
    max_column_stiffness_ratio_var.set(settings['MAX_COLUMN_STIFFNESS_RATIO']),
    min_column_stiffness_ratio_var.set(settings['MIN_COLUMN_STIFFNESS_RATIO']),
    llr_plans_var.set(to_list_string(settings["LLR_PLANS"]))
    llur_plans_var.set(to_list_string(settings["LLUR_PLANS"]))
    eq_factors_dl_var.set(settings['EQ_FACTORS_DL'])
    eq_factors_llr_var.set(settings['EQ_FACTORS_LLR'])
    eq_factors_llur_var.set(settings['EQ_FACTORS_LLUR'])
    create_backup_files_var.set(settings['CREATE_BACKUP_FILES'])
    update_llr_listbox()
    update_llur_listbox()

def get_settings_dict() -> SettingsDict:
    # Initial data fetching

    def safe_get_number(var,default):
        try:
            var.get()
            
        except:
            var.set(default)
            
        finally:
            return var.get()

    settings = {
        "REINFORCED_CONCRETE_DENSITY": safe_get_number(reinforced_concrete_density_var,SETTINGS_DEFAULT['REINFORCED_CONCRETE_DENSITY']),
        "DRAWING_SCALE_1_TO": safe_get_number(drawing_scale_var,SETTINGS_DEFAULT['DRAWING_SCALE_1_TO']),
        # "WALL_GROUP": wall_group_var.get(),
        "FILES": from_json_string(files_properties_var.get()),
        "START_FROM_LEVEL_OR_INDEX": start_from_var.get().split('.cpt')[0],
        "END_AT_LEVEL_OR_INDEX": end_at_var.get().split('.cpt')[0],
        "MAX_ATTEMPTS_IF_ERRORS_RAISED": safe_get_number(max_attempts_var,SETTINGS_DEFAULT["MAX_ATTEMPTS_IF_ERRORS_RAISED"]),
        "EXIT_CODE_AFTER_X_SECONDS": safe_get_number(exit_code_var,SETTINGS_DEFAULT["EXIT_CODE_AFTER_X_SECONDS"]),
        "ATEMPT_RESTART_IF_ERROR": attempt_restart_var.get(),
        "ALL_DEAD_LC": all_dead_lc_var.get(),   
        "ALL_LIVE_LOADS_LC": all_live_load_lc_var.get(),   
        "TRANSFER_DEAD": transfer_dead_var.get(),
        "TRANSFER_LL_REDUCIBLE": transfer_ll_reducible_var.get(),
        "TRANSFER_LL_UNREDUCIBLE": transfer_ll_unreducible_var.get(),
        "LL_UNREDUCIBLE": ll_unreducible_var.get(),
        "GENERATE_MESH": generate_mesh_var.get(),
        "DEBUG": debug_var.get(),
        "ROOT_DIRECTORY": root_directory_var.get(),
        "DO_LOAD_RUNDOWN": do_load_rundown_var.get(),
        "DO_CENTROID_CALCS": do_centroid_calcs_var.get(),
        "UPDATE_COLUMN_STIFNESS_CALCS": update_column_stiffness_calcs_var.get(),
        "MAX_COLUMN_STIFFNESS_RATIO": max_column_stiffness_ratio_var.get(),
        "MIN_COLUMN_STIFFNESS_RATIO": min_column_stiffness_ratio_var.get(),
        "EQ_FACTORS_DL": safe_get_number(eq_factors_dl_var,SETTINGS_DEFAULT['EQ_FACTORS_DL']),
        "EQ_FACTORS_LLR": safe_get_number(eq_factors_llr_var,SETTINGS_DEFAULT['EQ_FACTORS_LLR']),
        "EQ_FACTORS_LLUR": safe_get_number(eq_factors_llur_var,SETTINGS_DEFAULT['EQ_FACTORS_LLUR']),
        "CREATE_BACKUP_FILES": create_backup_files_var.get(),
        "LLR_PLANS": from_list_string(llr_plans_var.get()),
        "LLUR_PLANS": from_list_string(llur_plans_var.get()),
    }

    return settings

def add_LLR():
    if not llr_add_var.get():
        return
    _llr_plans_var = from_list_string(llr_plans_var.get())
    _llr_plans_var.append(llr_add_var.get())
    llr_plans_var.set(to_list_string(_llr_plans_var))
    update_llr_listbox()

def remove_LLR():
    curselection = llr_listbox.curselection()

    if not curselection:
        return
    
    _llr_plans_var = from_list_string(llr_plans_var.get())
    _llr_plans_var.pop(curselection[0])
    llr_plans_var.set(to_list_string(_llr_plans_var))

    update_llr_listbox()

def add_LLUR():
    if not llur_add_var.get():
        return
    _llur_plans_var = from_list_string(llur_plans_var.get())
    _llur_plans_var.append(llur_add_var.get())
    llur_plans_var.set(to_list_string(_llur_plans_var))
    update_llur_listbox()

def remove_LLUR():

    curselection = llur_listbox.curselection()

    if not curselection:
        return
    
    _llur_plans_var = from_list_string(llur_plans_var.get())
    _llur_plans_var.pop(curselection[0])
    llur_plans_var.set(to_list_string(_llur_plans_var))
    update_llur_listbox()

def update_llr_listbox():
    _llr_plans_var = from_list_string(llr_plans_var.get())
    llr_listbox.delete(0, tk.END)
    
    for plan in _llr_plans_var:
        llr_listbox.insert(tk.END, plan)

def update_llur_listbox():
    _llur_plans_var = from_list_string(llur_plans_var.get())
    llur_listbox.delete(0, tk.END)
    
    for plan in _llur_plans_var:
        llur_listbox.insert(tk.END, plan)

UPDATE_VARS  = False

frame_kwargs = dict(pady=5, padx=5, width=100, border=0)

label_kwargs = dict(padx=1, pady=2)
entry_kwargs = dict()
double_entry_kwargs = dict(width=5)

grid_kwargs = dict(pady=2, sticky='w')

left_tk_frame = tk.LabelFrame(root, border=0, padx=5)
left_tk_frame.grid(row=0, column=0,sticky='ns')

mid_tk_frame = tk.LabelFrame(root, border=0,)
mid_tk_frame.grid(row=0, column=1,sticky='ns')

right_tk_frame = tk.LabelFrame(root, border=0)
right_tk_frame.grid(row=0, column=2,sticky='ns')

settings_frame = tk.LabelFrame(left_tk_frame, text='SETTINGS', **frame_kwargs)
settings_frame.grid(row=0, column=0, **grid_kwargs)

############ LEFT FRAME ############

# Add widgets to the mesh settings frame
tk.Label(settings_frame, text="Reinforced Concrete Density (kN/m3)", **label_kwargs).grid(row=0, column=0, **grid_kwargs)
tk.Entry(settings_frame,textvariable=reinforced_concrete_density_var,**double_entry_kwargs, **entry_kwargs).grid(row=0, column=1, **grid_kwargs)

tk.Label(settings_frame, text="PDF Drawing Scale 1:?", **label_kwargs).grid(row=1, column=0, **grid_kwargs)
tk.Entry(settings_frame, textvariable=drawing_scale_var,**double_entry_kwargs, **entry_kwargs).grid(row=1, column=1, **grid_kwargs)

tk.Label(settings_frame, text="MAX Column Stiffness Ratio", **label_kwargs).grid(row=2, column=0, **grid_kwargs)
tk.Entry(settings_frame, textvariable=max_column_stiffness_ratio_var, **double_entry_kwargs,**entry_kwargs).grid(row=2, column=1, **grid_kwargs)

tk.Label(settings_frame, text="MIN Column Stiffness Ratio", **label_kwargs).grid(row=3, column=0, **grid_kwargs)
tk.Entry(settings_frame, textvariable=min_column_stiffness_ratio_var, **double_entry_kwargs,**entry_kwargs).grid(row=3, column=1, **grid_kwargs)

tk.Label(settings_frame, text="Generate Mesh", **label_kwargs).grid(row=4, column=0, **grid_kwargs)
tk.Checkbutton(settings_frame, variable=generate_mesh_var, **entry_kwargs).grid(row=4, column=1, **grid_kwargs)

# tk.Label(settings_frame, text="Wall Group", **label_kwargs).grid(row=5, column=0, **grid_kwargs)
# tk.Checkbutton(settings_frame, variable=wall_group_var, **entry_kwargs).grid(row=5, column=1, **grid_kwargs)

tk.Label(settings_frame, text="Create Backup Files", **label_kwargs).grid(row=6, column=0, **grid_kwargs)
tk.Checkbutton(settings_frame, variable=create_backup_files_var, **entry_kwargs).grid(row=6, column=1, **grid_kwargs)

loadings_frame = tk.LabelFrame(left_tk_frame, text='RAM C LOADING NAMES', **frame_kwargs)
loadings_frame.grid(row=1, column=0, **grid_kwargs)

tk.Label(loadings_frame, text="Transfer Dead", **label_kwargs).grid(row=0, column=0, **grid_kwargs)
tk.Entry(loadings_frame, textvariable=transfer_dead_var, **entry_kwargs).grid(row=0, column=1, **grid_kwargs)

tk.Label(loadings_frame, text="Transfer LL Reducible", **label_kwargs).grid(row=1, column=0, **grid_kwargs)
tk.Entry(loadings_frame, textvariable=transfer_ll_reducible_var, **entry_kwargs).grid(row=1, column=1, **grid_kwargs)

tk.Label(loadings_frame, text="LL Reducible PLANS", **label_kwargs).grid(row=2, column=0, **grid_kwargs)
llr_listbox = tk.Listbox(loadings_frame, width=20, height=8)
llr_listbox.grid(row=2, column=1,rowspan=4, sticky='w',pady=10)

# Create a frame for the update typical functionality
add_llr_btn = tk.Button(loadings_frame, text="Add LLR Load Plan", command=add_LLR)
add_llr_btn.grid(row=3, column=0, pady=0, sticky='w')

add_llr_entry = tk.Entry(loadings_frame,textvariable=llr_add_var, **entry_kwargs)
add_llr_entry.grid(row=4, column=0, pady=0, sticky='w')
remove_llr_button = tk.Button(loadings_frame, text="Remove Selected", command=remove_LLR)
remove_llr_button.grid(row=5, column=0,pady=0, sticky='w')

# tk.Label(loadings_frame, text="Template Includes LL Unreducible", **label_kwargs).grid(row=6, column=0, **grid_kwargs)
# tk.Checkbutton(loadings_frame, variable=template_has_llur_var, **entry_kwargs).grid(row=6, column=1, **grid_kwargs)

tk.Label(loadings_frame, text="Transfer LL Unreducible", **label_kwargs).grid(row=7, column=0, **grid_kwargs)
tk.Entry(loadings_frame, textvariable=transfer_ll_unreducible_var, **entry_kwargs).grid(row=7, column=1, **grid_kwargs)

tk.Label(loadings_frame, text="LL Unreducible PLANS", **label_kwargs).grid(row=8, column=0, **grid_kwargs)
llur_listbox = tk.Listbox(loadings_frame, width=20, height=8)
llur_listbox.grid(row=8, column=1,rowspan=4, sticky='w',pady=10)

# Create a frame for the update typical functionality
add_llur_btn = tk.Button(loadings_frame, text="Add LLUR Load Plan", command=add_LLUR)
add_llur_btn.grid(row=9, column=0, pady=0, sticky='w')

add_llur_entry = tk.Entry(loadings_frame,textvariable=llur_add_var, **entry_kwargs)
add_llur_entry.grid(row=10, column=0, pady=0, sticky='w')
remove_llur_button = tk.Button(loadings_frame, text="Remove Selected", command=remove_LLUR)
remove_llur_button.grid(row=11, column=0,pady=0, sticky='w')

# tk.Label(loadings_frame, text="LL Unreducible", **label_kwargs).grid(row=9, column=0, **grid_kwargs)
# tk.Entry(loadings_frame, textvariable=ll_unreducible_var, **entry_kwargs).grid(row=9, column=1, **grid_kwargs)

load_combinations_frame = tk.LabelFrame(left_tk_frame, text='RAM C LOAD COMBINATION NAMES', **frame_kwargs)
load_combinations_frame.grid(row=2, column=0, **grid_kwargs)

tk.Label(load_combinations_frame, text="All Dead LC", **label_kwargs).grid(row=0, column=0, **grid_kwargs)
tk.Entry(load_combinations_frame, textvariable=all_dead_lc_var, **entry_kwargs).grid(row=0, column=1, **grid_kwargs)

tk.Label(load_combinations_frame, text="All Live Load LC", **label_kwargs).grid(row=1, column=0, **grid_kwargs)
tk.Entry(load_combinations_frame, textvariable = all_live_load_lc_var, **entry_kwargs).grid(row=1, column=1, **grid_kwargs)

############ MID FRAME ###########

# Create a frame for the update typical functionality
frame_files = tk.LabelFrame(mid_tk_frame, text='LEVEL FILES', **frame_kwargs)
frame_files.grid(row=0, column=0, **grid_kwargs)


listbox = tk.Listbox(frame_files, width=50, height=30)
listbox.grid(row=0, column=1, **grid_kwargs)

save_files = tk.LabelFrame(mid_tk_frame, text='SAVE/LOAD FILES', **frame_kwargs)
save_files.grid(row=1, column=0, **grid_kwargs)

# Add save button
tk.Button(save_files, text="New Project", command=new_project).grid(row=0, column=0, **grid_kwargs)
tk.Button(save_files, text="Open Project", command=open_project).grid(row=0, column=1, **grid_kwargs)
tk.Button(save_files, text="Save Project", command=save_project).grid(row=0, column=2, **grid_kwargs)
tk.Button(save_files, text="Save Project As", command=save_project_as).grid(row=1, column=0, **grid_kwargs)
tk.Button(save_files, text="Load Last Saved", command=load_inputs).grid(row=1, column=1, **grid_kwargs)
tk.Button(save_files, text="Reset To Default Inputs", command=reset_inputs).grid(row=1, column=2, **grid_kwargs)

root_files = tk.LabelFrame(mid_tk_frame, text='PROJECT FOLDER', **frame_kwargs)

root_files.grid(row=2, column=0, **grid_kwargs)

# Create a listbox with a wider width
root_box = tk.Listbox(root_files, width=50, height=1)
root_box.grid(row=0, column=0, **grid_kwargs)

############ RIGHT FRAME ############
# Create a frame for the buttons
frame_buttons = tk.LabelFrame(right_tk_frame, text=' ', **frame_kwargs)
frame_buttons.grid(row=0, column=2, **grid_kwargs)

# Create buttons and associate them with the functions
btn_add = tk.Button(frame_buttons, text="Add Files", command=add_files)
btn_add.grid(row=0, column=0, **grid_kwargs)

btn_up = tk.Button(frame_buttons, text="Move Up", command=move_up)
btn_up.grid(row=1, column=0, **grid_kwargs)

btn_down = tk.Button(frame_buttons, text="Move Down", command=move_down)
btn_down.grid(row=2, column=0, **grid_kwargs)

btn_remove = tk.Button(frame_buttons, text="Remove Selected", command=remove_file)
btn_remove.grid(row=3, column=0, **grid_kwargs)

btn_remove = tk.Button(frame_buttons, text="Remove All", command=remove_all)
btn_remove.grid(row=4, column=0, **grid_kwargs)

# Create a frame for the update typical functionality
frame_update = tk.LabelFrame(right_tk_frame, text='SELECT FLOORS', **frame_kwargs)
frame_update.grid(row=1, column=2, **grid_kwargs)

btn_from_selected = tk.Button(frame_update, text="From Selected", command=update_from_selected)
btn_from_selected.grid(row=4, column=0, **grid_kwargs)

btn_to_selected = tk.Button(frame_update, text="To Selected", command=update_to_selected)
btn_to_selected.grid(row=5, column=0, **grid_kwargs)

update_typical_frame = tk.LabelFrame(right_tk_frame, text='TYPICAL FLOORS COUNT', **frame_kwargs)
update_typical_frame.grid(row=2, column=2, **grid_kwargs)

# Create a button to update the typical value
btn_update_typical = tk.Button(update_typical_frame, text="Update Typical", command=update_typical)
btn_update_typical.grid(row=3, column=0, **grid_kwargs)

# Create an entry widget to input the typical value
entry = tk.Entry(update_typical_frame,double_entry_kwargs, **entry_kwargs)
entry.grid(row=3, column=1, **grid_kwargs)

eq_combo_factors = tk.LabelFrame(right_tk_frame, text='EQ COMBINATION FACTORS', **frame_kwargs)
eq_combo_factors.grid(row=3, column=2, **grid_kwargs)

tk.Label(eq_combo_factors, text="Dead Load", **label_kwargs).grid(row=0, column=0, **grid_kwargs)
tk.Entry(eq_combo_factors, textvariable=eq_factors_dl_var, **double_entry_kwargs, **entry_kwargs).grid(row=0, column=1, **grid_kwargs)

tk.Label(eq_combo_factors, text="Live Load Reducible", **label_kwargs).grid(row=1, column=0, **grid_kwargs)
tk.Entry(eq_combo_factors, textvariable=eq_factors_llr_var, **double_entry_kwargs, **entry_kwargs).grid(row=1, column=1, **grid_kwargs)

tk.Label(eq_combo_factors, text="Live Load Unreducible", **label_kwargs).grid(row=2, column=0, **grid_kwargs)
tk.Entry(eq_combo_factors, textvariable=eq_factors_llur_var, **double_entry_kwargs, **entry_kwargs).grid(row=2, column=1, **grid_kwargs)

error_handling_frame = tk.LabelFrame(right_tk_frame, text='ERROR HANDLING', **frame_kwargs)
error_handling_frame.grid(row=4, column=2, **grid_kwargs)

tk.Label(error_handling_frame, text="Max Attempts if Errors Raised", **label_kwargs).grid(row=0, column=0, **grid_kwargs)
tk.Entry(error_handling_frame, textvariable=max_attempts_var,**double_entry_kwargs, **entry_kwargs).grid(row=0, column=1, **grid_kwargs)

tk.Label(error_handling_frame, text="Exit Code After X Seconds", **label_kwargs).grid(row=1, column=0, **grid_kwargs)
tk.Entry(error_handling_frame, textvariable=exit_code_var,**double_entry_kwargs, **entry_kwargs).grid(row=1, column=1, **grid_kwargs)

tk.Label(error_handling_frame, text="Debug", **label_kwargs).grid(row=3, column=0, **grid_kwargs)
tk.Checkbutton(error_handling_frame, variable=debug_var, **entry_kwargs).grid(row=3, column=1, **grid_kwargs)

run_files = tk.LabelFrame(right_tk_frame, text='RUN FILES', **frame_kwargs)
run_files.grid(row=5, column=2, **grid_kwargs)

# Add save button
tk.Label(run_files, text="Do Load Rundown", **label_kwargs).grid(row=0, column=0, **grid_kwargs)
tk.Checkbutton(run_files, variable=do_load_rundown_var, **entry_kwargs).grid(row=0, column=1, **grid_kwargs)

tk.Label(run_files, text="Do Centroid Calcs", **label_kwargs).grid(row=2, column=0, **grid_kwargs)
tk.Checkbutton(run_files, variable=do_centroid_calcs_var, **entry_kwargs).grid(row=2, column=1, **grid_kwargs)

tk.Label(run_files, text="Update Col I Factor", **label_kwargs).grid(row=3, column=0, **grid_kwargs)
tk.Checkbutton(run_files, variable=update_column_stiffness_calcs_var, **entry_kwargs).grid(row=3, column=1, **grid_kwargs)

tk.Button(run_files, text="Run Calcs", command=wrapped_run_click).grid(row=4, column=0, **grid_kwargs)
tk.Button(run_files, text="Validate Inputs", command=wrapped_validate_settings).grid(row=5, column=0, **grid_kwargs)

listbox.bind('<Delete>', lambda e: remove_file())
listbox.bind('<Control-Up>', lambda e: move_up())
listbox.bind('<Control-Down>', lambda e: move_down())
root.resizable(False, False)  # Disable resizing (width, height)

if __name__ == "__main__":
    update_vars = True
    update_llr_listbox()
    update_llur_listbox()
    root.mainloop()