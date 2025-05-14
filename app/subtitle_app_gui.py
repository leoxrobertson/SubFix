import PySimpleGUI as sg
import os
from pathlib import Path
import json
# from processors.translator import translate_srt  # Commented out translation import
from processors.spellchecker import spellcheck_srt
from processors.sdh_cleaner import remove_hi_tags
from processors.timing_editor import adjust_timings
import re
from datetime import datetime, timedelta
from spellchecker import SpellChecker
import re

# ========================
#      CONFIGURATION
# ========================
DEFAULT_SETTINGS = {
    "theme": "DarkBlue3",
    "translation": {
        "target_lang": "es"  # Commented out translation settings
    },
    "timing": {
        "min_duration": 0.6,
        "max_duration": 8.0,
        "gap_between": 0.066,
        "chars_per_sec": 25
    },
    "formatting": {
        "chars_per_line": 43,
        "max_lines": 2
    }
}

# ========================
#        GUI SETUP
# ========================
def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def create_window(settings):
    # Set a black-and-white theme
    sg.theme("DarkGrey5")  # Predefined black-and-white theme

    # Layout components
    file_list = [
        [sg.Text("Files to Process:")],
        [sg.Multiline("", key="-FILEDROP-", enable_events=True, visible=False, size=(1, 1)),
         sg.Listbox(values=[], size=(60, 6), key="-FILELIST-", enable_events=True)],
        [sg.Button("Add Files"), sg.Button("Add Folder"), sg.Button("Clear")]
    ]
    
    operation_buttons = [
        [sg.Button("Spellcheck", size=(15, 1), key="-SPELLCHECK-")],
        [sg.Button("Remove SDH", size=(15, 1), key="-REMOVE_SDH-"),
         sg.Button("Adjust Timings", size=(15, 1), key="-ADJUST_TIMINGS-")]
    ]
    
    operation_settings = [
        [sg.Frame("Timing Settings", [
            [sg.T("Min duration (s):"), sg.Input(settings["timing"]["min_duration"], key="-MIN_DUR-", size=6),
             sg.T("Max duration (s):"), sg.Input(settings["timing"]["max_duration"], key="-MAX_DUR-", size=6)],
            [sg.T("Gap between (s):"), sg.Input(settings["timing"]["gap_between"], key="-GAP-", size=6),
             sg.T("Chars/sec:"), sg.Input(settings["timing"]["chars_per_sec"], key="-CPS-", size=6)]
        ])],

        [sg.Frame("Formatting", [
            [sg.T("Chars/line:"), sg.Input(settings["formatting"]["chars_per_line"], key="-CPL-", size=6),
             sg.T("Max lines:"), sg.Input(settings["formatting"]["max_lines"], key="-MAX_LINES-", size=6)]
        ])]
    ]
    
    # Main layout
    layout = [
        [sg.Text("Subtitle Toolkit", font=('Helvetica', 20))],
        [sg.HorizontalSeparator()],
        
        [sg.Column(file_list)],
        [sg.Text("Operations:")],
        [sg.Column(operation_buttons)],
        [sg.Column(operation_settings)],
        
        [sg.Text("Output Folder:"), 
         sg.Input("output", key="-OUTFOLDER-"), 
         sg.FolderBrowse()],
         
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key="-PROGRESS-")],
        [sg.StatusBar("Ready to process files", key="-STATUS-")],
        
        [sg.Button("Run All", size=10), 
         sg.Button("Theme", size=10),
         sg.Button("Exit", size=10)]
    ]
    
    return sg.Window("Subtitle Toolkit", layout)

# ========================
#      MAIN APP LOGIC
# ========================
def main():
    settings = load_settings()
    window = create_window(settings)
    files_to_process = []
    
    # Track button states (True = "on", False = "off")
    button_states = {
        "-SPELLCHECK-": False,
        "-REMOVE_SDH-": False,
        "-ADJUST_TIMINGS-": False
    }
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break
            
        elif event == "Theme":
            settings["theme"] = "DarkBlue3" if settings["theme"] == "SystemDefault" else "SystemDefault"
            save_settings(settings)
            sg.popup("Theme changed", "Please restart the application")
            break
            
        elif event == "Add Files":
            new_files = sg.popup_get_file("Select subtitle files", multiple_files=True, file_types=(("SRT Files", "*.srt"),))
            if new_files:
                files_to_process.extend(new_files.split(";"))
                window["-FILELIST-"].update(files_to_process)
                
        elif event == "Add Folder":
            folder = sg.popup_get_folder("Select folder with SRT files")
            if folder:
                new_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.srt')]
                files_to_process.extend(new_files)
                window["-FILELIST-"].update(files_to_process)
                
        elif event == "Clear":
            files_to_process = []
            window["-FILELIST-"].update(files_to_process)
            # Reset button states
            for key in button_states:
                button_states[key] = False
                window[key].update(button_color=("white", sg.theme_button_color_background()))
            
        elif event in button_states:
            # Toggle button state
            button_states[event] = not button_states[event]
            
            # Update button appearance
            if button_states[event]:
                window[event].update(button_color=("white", "green"))  # "On" state
            else:
                window[event].update(button_color=("white", sg.theme_button_color_background()))  # "Off" state
            
        elif event == "-FILEDROP-":
            # Handle drag-and-drop of files
            dropped_files = values["-FILEDROP-"].split(";")
            for file in dropped_files:
                if file.lower().endswith(".srt"):  # Only add .srt files
                    files_to_process.append(file)
            window["-FILELIST-"].update(files_to_process)
            
        elif event == "Run All":
            if not files_to_process:
                sg.popup_error("No files selected!")
                continue
            
            # Update settings from UI
            settings["timing"] = {
                "min_duration": float(values["-MIN_DUR-"]),
                "max_duration": float(values["-MAX_DUR-"]),
                "gap_between": float(values["-GAP-"]),
                "chars_per_sec": float(values["-CPS-"])
            }
            settings["formatting"] = {
                "chars_per_line": int(values["-CPL-"]),
                "max_lines": int(values["-MAX_LINES-"])
            }
            save_settings(settings)
            
            # Process files
            out_folder = values["-OUTFOLDER-"]
            os.makedirs(out_folder, exist_ok=True)
            
            total_files = len(files_to_process)
            for i, infile in enumerate(files_to_process):
                try:
                    window["-STATUS-"].update(f"Processing {i+1}/{total_files}: {Path(infile).name}")
                    window["-PROGRESS-"].update((i+1)/total_files * 100)
                    
                    original_name = Path(infile).stem
                    outfile = os.path.join(out_folder, f"{original_name}_processed.srt")
                    
                    # Apply selected operations
                    if button_states["-SPELLCHECK-"]:
                        spellcheck_srt(infile, outfile)
                    if button_states["-REMOVE_SDH-"]:
                        remove_hi_tags(infile, outfile)
                    if button_states["-ADJUST_TIMINGS-"]:
                        adjust_timings(
                            infile, outfile,
                            min_duration=settings["timing"]["min_duration"],
                            max_duration=settings["timing"]["max_duration"],
                            min_gap=settings["timing"]["gap_between"],
                            chars_per_sec=settings["timing"]["chars_per_sec"],
                            chars_per_line=settings["formatting"]["chars_per_line"],
                            max_lines=settings["formatting"]["max_lines"]
                        )
                        
                except Exception as e:
                    sg.popup_error(f"Failed to process {Path(infile).name}:\n{str(e)}")
                    continue
                    
            window["-STATUS-"].update(f"Done! Processed {total_files} files")
            sg.popup("Batch complete", f"Processed {total_files} files\nSaved to: {out_folder}")
            window["-PROGRESS-"].update(0)
            
    window.close()

if __name__ == "__main__":
    main()

