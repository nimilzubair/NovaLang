# File: nova_lang/__init__.py
"""
NovaLang compiler package
"""

# Version
__version__ = "1.0.0"
__author__ = "NovaLang Team"
__description__ = "Educational compiler front-end for NovaLang"

# Make important classes available at package level
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .semantic import SemanticAnalyzer, SemanticError
from .ast_nodes import Program