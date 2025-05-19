import flet as ft

def create_main_view(page: ft.Page, state):
    page.title = "SubFix"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    def run_all_clicked(e):
        page.dialog = ft.AlertDialog(title=ft.Text("Running..."), content=ft.Text("Your subtitles are being processed."))
        page.dialog.open = True
        page.update()

    # STEP 1: File input
    file_list = ft.ListView(expand=True, spacing=10, height=120)

    add_files_button = ft.ElevatedButton("Add Files", icon="upload_file")
    add_folder_button = ft.ElevatedButton("Add Folder", icon="folder")
    clear_button = ft.TextButton("Clear", icon="clear")

    file_controls = ft.Row([add_files_button, add_folder_button, clear_button], spacing=10)

    step1 = ft.Column([
        ft.Text("STEP 1: Add files or folders", size=20, weight=ft.FontWeight.BOLD),
        file_list,
        file_controls
    ], spacing=10)

    # STEP 2: Operation toggles
    operations = ft.Column([
        ft.Text("STEP 2: Choose operations", size=20, weight=ft.FontWeight.BOLD),
        ft.Checkbox(label="Spellcheck", value=False),
        ft.Checkbox(label="Remove SDH", value=False),
        ft.Checkbox(label="Adjust Timings", value=False)
    ], spacing=8)

    # STEP 3: Settings
    timing_inputs = ft.Column([
        ft.Text("STEP 3: Timing & Formatting Settings", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Text("Min duration (s):"), ft.TextField(value=str(state["timing"]["min_duration"]), width=100),
            ft.Text("Max duration (s):"), ft.TextField(value=str(state["timing"]["max_duration"]), width=100),
        ]),
        ft.Row([
            ft.Text("Gap between (s):"), ft.TextField(value=str(state["timing"]["gap_between"]), width=100),
            ft.Text("Chars/sec:"), ft.TextField(value=str(state["timing"]["chars_per_sec"]), width=100),
        ]),
        ft.Row([
            ft.Text("Chars/line:"), ft.TextField(value=str(state["formatting"]["chars_per_line"]), width=100),
            ft.Text("Max lines:"), ft.TextField(value=str(state["formatting"]["max_lines"]), width=100),
        ]),
    ], spacing=8)

    # STEP 4: Output folder
    output_path = ft.TextField(label="Output Folder", value="output", expand=True)

    step4 = ft.Column([
        ft.Text("STEP 4: Choose output folder", size=20, weight=ft.FontWeight.BOLD),
        output_path
    ], spacing=10)

    progress = ft.ProgressBar(width=600)

    run_button = ft.ElevatedButton("Run All", icon="play_arrow", on_click=run_all_clicked)

    layout = ft.Column([
        ft.Text("SubFix", size=32, weight=ft.FontWeight.W_600),
        ft.Divider(),
        step1,
        operations,
        timing_inputs,
        step4,
        progress,
        ft.Row([run_button], alignment=ft.MainAxisAlignment.END)
    ], spacing=20)

    page.add(layout)

