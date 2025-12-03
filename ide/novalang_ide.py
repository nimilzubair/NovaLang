# File: ide/novalang_ide.py
"""
NovaLang IDE - Main Application
Professional IDE with modern UI for NovaLang programming language
"""

import sys
import os
import subprocess
import re

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSplitter, QStatusBar, QToolBar, QFileDialog,
    QMessageBox, QPushButton, QLabel, QFrame
)
from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtCore import Qt

from editor import CodeEditorWithLineNumbers
from themes import get_theme


class NovaLangIDE(QMainWindow):
    """Main IDE window for NovaLang"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaLang IDE")
        self.setGeometry(100, 100, 1400, 800)
        self.current_file = None
        
        self.init_ui()
        self.create_actions()
        self.create_menu()
        self.create_toolbar()
        self.apply_dark_theme()
        self.load_sample_code()

    def init_ui(self):
        """Initialize the user interface"""
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Editor and output splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Editor
        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        
        # Editor header
        editor_header = QFrame()
        editor_header.setFrameShape(QFrame.Shape.StyledPanel)
        editor_header.setMaximumHeight(35)
        editor_header_layout = QHBoxLayout(editor_header)
        editor_header_layout.setContentsMargins(10, 5, 10, 5)
        
        editor_label = QLabel("📝 Editor")
        editor_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        editor_header_layout.addWidget(editor_label)
        editor_header_layout.addStretch()
        
        # Run button in header
        self.run_btn = QPushButton("▶ Run")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
        """)
        self.run_btn.clicked.connect(self.compile_code_backend)
        editor_header_layout.addWidget(self.run_btn)
        
        editor_layout.addWidget(editor_header)
        
        # Code editor
        self.editor = CodeEditorWithLineNumbers()
        editor_layout.addWidget(self.editor)
        
        # Right panel - Output
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(0)
        
        # Output header
        output_header = QFrame()
        output_header.setFrameShape(QFrame.Shape.StyledPanel)
        output_header.setMaximumHeight(35)
        output_header_layout = QHBoxLayout(output_header)
        output_header_layout.setContentsMargins(10, 5, 10, 5)
        
        output_label = QLabel("📤 Output")
        output_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        output_header_layout.addWidget(output_label)
        output_header_layout.addStretch()
        
        # Clear output button
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        clear_btn.clicked.connect(lambda: self.output_text.clear())
        output_header_layout.addWidget(clear_btn)
        
        output_layout.addWidget(output_header)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont(
            "Consolas" if QFont("Consolas").exactMatch() else "Courier New", 
            10
        ))
        output_layout.addWidget(self.output_text)
        
        # Add panels to splitter
        splitter.addWidget(editor_panel)
        splitter.addWidget(output_panel)
        splitter.setSizes([900, 500])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # File info in status bar
        self.file_label = QLabel("No file")
        self.status_bar.addPermanentWidget(self.file_label)

    def create_actions(self):
        """Create menu and toolbar actions"""
        # File actions
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction("Save As", self)
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)
        
        # Run action
        self.run_action = QAction("Run", self)
        self.run_action.setShortcut("F5")
        self.run_action.triggered.connect(self.compile_code_backend)
        
        # Theme actions
        self.light_theme_action = QAction("Light Theme", self)
        self.light_theme_action.triggered.connect(self.apply_light_theme)
        
        self.dark_theme_action = QAction("Dark Theme", self)
        self.dark_theme_action.triggered.connect(self.apply_dark_theme)
        
        # Debug action - Test error highlighting
        self.test_error_action = QAction("Test Error Highlight (Line 4)", self)
        self.test_error_action.triggered.connect(
            lambda: self.editor.highlight_error_line(4)
        )

    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Run menu
        run_menu = menubar.addMenu("Run")
        run_menu.addAction(self.run_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.light_theme_action)
        view_menu.addAction(self.dark_theme_action)
        
        # Debug menu (can be removed in production)
        debug_menu = menubar.addMenu("Debug")
        debug_menu.addAction(self.test_error_action)

    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()

    # ==================== File Operations ====================
    
    def new_file(self):
        """Create a new file"""
        if self.check_save():
            self.editor.set_text("")
            self.current_file = None
            self.setWindowTitle("NovaLang IDE - Untitled")
            self.file_label.setText("No file")
            self.status_label.setText("New file created")

    def open_file(self):
        """Open an existing file"""
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
                    filename = os.path.basename(file_path)
                    self.setWindowTitle(f"NovaLang IDE - {filename}")
                    self.file_label.setText(filename)
                    self.status_label.setText(f"Opened: {filename}")
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", 
                        f"Could not open file:\n{str(e)}"
                    )

    def save_file(self):
        """Save the current file"""
        if self.current_file is None:
            return self.save_file_as()
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.editor.document().setModified(False)
            filename = os.path.basename(self.current_file)
            self.status_label.setText(f"Saved: {filename}")
            return True
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Could not save file:\n{str(e)}"
            )
            return False

    def save_file_as(self):
        """Save the current file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save NovaLang File", "",
            "NovaLang Files (*.nova);;All Files (*.*)"
        )
        if file_path:
            if not file_path.endswith('.nova'):
                file_path += '.nova'
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"NovaLang IDE - {filename}")
            self.file_label.setText(filename)
            return self.save_file()
        return False

    def check_save(self):
        """Check if the file needs to be saved before proceeding"""
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

    # ==================== Compilation ====================
    
    def compile_code_backend(self):
        """Compile the code using the backend compiler"""
        if self.current_file is None:
            self.save_file_as()
            if self.current_file is None:
                return
        
        # Save file before compiling
        self.save_file()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_exe = os.path.join(current_dir, "Project2.exe")
        
        if not os.path.exists(backend_exe):
            self.output_text.setHtml(
                f'<p style="color: #ff6b6b;"><b>❌ Error:</b> '
                f'Backend compiler not found</p>'
                f'<p style="color: #999;">Expected location: {backend_exe}</p>'
            )
            return
        
        self.output_text.clear()
        self.editor.clear_error_highlighting()
        self.status_label.setText("⚙️ Compiling...")
        self.run_btn.setEnabled(False)
        
        try:
            result = subprocess.run(
                [backend_exe, self.current_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # Try multiple patterns to extract line number
            line_num = None
            
            # First, look for "Error:" line which contains the actual error
            error_line_match = re.search(r'Error:.*', output, re.IGNORECASE)
            if error_line_match:
                error_text = error_line_match.group(0)
                print(f"DEBUG: Error line found: {error_text}")
                
                # Try to extract variable/identifier name from error
                # Pattern: "undeclared variable 'result'" or similar
                var_match = re.search(r"['\"](\w+)['\"]", error_text)
                if var_match:
                    var_name = var_match.group(1)
                    print(f"DEBUG: Error involves identifier: {var_name}")
                    
                    # Find the line where this identifier appears
                    # Look for IDENT('var_name') @LINE:COL pattern
                    ident_pattern = rf"IDENT\(['\"]?{re.escape(var_name)}['\"]?\)\s+@(\d+):\d+"
                    ident_matches = list(re.finditer(ident_pattern, output))
                    if ident_matches:
                        # Get the LAST occurrence of this identifier (where error likely is)
                        line_num = int(ident_matches[-1].group(1))
                        print(f"DEBUG: Found '{var_name}' at line {line_num}")
            
            # Pattern 2: "at 15:1" in the error line
            if not line_num and error_line_match:
                match = re.search(r'at\s+(\d+):\d+', error_line_match.group(0))
                if match:
                    line_num = int(match.group(1))
                    print(f"DEBUG: Found line number in error: {line_num}")
            
            # Pattern 3: Look for the LAST non-EOF token before "Error:"
            if not line_num:
                # Find all @LINE:COL patterns, excluding EOF
                matches = list(re.finditer(r"(?!EOF)IDENT.*?@(\d+):\d+", output))
                if not matches:
                    matches = list(re.finditer(r"(?!EOF)\w+\([^)]*\)\s+@(\d+):\d+", output))
                if matches:
                    # Get the last match before "Error:"
                    error_pos = output.find('Error:')
                    if error_pos > 0:
                        for match in reversed(matches):
                            if match.start() < error_pos:
                                line_num = int(match.group(1))
                                print(f"DEBUG: Found line number from last token before error: {line_num}")
                                break
            
            # Pattern 4: "at 15:1" anywhere in output
            if not line_num:
                match = re.search(r'at\s+(\d+):\d+', output)
                if match:
                    line_num = int(match.group(1))
                    print(f"DEBUG: Found line number using 'at LINE:COL': {line_num}")
            
            # Pattern 5: "line 4" or "Line 4"
            if not line_num:
                match = re.search(r'[Ll]ine\s+(\d+)', output)
                if match:
                    line_num = int(match.group(1))
                    print(f"DEBUG: Found line number using 'line N': {line_num}")
            
            # Highlight the error line if found
            if line_num and result.returncode != 0:
                self.editor.highlight_error_line(line_num)
            else:
                if result.returncode != 0:
                    print(f"DEBUG: No line number found in output: {output[:200]}")
            
            # Format output with colors
            if result.returncode == 0:
                self.output_text.setHtml(
                    f'<p style="color: #4ec9b0;"><b>✓ Compilation Successful</b></p>'
                    f'<pre style="color: #d4d4d4;">{output}</pre>'
                )
                self.status_label.setText("✓ Compilation successful")
            else:
                # Show line number in error message if found
                error_msg = '✗ Compilation Failed'
                if line_num:
                    error_msg += f' (Line {line_num})'
                
                self.output_text.setHtml(
                    f'<p style="color: #ff6b6b;"><b>{error_msg}</b></p>'
                    f'<pre style="color: #f48771;">{output}</pre>'
                )
                status_msg = "✗ Compilation failed"
                if line_num:
                    status_msg += f" at line {line_num}"
                self.status_label.setText(status_msg)
        
        except subprocess.TimeoutExpired:
            self.output_text.setHtml(
                '<p style="color: #ff6b6b;"><b>✗ Error:</b> '
                'Compilation timed out</p>'
            )
            self.status_label.setText("✗ Timeout")
        except Exception as e:
            self.output_text.setHtml(
                f'<p style="color: #ff6b6b;"><b>✗ Error:</b> {str(e)}</p>'
            )
            self.status_label.setText("✗ Error")
        finally:
            self.run_btn.setEnabled(True)

    # ==================== Themes ====================
    
    def apply_light_theme(self):
        """Apply light theme to the IDE"""
        self.editor.apply_light_theme()
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: none;
            }
        """)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f3;
            }
            QMenuBar {
                background-color: #f3f3f3;
                color: #333333;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            QMenu {
                background-color: #ffffff;
                color: #333333;
            }
            QToolBar {
                background-color: #f3f3f3;
                border-bottom: 1px solid #d0d0d0;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QFrame {
                background-color: #e8e8e8;
            }
        """)

    def apply_dark_theme(self):
        """Apply dark theme to the IDE"""
        self.editor.apply_dark_theme()
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        """)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d30;
            }
            QMenuBar {
                background-color: #2d2d30;
                color: #d4d4d4;
                border-bottom: 1px solid #3e3e42;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
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
            }
            QToolButton:hover {
                background-color: #3e3e42;
                border-radius: 3px;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QFrame {
                background-color: #333337;
            }
            QLabel {
                color: #cccccc;
            }
        """)

    def load_sample_code(self):
        """Load sample NovaLang code into the editor"""
        sample = """start
# Welcome to NovaLang IDE!
# Press F5 or click Run to compile

num count = 10
text greeting = "Hello, NovaLang!"
flag is_active = true

show greeting

when count > 5 {
    show "Count is greater than 5"
}

loop i = 1 to 5 {
    show i
}

func multiply(x, y) {
    back x * y
}

num result = multiply(3, 4)
show result

end
"""
        self.editor.set_text(sample)

    def closeEvent(self, event):
        """Handle window close event"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()


# ==================== Main ====================

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("NovaLang IDE")
    
    ide = NovaLangIDE()
    ide.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()