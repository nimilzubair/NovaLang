# File: ide/themes.py
"""
Theme configurations for NovaLang IDE
"""

def get_theme(theme_name="dark"):
    """
    Get theme configuration
    
    Args:
        theme_name: 'dark' or 'light'
    
    Returns:
        Dictionary containing theme colors
    """
    if theme_name == "dark":
        return {
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
            'selection': '#264f78',
            'line_numbers': {
                'background': '#252526',
                'foreground': '#858585'
            },
            'tokens': {
                'keyword': '#569cd6',
                'number': '#b5cea8',
                'string': '#ce9178',
                'comment': '#6a9955',
                'operator': '#d4d4d4',
                'identifier': '#9cdcfe',
                'function': '#dcdcaa'
            }
        }
    else:  # light theme
        return {
            'background': '#ffffff',
            'foreground': '#000000',
            'selection': '#add6ff',
            'line_numbers': {
                'background': '#f3f3f3',
                'foreground': '#237893'
            },
            'tokens': {
                'keyword': '#0000ff',
                'number': '#098658',
                'string': '#a31515',
                'comment': '#008000',
                'operator': '#000000',
                'identifier': '#001080',
                'function': '#795e26'
            }
        }