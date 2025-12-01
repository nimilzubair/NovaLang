# ✨ NovaLang IDE and Compiler

## 🌟 Project Overview

**NovaLang** is a custom-designed, educational programming language and Integrated Development Environment (IDE) built using **Python** and **PyQt6**. This project serves as a complete compiler front-end, demonstrating the core stages of language processing—**Lexical Analysis**, **Parsing**, and **Semantic Analysis**—within a functional, user-friendly desktop application.

The IDE features real-time **syntax highlighting** and **live error feedback** (with line highlighting) to provide an engaging environment for learning compiler principles and structured programming concepts. 

---

## 🚀 Key Features

### IDE Enhancements (PyQt6)
* **Precision Error Highlighting:** **Prominent red background highlighting** on the **exact line** where the compiler reports a Lexer, Parser, or Semantic error.
* **Syntax Highlighting:** Real-time highlighting for all NovaLang keywords (`when`, `loop`, `func`, `num`, etc.), literals, and operators.
* **Theming:** Support for multiple color themes (Dark, Light, Monokai) for a personalized development environment.
* **Line Numbers:** Integrated, custom line number sidebar for easy code navigation.

### Compiler Core (Python)

The compiler is structured following the standard three-stage architecture: 

| Stage | Component | Task | Output |
| :--- | :--- | :--- | :--- |
| 1. **Lexing** | `lexer.py` | Converts raw source code into meaningful **tokens** (e.g., `IDENT`, `NUMBER`, `WHEN`). | List of Tokens |
| 2. **Parsing** | `parser.py` | Uses a **Recursive Descent Parser** to build the **Abstract Syntax Tree (AST)**. Validates the grammatical structure (syntax). | AST |
| 3. **Semantic** | `semantic.py` | Performs context-sensitive analysis, including **type checking** and symbol table validation. | Verified AST |

---

## 💻 Getting Started

### Prerequisites

You need **Python 3.x** and the **PyQt6** library installed.

```bash
pip install PyQt6
```
Installation & Run
Clone the repository:

```Bash

git clone [https://github.com/YourUsername/NovaLang-IDE.git](https://github.com/YourUsername/NovaLang-IDE.git)
cd NovaLang-IDE
Run the IDE from the package root:
```



## Code snippet
```
start
    # Variable Declaration & Assignment
    num count = 10
    text greeting = "Hello, NovaLang!"
    
    # Conditional statement
    when count > 5 { 
        show greeting 
    } elsewhen count == 5 {
        show "Count is 5"
    } else {
        show "Count is less than 5"
    }
    
    # Loop example
    loop i = 1 to 3 { 
        show i 
        when i == 2 {
            break # Exit the loop early
        }
    }
    
    # Function Definition and Call
    func calculate_tax(amount) {
        # 'back' is used to return a value
        back amount * 0.15 
    }
    
    num tax_due = calculate_tax(100)
    show tax_due
end
```
⚙️ Technical Deep Dive
Enhanced Parser Error Reporting
A key technical achievement is ensuring that syntax errors related to missing blocks ({}) are reported accurately at the point of failure.

Problem: When a brace ({) was missing after a keyword like when, the error traditionally pointed to the next token (end or EOF), which was misleading.

**Solution :** In nova_lang/parser.py, the when_stmt and loop_stmt methods now capture the starting keyword token (when_token or loop_token) and pass it to the block(self, context_token) method. If the LBRACE is missing, the ParserError is raised using the line number of the context_token, ensuring the highlight targets the correct line (e.g., the line containing when x > 5).
```
Project Structure
NovaLang-IDE/
├── ide/
│   ├── editor.py             # Custom QPlainTextEdit (Line numbering, error highlighting)
│   ├── novalang_ide.py       # Main Application Window and CompilationThread
│   ├── syntax_highlighter.py # QSyntaxHighlighter implementation
│   └── themes.py             # Color theme definitions
└── nova_lang/
    ├── lexer.py              # Lexical Analyzer (Regex-based)
    ├── parser.py             # Recursive Descent Parser (AST Builder)
    ├── semantic.py           # Semantic Analyzer (Type Checker, Scoping)
    ├── ast_nodes.py          # Abstract Syntax Tree (AST) node classes
    ├── token.py              # Token definitions
    └── main.py               # CLI entry point for compiler testing

```
🤝 Contributing
We welcome contributions to NovaLang! If you have suggestions for new language features, bug reports, or IDE improvements, please open an issue or submit a pull request.
