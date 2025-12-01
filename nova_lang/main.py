"""
CLI entry point
"""

import sys
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .semantic import SemanticAnalyzer, SemanticError

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m novalang.main <file.nova>")
        sys.exit(1)

    fname = sys.argv[1]
    with open(fname, 'r') as f:
        text = f.read()

    # Lex
    try:
        lexer = Lexer(text)
        tokens = list(lexer.generate_tokens())
    except LexerError as e:
        print("Lexer error:", e)
        sys.exit(1)

    print("Tokens:")
    for t in tokens:
        print(t)

    # Parse
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except ParserError as e:
        print("Parser error:", e)
        sys.exit(1)

    print("\nAST:", ast)

    # Semantic
    try:
        sem = SemanticAnalyzer()
        sem.analyze(ast)
        print("\nSemantic analysis: OK")
    except SemanticError as e:
        print("Semantic error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
