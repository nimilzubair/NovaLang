# ✨ NovaLang IDE and Compiler

<div align="center">

![NovaLang Logo](https://img.shields.io/badge/NovaLang-IDE-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![C++](https://img.shields.io/badge/C++-Compiler-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A modern, educational programming language with a professional IDE**

[Features](#-key-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Project Overview

**NovaLang** is a custom-designed, educational programming language featuring a complete **compiler backend (C++)** and a beautiful **IDE frontend (Python/PyQt6)**. This project demonstrates the full stack of language development—from **Lexical Analysis** through **Parsing**, **Semantic Analysis**, to **Code Generation**—all wrapped in a professional, user-friendly desktop application.

### Why NovaLang?

- 🎓 **Educational**: Perfect for learning compiler design and language implementation
- 🎨 **Beautiful UI**: Modern IDE with VS Code-inspired design
- 🔴 **Smart Error Detection**: Precise error highlighting with line-level accuracy
- ⚡ **Fast Compilation**: C++ backend for optimal performance
- 🌈 **Customizable**: Multiple themes and syntax highlighting

---

## 🚀 Key Features

### 🎨 IDE Features (Python + PyQt6)

| Feature | Description |
|---------|-------------|
| **🔴 Precision Error Highlighting** | Bright red background highlighting on the exact line where errors occur |
| **✨ Syntax Highlighting** | Real-time highlighting for keywords, literals, operators, and identifiers |
| **🌓 Multiple Themes** | Dark and Light themes for comfortable coding |
| **📊 Line Numbers** | Integrated line numbers with error markers (✗) |
| **⚡ Live Compilation** | Real-time feedback with detailed error messages |
| **💾 File Management** | Full file operations: New, Open, Save, Save As |
| **⌨️ Keyboard Shortcuts** | Intuitive shortcuts (F5 to run, Ctrl+S to save, etc.) |

### 🔧 Compiler Features (C++ Backend)

The compiler follows a standard multi-stage architecture:

| Stage | Component | Responsibility | Output |
|-------|-----------|----------------|--------|
| **1. Lexical Analysis** | `lexer.cpp/hpp` | Tokenizes source code into meaningful units | Token Stream |
| **2. Syntax Analysis** | `parser.cpp/hpp` | Builds Abstract Syntax Tree (AST) using recursive descent | AST |
| **3. Semantic Analysis** | `semantic.cpp/hpp` | Type checking, scope validation, symbol table management | Validated AST |

---

## 💻 Installation

### Prerequisites

Ensure you have the following installed:

- **Python 3.8+**
- **PyQt6** library
- **C++ Compiler** (GCC, MSVC, or Clang)
- **Make** or **CMake** (optional, for building)

### Step 1: Clone the Repository
```bash
git clone https://github.com/YourUsername/NovaLang-IDE.git
cd NovaLang-IDE
```

### Step 2: Install Python Dependencies
```bash
pip install PyQt6
```

### Step 3: Build the C++ Compiler Backend

#### On Windows (using MSVC):
```bash
cd nova_lang
cl /EHsc main.cpp lexer.cpp parser.cpp semantic.cpp token.cpp /Fe:Project2.exe
```

#### On Linux/Mac (using GCC):
```bash
cd nova_lang
g++ -std=c++17 main.cpp lexer.cpp parser.cpp semantic.cpp token.cpp -o Project2
```

### Step 4: Move Compiler to IDE Directory
```bash
# Windows
copy nova_lang\Project2.exe ide\

# Linux/Mac
cp nova_lang/Project2 ide/
```

---

## 🎯 Usage

### Running the IDE
```bash
cd ide
python novalang_ide.py
```

### Quick Start Guide

1. **Create a new file**: Click `File → New` or press `Ctrl+N`
2. **Write your code**: Use the NovaLang syntax (see examples below)
3. **Run the code**: Click the `▶ Run` button or press `F5`
4. **View output**: Check the output panel on the right
5. **Fix errors**: Red-highlighted lines indicate errors

### Example NovaLang Program
```novalang
start
    # Variable declarations
    num count = 10
    text greeting = "Hello, NovaLang!"
    flag is_active = true
    
    # Output
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
        when i == 3 {
            break
        }
    }
    
    # Function definition
    func multiply(x, y) {
        back x * y  # 'back' returns a value
    }
    
    # Function call
    num result = multiply(4, 5)
    show result
end
```

---

## 📚 Language Reference

### Data Types

| Type | Keyword | Example | Description |
|------|---------|---------|-------------|
| Integer | `num` | `num age = 25` | Numeric values |
| String | `text` | `text name = "John"` | Text values |
| Boolean | `flag` | `flag active = true` | true/false values |

### Keywords
```
start    end      show     take     when     elsewhen
else     loop     break    func     back     num
text     flag     true     false    to
```

### Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`, `-`, `*`, `/` |
| Comparison | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| Assignment | `=` |

### Control Flow

#### Conditional Statements
```novalang
when condition {
    # code
} elsewhen another_condition {
    # code
} else {
    # code
}
```

#### Loops
```novalang
loop i = 1 to 10 {
    show i
    when i == 5 {
        break
    }
}
```

#### Functions
```novalang
func function_name(param1, param2) {
    # code
    back result
}
```

---

## 🏗️ Project Structure
```
NovaLang-IDE/
├── ide/                          # IDE Frontend (Python/PyQt6)
│   ├── editor.py                # Code editor with line numbers
│   ├── novalang_ide.py          # Main IDE application
│   ├── syntax_highlighter.py    # Syntax highlighting engine
│   ├── themes.py                # Color theme definitions
│   └── Project2.exe             # Compiled backend (after build)
│
├── nova_lang/                    # Compiler Backend (C++)
│   ├── lexer.cpp / .hpp         # Lexical analyzer
│   ├── parser.cpp / .hpp        # Syntax parser
│   ├── semantic.cpp / .hpp      # Semantic analyzer
│   ├── ast_nodes.hpp            # AST node definitions
│   ├── token.cpp / .hpp         # Token definitions
│   ├── main.cpp                 # Compiler entry point
│   └── Makefile.win             # Build configuration
│
├── examples/                     # Sample NovaLang programs
│   ├── hello_world.nova
│   ├── fibonacci.nova
│   └── calculator.nova
│
└── README.md                     # This file
```

---

## 🔍 Technical Deep Dive

### Compiler Architecture

#### 1. Lexer (Tokenization)
The lexer converts raw source code into tokens:
```cpp
// Input: "num count = 10"
// Output:
NUM('num') @1:1
IDENT('count') @1:5
ASSIGN('=') @1:11
NUMBER('10') @1:13
```

#### 2. Parser (AST Construction)
Recursive descent parser builds the Abstract Syntax Tree:
```
Program
├── VarDecl(num, count, 10)
└── ShowStmt(count)
```

#### 3. Semantic Analyzer
Validates:
- ✅ Type compatibility
- ✅ Variable declarations
- ✅ Function signatures
- ✅ Scope rules

### IDE Architecture

The IDE uses a **modular design**:
```python
# editor.py - Custom QPlainTextEdit
- Line numbers
- Error highlighting
- Syntax highlighting integration

# novalang_ide.py - Main window
- File operations
- Compilation management
- UI layout

# syntax_highlighter.py - QSyntaxHighlighter
- Token-based highlighting
- Theme support

# themes.py - Color schemes
- Dark theme
- Light theme
```

### Error Highlighting Algorithm
```python
# Smart error detection
1. Parse compiler output
2. Extract error message: "Error: Use of undeclared variable 'result'"
3. Find identifier: 'result'
4. Locate in token stream: IDENT('result') @7:6
5. Highlight line 7 with red background
6. Show error marker: ✗ 7
```

---

## 🎨 Screenshots

### Dark Theme with Error Highlighting
```
┌─────────────────────────────────────────────────┐
│ 📝 Editor                         ▶ Run         │
├─────────────────────────────────────────────────┤
│  1  start                                       │
│  2  num x = 10                                  │
│✗ 3  show result      ← RED HIGHLIGHT           │
│  4  end                                         │
└─────────────────────────────────────────────────┘
```

### Light Theme
```
Clean, bright interface for daytime coding
```

---

## 🧪 Running Tests

### Test the Compiler
```bash
cd nova_lang
./Project2 ../examples/hello_world.nova
```

### Test the IDE
```bash
cd ide
python novalang_ide.py
# Use Debug → Test Error Highlight
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Areas for Contribution

- 🐛 **Bug Fixes**: Report and fix issues
- ✨ **New Features**: Add language features or IDE enhancements
- 📚 **Documentation**: Improve docs and examples
- 🎨 **Themes**: Create new color schemes
- 🧪 **Testing**: Write test cases

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- **Python**: Follow PEP 8
- **C++**: Use modern C++17 standards
- **Comments**: Document complex logic

---

## 📖 Documentation

### Additional Resources

- 📘 [Language Specification](docs/language-spec.md)
- 🔧 [API Reference](docs/api-reference.md)
- 🎓 [Tutorial Series](docs/tutorials/)
- 💡 [FAQ](docs/faq.md)

---

## 🐛 Known Issues

- [ ] Long compilation times for very large files (>1000 lines)
- [ ] Theme switching requires restart for full effect
- [ ] Windows-only executable (Linux/Mac support coming soon)

---

## 🗺️ Roadmap

### Version 1.1 (Coming Soon)
- [ ] Code autocompletion
- [ ] Bracket matching
- [ ] Find and replace
- [ ] Multiple file tabs

### Version 2.0 (Future)
- [ ] Debugger integration
- [ ] Code formatting
- [ ] Plugin system
- [ ] Cross-platform binaries

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2025 NovaLang Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👥 Authors

- **Your Name** - *Initial work* - [@YourGitHub](https://github.com/YourUsername)

See also the list of [contributors](https://github.com/YourUsername/NovaLang-IDE/contributors) who participated in this project.

---

## 🙏 Acknowledgments

- Inspired by modern IDEs like **VS Code** and **Sublime Text**
- Built with **PyQt6** framework
- Compiler design based on **Dragon Book** principles
- Community feedback and contributions

---

## 📞 Support

- 📧 Email: support@novalang.dev
- 💬 Discord: [Join our community](https://discord.gg/novalang)
- 🐦 Twitter: [@NovaLangIDE](https://twitter.com/novalangide)
- 📖 Documentation: [docs.novalang.dev](https://docs.novalang.dev)

---

<div align="center">

**⭐ Star this repo if you find it helpful! ⭐**

Made with ❤️ by the NovaLang Team

[Report Bug](https://github.com/YourUsername/NovaLang-IDE/issues) • [Request Feature](https://github.com/YourUsername/NovaLang-IDE/issues)

</div>