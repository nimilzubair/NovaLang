# File: ide/novalang_ide.py (complete fix)
"""
NovaLang IDE - PyQt6 Version
"""
import sys
import os
from ide.themes import get_theme
from ide.syntax_highlighter import NovaLangHighlighter
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QSplitter, QStatusBar, 
                             QToolBar, QFileDialog, QMessageBox, QPlainTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QTextCursor, QColor, QPalette, QPainter, QTextFormat

from nova_lang.lexer import Lexer, LexerError
from nova_lang.parser import Parser, ParserError
from nova_lang.semantic import SemanticAnalyzer, SemanticError

class CompilationThread(QThread):
    """Thread for running compilation to avoid freezing UI"""
    compilation_done = pyqtSignal(str, bool)  # message, success
    
    def __init__(self, code):
        super().__init__()
        self.code = code
    
    def run(self):
        try:
            # Lexical analysis
            lexer = Lexer(self.code)
            tokens = list(lexer.generate_tokens())
            
            # Parsing
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Semantic analysis
            sem = SemanticAnalyzer()
            sem.analyze(ast)
            
            self.compilation_done.emit("Compilation successful!", True)
        except LexerError as e:
            self.compilation_done.emit(f"Lexer Error: {str(e)}", False)
        except ParserError as e:
            self.compilation_done.emit(f"Parser Error: {str(e)}", False)
        except SemanticError as e:
            self.compilation_done.emit(f"Semantic Error: {str(e)}", False)
        except Exception as e:
            self.compilation_done.emit(f"Unexpected Error: {str(e)}", False)

class CodeEditorWithLineNumbers(QPlainTextEdit):
    """Code editor with line numbers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas" if QFont("Consolas").exactMatch() else "Courier New", 11))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        
        # Initialize color variables
        self.line_number_bg_color = QColor(53, 53, 53)  # Default dark
        self.line_number_fg_color = QColor(200, 200, 200)  # Default light gray
        # Line number area
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Initial setup
        self.update_line_number_area_width(0)
        
        # Apply syntax highlighting
        self.highlighter = NovaLangHighlighter(self.document())
        
        self.highlight_current_line()
        
        # Apply dark theme by default
        self.apply_dark_theme()

    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
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
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), 
                                         self.line_number_area_width(), cr.height())
        
    def highlight_current_line(self):
        """Highlight the current line"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()  # Use QTextEdit instead
            line_color = QColor(40, 40, 50)
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)    

    def apply_dark_theme(self):
        """Apply dark theme to editor"""
        from ide.themes import get_theme
        theme = get_theme("dark")
        
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                selection-background-color: {theme['selection']};
                border: none;
            }}
        """)
        
        # Set line number colors
        self.line_number_bg_color = QColor(theme['line_numbers']['background'])
        self.line_number_fg_color = QColor(theme['line_numbers']['foreground'])
        
        # Update the highlighter with theme colors
        self.highlighter.set_theme_colors(theme['tokens'])
        self.highlighter.rehighlight()
        
        # Update line number area
        self.line_number_area.update()
    
    def apply_light_theme(self):
        """Apply light theme to editor"""
        from ide.themes import get_theme
        theme = get_theme("light")
        
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                selection-background-color: {theme['selection']};
                border: none;
            }}
        """)
        
        # Set line number colors
        self.line_number_bg_color = QColor(theme['line_numbers']['background'])
        self.line_number_fg_color = QColor(theme['line_numbers']['foreground'])
        
        # Update the highlighter with theme colors
        self.highlighter.set_theme_colors(theme['tokens'])
        self.highlighter.rehighlight()
        
        # Update line number area
        self.line_number_area.update()
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), self.line_number_bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.line_number_fg_color)
                painter.drawText(0, int(top), 
                               self.line_number_area.width() - 5,
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def get_text(self):
        """Get editor text"""
        return self.toPlainText()
    
    def set_text(self, text):
        """Set editor text"""
        self.setPlainText(text)
        self.document().setModified(False)

class LineNumberArea(QWidget):
    """Widget to display line numbers"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return self.editor.line_number_area_width()
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class NovaLangIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaLang IDE")
        self.setGeometry(100, 100, 1200, 700)
        
        self.current_file = None
        
        self.init_ui()
        self.create_actions()
        self.create_menu()
        self.create_toolbar()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Load sample code
        self.load_sample_code()
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter for editor and output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Editor widget
        self.editor = CodeEditorWithLineNumbers()
        
        # Output widget
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas" if QFont("Consolas").exactMatch() else "Courier New", 10))
        
        # Add widgets to splitter
        splitter.addWidget(self.editor)
        splitter.addWidget(self.output_text)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_actions(self):
        # File actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction("Save &As", self)
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.compile_action = QAction("&Compile", self)
        self.compile_action.setShortcut("F5")
        self.compile_action.triggered.connect(self.compile_code)
        
        # View actions
        self.light_theme_action = QAction("&Light Theme", self)
        self.light_theme_action.triggered.connect(self.apply_light_theme)
        
        self.dark_theme_action = QAction("&Dark Theme", self)
        self.dark_theme_action.triggered.connect(self.apply_dark_theme)
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.compile_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.light_theme_action)
        view_menu.addAction(self.dark_theme_action)
    
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.compile_action)
    
    def new_file(self):
        """Create a new file"""
        if self.check_save():
            self.editor.set_text("")
            self.current_file = None
            self.setWindowTitle("NovaLang IDE - Untitled")
            self.status_bar.showMessage("New file created", 3000)
    
    def open_file(self):
        """Open a file"""
        if self.check_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open NovaLang File", "", 
                "NovaLang Files (*.nova);;All Files (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.editor.set_text(content)
                    self.current_file = file_path
                    self.setWindowTitle(f"NovaLang IDE - {os.path.basename(file_path)}")
                    self.status_bar.showMessage(f"Opened: {file_path}", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", 
                                       f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file is None:
            return self.save_file_as()
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.editor.document().setModified(False)
            self.status_bar.showMessage(f"Saved: {self.current_file}", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Could not save file: {str(e)}")
            return False
    
    def save_file_as(self):
        """Save file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save NovaLang File", "", 
            "NovaLang Files (*.nova);;All Files (*.*)"
        )
        if file_path:
            # Ensure .nova extension
            if not file_path.endswith('.nova'):
                file_path += '.nova'
            
            self.current_file = file_path
            self.setWindowTitle(f"NovaLang IDE - {os.path.basename(file_path)}")
            return self.save_file()
        return False
    
    def check_save(self):
        """Check if we need to save before closing/opening new file"""
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, "Save Changes",
                "The document has been modified. Save changes?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                return self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        return True
    
    def compile_code(self):
        """Compile the current code"""
        code = self.editor.get_text()
        if not code.strip():
            self.output_text.setText("No code to compile.")
            return
        
        self.status_bar.showMessage("Compiling...")
        self.output_text.clear()
        
        # Create and start compilation thread
        self.compilation_thread = CompilationThread(code)
        self.compilation_thread.compilation_done.connect(self.on_compilation_done)
        self.compilation_thread.start()
    
    def on_compilation_done(self, message, success):
        """Handle compilation result"""
        if success:
            self.output_text.setText(f"✅ {message}")
            self.status_bar.showMessage("Compilation successful", 3000)
        else:
            self.output_text.setText(f"❌ {message}")
            self.status_bar.showMessage("Compilation failed", 3000)
    
    def apply_light_theme(self):
        """Apply light theme to the entire IDE"""
        # Apply to editor
        self.editor.apply_light_theme()
        
        # Apply to output
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                color: #333;
                border: none;
            }
        """)
        
        # Apply to main window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def apply_dark_theme(self):
        """Apply dark theme to the entire IDE"""
        # Apply to editor
        self.editor.apply_dark_theme()
        
        # Apply to output
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                color: #d4d4d4;
                border: none;
            }
        """)
        
        # Apply dark theme to menu bar and toolbar
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d30;
            }
            QMenuBar {
                background-color: #2d2d30;
                color: #d4d4d4;
                border-bottom: 1px solid #3e3e42;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            QMenuBar::item:pressed {
                background-color: #505050;
            }
            QMenu {
                background-color: #2d2d30;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #3e3e42;
            }
            QToolBar {
                background-color: #2d2d30;
                border-bottom: 1px solid #3e3e42;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                color: #d4d4d4;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3e3e42;
                border: 1px solid #505050;
            }
            QToolButton:pressed {
                background-color: #505050;
            }
            QStatusBar {
                background-color: #2d2d30;
                color: #d4d4d4;
                border-top: 1px solid #3e3e42;
            }
        """)

    def load_sample_code(self):
        """Load sample code into editor"""
        sample_code = """start
# Simple NovaLang program
num count = 10
text greeting = "Hello, NovaLang!"
flag is_active = true

show greeting

# Conditional statement
when count > 5 {
    show "Count is greater than 5"
} elsewhen count == 5 {
    show "Count is exactly 5"
} else {
    show "Count is less than 5"
}

# Loop example
loop i = 1 to 5 {
    show i
}

# Function definition and call
func multiply(x, y) {
    back x * y
}

num result = multiply(3, 4)
show result

# Take input (simulated)
text name = "User"
take name
show "Hello, " + name

end
"""
        self.editor.set_text(sample_code)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application icon and name
    app.setApplicationName("NovaLang IDE")
    
    ide = NovaLangIDE()
    ide.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()