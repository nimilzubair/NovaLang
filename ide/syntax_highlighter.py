# File: ide/syntax_highlighter.py (updated)
"""
Syntax highlighter for NovaLang
"""
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QBrush
from PyQt6.QtCore import QRegularExpression

class NovaLangHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        self.theme_colors = {}
        
        # Set default theme (dark) - Use QColor objects instead of strings
        self.set_theme_colors({
            "keyword": QColor(86, 156, 214),    # Blue
            "number": QColor(181, 206, 168),    # Green
            "string": QColor(206, 145, 120),    # Orange
            "comment": QColor(106, 153, 85),    # Gray-green
            "operator": QColor(220, 220, 170),  # Yellow
            "identifier": QColor(156, 220, 254), # Light blue
            "function": QColor(220, 220, 170)   # Yellow
        })
        
        self.setup_rules()
    
    def set_theme_colors(self, colors):
        """Set colors for syntax highlighting from theme"""
        # Convert string colors to QColor objects if needed
        self.theme_colors = {}
        for key, value in colors.items():
            if isinstance(value, str):
                # Convert hex string to QColor
                self.theme_colors[key] = QColor(value)
            else:
                # Assume it's already a QColor or compatible
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
            rule = (pattern, keyword_format)
            self.highlighting_rules.append(rule)
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QBrush(self.theme_colors["number"]))
        number_rule = (QRegularExpression(r"\b[0-9]+\b"), number_format)
        self.highlighting_rules.append(number_rule)
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QBrush(self.theme_colors["string"]))
        string_rule = (QRegularExpression(r'"[^"]*"'), string_format)
        self.highlighting_rules.append(string_rule)
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QBrush(self.theme_colors["comment"]))
        comment_rule = (QRegularExpression(r'#.*'), comment_format)
        self.highlighting_rules.append(comment_rule)
        
        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QBrush(self.theme_colors["operator"]))
        operators = [
            r'\+', r'-', r'\*', r'/', r'=', r'==', r'!=',
            r'>', r'<', r'>=', r'<='
        ]
        for op in operators:
            pattern = QRegularExpression(op)
            rule = (pattern, operator_format)
            self.highlighting_rules.append(rule)
        
        # Functions (identifiers followed by parentheses)
        function_format = QTextCharFormat()
        function_format.setForeground(QBrush(self.theme_colors["function"]))
        function_rule = (QRegularExpression(r'\b[A-Za-z_][A-Za-z0-9_]*\s*(?=\()'), function_format)
        self.highlighting_rules.append(function_rule)
        
        # Parentheses and braces
        paren_format = QTextCharFormat()
        paren_format.setForeground(QBrush(self.theme_colors["operator"]))
        parens = [r'\(', r'\)', r'\{', r'\}', r'\[', r'\]', r',']
        for paren in parens:
            pattern = QRegularExpression(paren)
            rule = (pattern, paren_format)
            self.highlighting_rules.append(rule)
        
        # Identifier (last rule so it doesn't interfere with keywords)
        identifier_format = QTextCharFormat()
        identifier_format.setForeground(QBrush(self.theme_colors["identifier"]))
        identifier_rule = (QRegularExpression(r'\b[A-Za-z_][A-Za-z0-9_]*\b'), identifier_format)
        self.highlighting_rules.append(identifier_rule)
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), 
                             match.capturedLength(), fmt)