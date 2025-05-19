DEFAULT_SETTINGS = {
    "theme": "DarkGrey5",
    "translation": {
        "target_lang": "es"
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

import json

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def initial_button_states():
    return {
        "-SPELLCHECK-": False,
        "-REMOVE_SDH-": False,
        "-ADJUST_TIMINGS-": False
    }