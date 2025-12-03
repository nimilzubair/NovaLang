# File: ide/syntax_highlighter.py
"""
Syntax highlighter for NovaLang
"""

from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QColor, QFont
from PyQt6.QtCore import QRegularExpression


class NovaLangHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for NovaLang programming language"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        self.theme_colors = {}
        
        # Set default colors (will be overridden by theme)
        from themes import get_theme
        theme = get_theme("dark")
        self.set_theme_colors(theme['tokens'])
        self.setup_rules()

    def set_theme_colors(self, colors):
        """
        Set colors for syntax highlighting from theme
        
        Args:
            colors: Dictionary mapping token types to color values
        """
        self.theme_colors = {}
        for key, value in colors.items():
            if isinstance(value, str):
                # Convert hex string to QColor
                self.theme_colors[key] = QColor(value)
            else:
                # Assume it's already a QColor
                self.theme_colors[key] = value
        self.setup_rules()

    def setup_rules(self):
        """Setup highlighting rules with current theme colors"""
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QBrush(self.theme_colors["keyword"]))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            'start', 'end', 'show', 'take', 'when', 'elsewhen', 
            'else', 'loop', 'break', 'func', 'back', 'num', 
            'text', 'flag', 'true', 'false', 'to'
        ]
        
        for keyword in keywords:
            pattern = QRegularExpression(r"\b" + keyword + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QBrush(self.theme_colors["number"]))
        self.highlighting_rules.append(
            (QRegularExpression(r"\b[0-9]+\b"), number_format)
        )

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QBrush(self.theme_colors["string"]))
        self.highlighting_rules.append(
            (QRegularExpression(r'"[^"]*"'), string_format)
        )

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QBrush(self.theme_colors["comment"]))
        self.highlighting_rules.append(
            (QRegularExpression(r'#.*'), comment_format)
        )

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QBrush(self.theme_colors["operator"]))
        
        operators = [
            r'\+', r'-', r'\*', r'/', r'=', r'==', 
            r'!=', r'>', r'<', r'>=', r'<='
        ]
        
        for op in operators:
            pattern = QRegularExpression(op)
            self.highlighting_rules.append((pattern, operator_format))

        # Functions (identifiers followed by parentheses)
        function_format = QTextCharFormat()
        function_format.setForeground(QBrush(self.theme_colors["function"]))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b[A-Za-z_][A-Za-z0-9_]*\s*(?=\()'), function_format)
        )

    def highlightBlock(self, text):
        """
        Apply syntax highlighting to a block of text
        
        Args:
            text: The text block to highlight
        """
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(), 
                    match.capturedLength(), 
                    fmt
                )