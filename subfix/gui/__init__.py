import os
from .layout import create_main_window
from .events import handle_event
from .state import load_settings, initial_button_states
import PySimpleGUI as sg

def launch_gui():
    settings = load_settings()
    state = {
        "settings": settings,
        "files": [],
        "buttons": initial_button_states()
    }

    window = create_main_window(settings)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "-ADD_FILES-":
            new_files = sg.popup_get_file("Select subtitle files", multiple_files=True, file_types=(("SRT Files", "*.srt"),))
            if new_files:
                state["files"].extend(new_files.split(";"))
                window["-FILELIST-"].update(state["files"])
        

        result = handle_event(event, values, state, window)
        if result.get("exit"):
            break

    window.close()