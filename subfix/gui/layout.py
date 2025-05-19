import PySimpleGUI as sg

def file_list_section():
    return [
        [sg.Text("Files to Process:")],
        [sg.Multiline("", key="-FILEDROP-", enable_events=True, visible=False, size=(1, 1)),
         sg.Listbox(values=[], size=(60, 6), key="-FILELIST-", enable_events=True)],
        [sg.Button("Add Files"), sg.Button("Add Folder"), sg.Button("Clear")]
    ]

def operation_buttons_section():
    return [
        [sg.Button("Spellcheck", size=(15, 1), key="-SPELLCHECK-")],
        [sg.Button("Remove SDH", size=(15, 1), key="-REMOVE_SDH-"),
         sg.Button("Adjust Timings", size=(15, 1), key="-ADJUST_TIMINGS-")]
    ]

def operation_settings_section(settings):
    return [
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

def output_folder_section():
    return [sg.Text("Output Folder:"), sg.Input("output", key="-OUTFOLDER-"), sg.FolderBrowse()]

def create_main_window(settings):
    sg.theme(settings.get("theme", "DarkGrey5"))
    layout = [
        [sg.Text("SubFix", font=('Helvetica', 20))],
        [sg.HorizontalSeparator()],
        *file_list_section(),
        [sg.Text("Operations:")],
        *operation_buttons_section(),
        *operation_settings_section(settings),
        output_folder_section(),
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key="-PROGRESS-")],
        [sg.StatusBar("Ready to process files", key="-STATUS-")],
        [sg.Button("Run All", size=10), sg.Button("Theme", size=10), sg.Button("Exit", size=10)]
    ]
    return sg.Window("SubFix", layout)