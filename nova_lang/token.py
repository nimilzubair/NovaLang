"""
Token definitions for NovaLang
"""

from enum import Enum, auto

class TokenType(Enum):
    # Special
    EOF = auto()
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()

    # Keywords
    START = auto()
    END = auto()
    SHOW = auto()
    TAKE = auto()
    WHEN = auto()
    ELSEWHEN = auto()
    ELSE = auto()
    LOOP = auto()
    BREAK = auto()
    FUNC = auto()
    BACK = auto()
    NUM = auto()
    TEXT = auto()
    FLAG = auto()
    TRUE = auto()
    FALSE = auto()

    # Operators/Punct
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    EQEQ = auto()
    NOTEQ = auto()
    GT = auto()
    LT = auto()
    GTEQ = auto()
    LTEQ = auto()

    ASSIGN = auto()     # '='
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    TO = auto()

class Token:
    def __init__(self, ttype: TokenType, value: str, line: int, col: int):
        self.type = ttype
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.col})"
