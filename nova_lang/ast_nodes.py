"""
AST node classes for NovaLang
"""

class Program:
    def __init__(self, statements):
        self.statements = statements

class VarDecl:
    def __init__(self, vartype, name, expr):
        self.vartype = vartype
        self.name = name
        self.expr = expr

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Show:
    def __init__(self, expr):
        self.expr = expr

class Take:
    def __init__(self, name):
        self.name = name

class When:
    def __init__(self, cases, else_block):
        # cases = list of (cond, blockStatements)
        self.cases = cases
        self.else_block = else_block

class Loop:
    def __init__(self, var, start_expr, end_expr, body):
        self.var = var
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body

class Break:
    pass

class FuncDef:
    def __init__(self, name, params, body, back_expr):
        self.name = name
        self.params = params
        self.body = body
        self.back_expr = back_expr

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

# Expressions
class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # token
        self.right = right

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Literal:
    def __init__(self, value, lit_type):
        self.value = value
        self.lit_type = lit_type  # 'num', 'text', 'bool'

class Identifier:
    def __init__(self, name):
        self.name = name
