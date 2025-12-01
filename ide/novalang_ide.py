# File: ide/novalang_ide.py (simplified and fixed)
"""
NovaLang IDE - PyQt6 Version (Simplified)
"""
import sys
import os
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

class SimpleCodeEditor(QPlainTextEdit):
    """Simple code editor without line numbers"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas" if QFont("Consolas").exactMatch() else "Courier New", 11))
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
                border: 1px solid #555;
            }
        """)
    
    def get_text(self):
        return self.toPlainText()
    
    def set_text(self, text):
        self.setPlainText(text)
    
    def is_modified(self):
        return self.document().isModified()

class NovaLangIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaLang IDE")
        self.setGeometry(100, 100, 1200, 700)
        
        self.current_file = None
        self.is_modified = False
        
        self.init_ui()
        self.create_actions()
        self.create_menu()
        self.create_toolbar()
        
        # Load sample code
        self.load_sample_code()
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for editor and output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.editor = SimpleCodeEditor()
        left_layout.addWidget(self.editor)
        
        # Right side - output
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas" if QFont("Consolas").exactMatch() else "Courier New", 10))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                color: #d4d4d4;
                border: 1px solid #555;
            }
        """)
        right_layout.addWidget(self.output_text)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_actions(self):
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
        
        self.compile_action = QAction("&Compile", self)
        self.compile_action.setShortcut("F5")
        self.compile_action.triggered.connect(self.compile_code)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)
        
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
        if self.check_save():
            self.editor.clear()
            self.current_file = None
            self.is_modified = False
            self.setWindowTitle("NovaLang IDE - Untitled")
            self.status_bar.showMessage("New file created")
    
    def open_file(self):
        if self.check_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open NovaLang File", "", "NovaLang Files (*.nova);;All Files (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    self.editor.set_text(content)
                    self.current_file = file_path
                    self.is_modified = False
                    self.setWindowTitle(f"NovaLang IDE - {os.path.basename(file_path)}")
                    self.status_bar.showMessage(f"Opened: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        if self.current_file is None:
            return self.save_file_as()
        try:
            with open(self.current_file, 'w') as f:
                f.write(self.editor.get_text())
            self.is_modified = False
            self.status_bar.showMessage(f"Saved: {self.current_file}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save NovaLang File", "", "NovaLang Files (*.nova);;All Files (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.setWindowTitle(f"NovaLang IDE - {os.path.basename(file_path)}")
            return self.save_file()
        return False
    
    def check_save(self):
        if self.editor.is_modified():
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
        if success:
            self.output_text.setText(f"✅ {message}")
            self.status_bar.showMessage("Compilation successful")
        else:
            self.output_text.setText(f"❌ {message}")
            self.status_bar.showMessage("Compilation failed")
    
    def apply_light_theme(self):
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: white;
                color: black;
                selection-background-color: #c8e1ff;
                border: 1px solid #ccc;
            }
        """)
        
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                color: #333;
                border: 1px solid #ccc;
            }
        """)
        
        # Apply light palette to window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def apply_dark_theme(self):
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
                border: 1px solid #555;
            }
        """)
        
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                color: #d4d4d4;
                border: 1px solid #555;
            }
        """)
        
        # Apply dark palette to window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)
    
    def load_sample_code(self):
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
        if self.check_save():
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    ide = NovaLangIDE()
    ide.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()