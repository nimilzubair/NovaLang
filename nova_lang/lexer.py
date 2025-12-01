"""
NovaLang Regex Lexer with line/column tracking
"""

import re
from .token import Token, TokenType

class LexerError(Exception):
    pass

class Lexer:
    token_spec = [
        ('START', r'start\b'),
        ('END', r'end\b'),
        ('SHOW', r'show\b'),
        ('TAKE', r'take\b'),
        ('WHEN', r'when\b'),
        ('ELSEWHEN', r'elsewhen\b'),
        ('ELSE', r'else\b'),
        ('LOOP', r'loop\b'),
        ('BREAK', r'break\b'),
        ('FUNC', r'func\b'),
        ('BACK', r'back\b'),
        ('NUMKW', r'num\b'),
        ('TEXTKW', r'text\b'),
        ('FLAGKW', r'flag\b'),
        ('TRUE', r'true\b'),
        ('FALSE', r'false\b'),
        ('TO', r'to\b'),

        ('NUMBER', r'\d+'),
        ('STRING', r'"[^"]*"'),
        ('IDENT', r'[A-Za-z_][A-Za-z0-9_]*'),

        ('EQEQ', r'=='),
        ('NOTEQ', r'!='),
        ('GTEQ', r'>='),
        ('LTEQ', r'<='),
        ('GT', r'>'),
        ('LT', r'<'),
        ('ASSIGN', r'='),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('STAR', r'\*'),
        ('SLASH', r'/'),
        ('COMMA', r','),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),

        ('SKIP', r'[ \t]+'),
        ('NEWLINE', r'\n'),
        ('MISMATCH', r'.')
    ]

    tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_spec)

    def __init__(self, text: str):
        self.text = text
        self.line = 1
        self.col = 1
        self.pos = 0
        self.regex = re.compile(self.tok_regex)

        self.type_map = {
            'START': TokenType.START,
            'END': TokenType.END,
            'SHOW': TokenType.SHOW,
            'TAKE': TokenType.TAKE,
            'WHEN': TokenType.WHEN,
            'ELSEWHEN': TokenType.ELSEWHEN,
            'ELSE': TokenType.ELSE,
            'LOOP': TokenType.LOOP,
            'BREAK': TokenType.BREAK,
            'FUNC': TokenType.FUNC,
            'BACK': TokenType.BACK,
            'NUMKW': TokenType.NUM,
            'TEXTKW': TokenType.TEXT,
            'FLAGKW': TokenType.FLAG,
            'TRUE': TokenType.BOOL,
            'FALSE': TokenType.BOOL,
            'NUMBER': TokenType.NUMBER,
            'STRING': TokenType.STRING,
            'IDENT': TokenType.IDENT,
            'EQEQ': TokenType.EQEQ,
            'NOTEQ': TokenType.NOTEQ,
            'GTEQ': TokenType.GTEQ,
            'LTEQ': TokenType.LTEQ,
            'GT': TokenType.GT,
            'LT': TokenType.LT,
            'ASSIGN': TokenType.ASSIGN,
            'PLUS': TokenType.PLUS,
            'MINUS': TokenType.MINUS,
            'STAR': TokenType.STAR,
            'SLASH': TokenType.SLASH,
            'COMMA': TokenType.COMMA,
            'LPAREN': TokenType.LPAREN,
            'RPAREN': TokenType.RPAREN,
            'LBRACE': TokenType.LBRACE,
            'RBRACE': TokenType.RBRACE,
            'TO': TokenType.TO
        }

    def generate_tokens(self):
        for m in self.regex.finditer(self.text):
            kind = m.lastgroup
            value = m.group()
            if kind == 'NEWLINE':
                self.line += 1
                self.col = 1
                continue
            elif kind == 'SKIP':
                self.col += len(value)
                continue
            elif kind == 'MISMATCH':
                raise LexerError(f"Unexpected character {value!r} at line {self.line}, col {self.col}")
            else:
                ttype = self.type_map[kind]
                token = Token(ttype, value, self.line, self.col)
                yield token
                self.col += len(value)
        yield Token(TokenType.EOF, '', self.line, self.col)
