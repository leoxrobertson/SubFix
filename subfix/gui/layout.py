import PySimpleGUI as sg
from types import SimpleNamespace

THEMESETTINGS = SimpleNamespace(
    Large_header=("Helvetica", 32),
    Section_header=("Helvetica", 18, "bold"),
    Label=("Helvetica", 16), 
    Fat_label=("Helvetica", 16, "bold")
)

def file_list_section():
    return [
        [sg.Listbox(values=[], size=(80, 5), key="-FILELIST-", enable_events=True)],
        [sg.Multiline("", key="-FILEDROP-", enable_events=True, visible=False, size=(1, 1))],
        [sg.Button(
                "Add File(s)",
                key="-ADD_FILES-",
                size=(14, 1.1),
                font=("Segoe UI", 16, "bold"),
                border_width=0
                ),
         sg.Button("Clear",
                size=(14, 1.1),
                font=("Segoe UI", 16),
                border_width=1, 
                button_color=("white", "#1D1D24"),
                )
        ]
    ]

def operation_buttons_section():
    return [
        [sg.Checkbox("Spellcheck", font=THEMESETTINGS.Label, size=(20, 1), default=False, key="-SPELLCHECK-")], 
        [sg.Checkbox("Remove SDH", font=THEMESETTINGS.Label, size=(20, 1), default=False, key="-REMOVE_SDH-")],
        [sg.Checkbox("Adjust Timings", font=THEMESETTINGS.Label, size=(20, 1), default=False, key="-ADJUST_TIMINGS-")]
    ]

def operation_settings_section(settings):
    return [
        [sg.Text("")],
        [sg.Text("Timing Settings", font=THEMESETTINGS.Fat_label)],
        [sg.T("Min duration [s]", font=THEMESETTINGS.Label), sg.Input(settings["timing"]["min_duration"], key="-MIN_DUR-", size=(8,10), font=("Segoe UI", 14), pad=(8, 8), background_color="#3E4046", border_width=0, tooltip="Minimum duration a subtitle should stay on screen (in seconds)"),
         sg.T("Max duration [s]", font=THEMESETTINGS.Label), sg.Input(settings["timing"]["max_duration"], key="-MAX_DUR-", size=(8,1), font=("Segoe UI", 14), pad=(8, 8), background_color="#3E4046", border_width=0, tooltip="Maximum duration a subtitle should stay on screen (in seconds)")],
        
        [sg.T("Gap between [s]", font=THEMESETTINGS.Label), sg.Input(settings["timing"]["gap_between"], key="-GAP-", size=(8,), font=("Segoe UI", 14), pad=(8, 8), background_color="#3E4046", border_width=0, tooltip="Minimum duration a subtitle should stay on screen (in seconds)"),
         sg.T("Chars/sec       ", font=THEMESETTINGS.Label), sg.Input(settings["timing"]["chars_per_sec"], key="-CPS-", size=(8,), font=("Segoe UI", 14), pad=(8, 8), background_color="#3E4046", border_width=0, tooltip="Minimum duration a subtitle should stay on screen (in seconds)")
        ],
        [sg.Text("")],
        [sg.Text("Formatting", font=THEMESETTINGS.Fat_label)],
        [sg.T("Chars / line    ", font=THEMESETTINGS.Label), sg.Input(settings["formatting"]["chars_per_line"], key="-CPL-", size=(8,), font=("Segoe UI", 14), pad=(8, 8), background_color="#3E4046", border_width=0, tooltip="Minimum duration a subtitle should stay on screen (in seconds)"),
         sg.T("Max lines       ", font=THEMESETTINGS.Label), sg.Input(settings["formatting"]["max_lines"], key="-MAX_LINES-", size=(8,), font=("Segoe UI", 14), pad=(8, 8), background_color="#3E4046", border_width=0, tooltip="Minimum duration a subtitle should stay on screen (in seconds)")]
    ]
    

def output_folder_section():
    return [
        [sg.T("Current output folder", font=THEMESETTINGS.Label), sg.Input("Output", key="-OUTFOLDER-", size=(8,100), font=("Segoe UI", 16, "bold"), pad=(8, 8), background_color="#3E4046", border_width=0)], 
        [sg.FolderBrowse("Choose another output folder",
            size=(24, 1.1),
                font=("Segoe UI", 16, "bold")
        )]
    ]

def create_main_window(settings):
    sg.theme(settings.get("theme", "DarkGrey13"))
    
    layout = [
        [sg.Text("")],
        [sg.Text("1️⃣ Add file(s)", font=THEMESETTINGS.Section_header)],
        *file_list_section(),
        [sg.Text("")],
        [sg.Text("_" * 100, text_color="gray")],
        [sg.Text("")],
        [sg.Text("2️⃣ Choose operations", font=THEMESETTINGS.Section_header)],
        *operation_buttons_section(),
        [sg.Text("")],
        [sg.Text("_" * 100, text_color="gray")],
        [sg.Text("")],
        [sg.Text("3️⃣ Choose Operation Settings", font=THEMESETTINGS.Section_header)], 
        *operation_settings_section(settings),
        [sg.Text("")],
        [sg.Text("_" * 100, text_color="gray")],
        [sg.Text("")],
        [sg.Text("4️⃣ Set output folder", font=THEMESETTINGS.Section_header)],
        *output_folder_section(),
        [sg.Text("")],
        [sg.Text("_" * 100, text_color="gray")],
        [sg.Text("")],
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key="-PROGRESS-")],
        [sg.StatusBar("Ready to process files", key="-STATUS-")],
        [sg.Button(
            "Run All",
            size=(15, 1.2),
            font=("Segoe UI", 14, "bold"),
            button_color=("white", "#3f51b5"),
            border_width=0
        )]
            ]
    scrollable_layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(550, 700))]]
    return sg.Window("SubFix", scrollable_layout, resizable=True)