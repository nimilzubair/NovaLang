# File: ide/editor.py
"""
Code editor widget with syntax highlighting for NovaLang IDE
"""
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QTextFormat, QColor, QFont, QSyntaxHighlighter

from .syntax_highlighter import NovaLangHighlighter

class LineNumberArea(QWidget):
    """Widget to display line numbers"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return self.editor.line_number_area_width()
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced code editor with line numbers and syntax highlighting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up editor properties
        self.setFont(QFont("Consolas" if QFont("Consolas").exactMatch() else "Courier New", 11))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        
        # Create line number area
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Initialize line number area
        self.update_line_number_area_width(0)
        
        # Apply syntax highlighting
        self.highlighter = NovaLangHighlighter(self.document())
        
        # Highlight current line
        self.highlight_current_line()
        
        # Set theme (dark by default)
        self.apply_theme("dark")
    
    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = max(3, len(str(max(1, self.blockCount()))))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, new_block_count):
        """Update the editor margins to accommodate line numbers"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update the line number area"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                        self.line_number_area.width(), 
                                        rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(),
                  self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), self.line_number_bg_color)
        
        # Get the first visible block
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        # Draw line numbers for visible blocks
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.line_number_fg_color)
                painter.drawText(
                    0, int(top),
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlight_current_line(self):
        """Highlight the current line"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(30, 30, 40)  # Dark blue-gray
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def apply_theme(self, theme_name):
        """Apply a color theme to the editor"""
        from .themes import get_theme
        
        theme = get_theme(theme_name)
        
        # Set background and text colors
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                selection-background-color: {theme['selection']};
                border: 1px solid #555;
            }}
        """)
        
        # Set line number colors
        self.line_number_bg_color = QColor(theme['line_numbers']['background'])
        self.line_number_fg_color = QColor(theme['line_numbers']['foreground'])
        
        # Update the highlighter colors
        self.highlighter.set_theme_colors(theme['tokens'])
        self.highlighter.rehighlight()
        
        # Force repaint
        self.line_number_area.update()
    
    def get_text(self):
        """Get editor text"""
        return self.toPlainText()
    
    def set_text(self, text):
        """Set editor text"""
        self.setPlainText(text)
        self.document().setModified(False)
    
    def is_modified(self):
        """Check if document has been modified"""
        return self.document().isModified()
    
    def set_modified(self, modified):
        """Set document modified flag"""
        self.document().setModified(modified)