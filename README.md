# NovaLang Educational Compiler Front-End

This project provides a small educational compiler front-end for a toy language **NovaLang**.

## Features Implemented

- Lexing with line/column tracking and friendly errors
- Recursive-descent parsing
- AST construction
- Semantic checks:
  - use-before-declaration
  - redeclaration
  - type mismatches
  - break outside loop
  - back outside function
  - function call argument count mismatch
- Simple CLI (`python -m novalang.main file.nova`)

## EBNF Grammar

