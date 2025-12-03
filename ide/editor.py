# File: ide/editor.py
"""
Code editor widget with line numbers for NovaLang IDE
"""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QTextFormat, QColor, QFont, QTextCursor

from syntax_highlighter import NovaLangHighlighter
from themes import get_theme


class LineNumberArea(QWidget):
    """Widget to display line numbers alongside the editor"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditorWithLineNumbers(QPlainTextEdit):
    """
    Enhanced code editor with line numbers, syntax highlighting,
    and error line highlighting
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up editor properties
        self.setFont(QFont(
            "Consolas" if QFont("Consolas").exactMatch() else "Courier New", 
            11
        ))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        
        # Line number colors (will be updated by theme)
        self.line_number_bg_color = QColor(37, 37, 38)
        self.line_number_fg_color = QColor(133, 133, 133)
        
        # Error tracking
        self.error_line = -1
        
        # Create line number area
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Initialize
        self.update_line_number_area_width(0)
        self.highlighter = NovaLangHighlighter(self.document())
        self.highlight_current_line()
        self.apply_dark_theme()

    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = len(str(max(1, self.blockCount())))
        return 15 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        """Update the editor margins to accommodate line numbers"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update the line number area when scrolling or content changes"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), 
                self.line_number_area.width(), 
                rect.height()
            )

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), 
            self.line_number_area_width(), 
            cr.height()
        )

    def highlight_current_line(self):
        """Highlight the current line and any error lines"""
        extra_selections = []
        
        # Error line gets priority and should be more visible
        if self.error_line != -1:
            error_selection = QTextEdit.ExtraSelection()
            # Bright red background for error line
            error_selection.format.setBackground(QColor(220, 50, 47, 180))
            error_selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            block = self.document().findBlockByNumber(self.error_line - 1)
            if block.isValid():
                cursor = QTextCursor(block)
                cursor.clearSelection()
                error_selection.cursor = cursor
                extra_selections.append(error_selection)
        
        # Current line highlight (only if it's not the error line)
        if not self.isReadOnly():
            current_line = self.textCursor().blockNumber()
            if current_line != self.error_line - 1:
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(QColor(40, 40, 50))
                selection.format.setProperty(
                    QTextFormat.Property.FullWidthSelection, True
                )
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()
                extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)

    def highlight_error_line(self, line_num):
        """
        Highlight a specific line as an error
        
        Args:
            line_num: Line number to highlight (1-indexed)
        """
        self.error_line = line_num
        self.highlight_current_line()
        
        # Scroll to error line
        block = self.document().findBlockByNumber(line_num - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
        
        # Update line number area to show red marker
        self.line_number_area.update()

    def clear_error_highlighting(self):
        """Clear any error line highlighting"""
        self.error_line = -1
        self.highlight_current_line()
        self.line_number_area.update()

    def line_number_area_paint_event(self, event):
        """Paint line numbers in the line number area"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), self.line_number_bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()
        ).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                # Highlight error line number in red
                if block_number + 1 == self.error_line:
                    # Draw red background for error line number
                    painter.fillRect(
                        0, int(top), 
                        self.line_number_area.width(), 
                        self.fontMetrics().height(), 
                        QColor(220, 50, 47)
                    )
                    painter.setPen(QColor(255, 255, 255))  # White text
                    painter.drawText(
                        0, int(top), 
                        self.line_number_area.width() - 8,
                        self.fontMetrics().height(),
                        Qt.AlignmentFlag.AlignRight, 
                        f"✗ {number}"
                    )
                else:
                    painter.setPen(self.line_number_fg_color)
                    painter.drawText(
                        0, int(top), 
                        self.line_number_area.width() - 8,
                        self.fontMetrics().height(),
                        Qt.AlignmentFlag.AlignRight, 
                        number
                    )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def apply_dark_theme(self):
        """Apply dark theme to the editor"""
        theme = get_theme("dark")
        
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                selection-background-color: {theme['selection']};
                border: none;
            }}
        """)
        
        self.line_number_bg_color = QColor(theme['line_numbers']['background'])
        self.line_number_fg_color = QColor(theme['line_numbers']['foreground'])
        
        self.highlighter.set_theme_colors(theme['tokens'])
        self.highlighter.rehighlight()
        self.line_number_area.update()

    def apply_light_theme(self):
        """Apply light theme to the editor"""
        theme = get_theme("light")
        
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                selection-background-color: {theme['selection']};
                border: none;
            }}
        """)
        
        self.line_number_bg_color = QColor(theme['line_numbers']['background'])
        self.line_number_fg_color = QColor(theme['line_numbers']['foreground'])
        
        self.highlighter.set_theme_colors(theme['tokens'])
        self.highlighter.rehighlight()
        self.line_number_area.update()

    def get_text(self):
        """Get all text from the editor"""
        return self.toPlainText()

    def set_text(self, text):
        """
        Set text in the editor
        
        Args:
            text: The text to set
        """
        self.setPlainText(text)
        self.document().setModified(False)