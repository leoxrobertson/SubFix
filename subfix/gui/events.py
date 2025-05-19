import os
from pathlib import Path
import PySimpleGUI as sg
from subfix.processors.spellchecker import spellcheck_srt
from subfix.processors.sdh_cleaner import remove_hi_tags
from subfix.processors.timing_editor import adjust_timings
from .state import save_settings

def handle_event(event, values, state, window):
    files_to_process = state["files"]
    button_states = state["buttons"]
    settings = state["settings"]

    if event == "Exit":
        return {"exit": True}

    elif event == "Theme":
        settings["theme"] = "DarkBlue3" if settings["theme"] == "SystemDefault" else "SystemDefault"
        save_settings(settings)
        sg.popup("Theme changed", "Please restart the application")
        return {"exit": True}

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
        files_to_process.clear()
        window["-FILELIST-"].update([])
        for key in button_states:
            button_states[key] = False
            window[key].update(button_color=("white", sg.theme_button_color_background()))

    elif event in button_states:
        button_states[event] = not button_states[event]
        color = "green" if button_states[event] else sg.theme_button_color_background()
        window[event].update(button_color=("white", color))

    elif event == "-FILEDROP-":
        dropped = values["-FILEDROP-"].split(";")
        files_to_process.extend([f for f in dropped if f.endswith(".srt")])
        window["-FILELIST-"].update(files_to_process)

    elif event == "Run All":
        if not files_to_process:
            sg.popup_error("No files selected!")
            return {}

        update_settings_from_ui(values, settings)
        save_settings(settings)

        out_folder = values["-OUTFOLDER-"]
        os.makedirs(out_folder, exist_ok=True)

        total = len(files_to_process)
        for i, infile in enumerate(files_to_process):
            try:
                window["-STATUS-"].update(f"Processing {i+1}/{total}: {Path(infile).name}")
                window["-PROGRESS-"].update((i+1)/total * 100)
                original = Path(infile).stem
                outfile = os.path.join(out_folder, f"{original}_processed.srt")

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

        window["-STATUS-"].update(f"Done! Processed {total} files")
        sg.popup("Batch complete", f"Processed {total} files\nSaved to: {out_folder}")
        window["-PROGRESS-"].update(0)

    return {}

def update_settings_from_ui(values, settings):
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