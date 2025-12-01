# File: themes.py
"""
Theme definitions for NovaLang IDE
"""

THEMES = {
    "dark": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "selection": "#264f78",
        "line_numbers": {
            "background": "#252526",
            "foreground": "#858585"
        },
        "tokens": {
            "keyword": "#569cd6",
            "number": "#b5cea8",
            "string": "#ce9178",
            "comment": "#6a9955",
            "operator": "#dcdcaa",
            "identifier": "#9cdcfe",
            "function": "#dcdcaa"
        }
    },
    "light": {
        "background": "#ffffff",
        "foreground": "#000000",
        "selection": "#c8e1ff",
        "line_numbers": {
            "background": "#f0f0f0",
            "foreground": "#333333"
        },
        "tokens": {
            "keyword": "#0000ff",
            "number": "#098658",
            "string": "#a31515",
            "comment": "#008000",
            "operator": "#000000",
            "identifier": "#001080",
            "function": "#795e26"
        }
    },
    "monokai": {
        "background": "#272822",
        "foreground": "#f8f8f2",
        "selection": "#49483e",
        "line_numbers": {
            "background": "#272822",
            "foreground": "#8f908a"
        },
        "tokens": {
            "keyword": "#f92672",
            "number": "#ae81ff",
            "string": "#e6db74",
            "comment": "#75715e",
            "operator": "#f8f8f2",
            "identifier": "#66d9ef",
            "function": "#a6e22e"
        }
    }
}

def get_theme(name):
    """Get theme by name, returns dark theme if not found"""
    return THEMES.get(name, THEMES["dark"])