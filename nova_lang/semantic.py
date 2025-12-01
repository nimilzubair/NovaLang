"""
Semantic analysis for NovaLang: symbol tables, types, validation
"""

from .ast_nodes import *
from .token import TokenType

class SemanticError(Exception):
    pass

class Symbol:
    def __init__(self, name, typ):
        self.name = name
        self.type = typ

class FunctionSymbol:
    def __init__(self, name, params):
        self.name = name
        self.params = params  # list of param names
        # return type is num/text/flag, but here deduce later or store dynamic

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]  # var scopes
        self.functions = {}
        self.in_loop = 0
        self.in_func = 0

    def error(self, msg):
        raise SemanticError(msg)

    def declare_var(self, name, typ):
        if name in self.scopes[-1]:
            self.error(f"Redeclaration of variable '{name}'")
        self.scopes[-1][name] = Symbol(name, typ)

    def lookup_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.error(f"Use of undeclared variable '{name}'")

    def analyze(self, node):
        return self.visit(node)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(node)
        else:
            # ignore nodes or basic types
            return None

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDecl(self, node: VarDecl):
        vtyp = node.vartype  # str
        expr_type = self.visit(node.expr)
        if vtyp == 'num' and expr_type != 'num':
            self.error("Type mismatch: expected num")
        if vtyp == 'text' and expr_type != 'text':
            self.error("Type mismatch: expected text")
        if vtyp == 'flag' and expr_type != 'bool':
            self.error("Type mismatch: expected flag")
        self.declare_var(node.name, vtyp)

    def visit_Assign(self, node: Assign):
        sym = self.lookup_var(node.name)
        expr_type = self.visit(node.expr)
        if sym.type == 'num' and expr_type != 'num':
            self.error("Type mismatch in assignment to num")
        if sym.type == 'text' and expr_type != 'text':
            self.error("Type mismatch in assignment to text")
        if sym.type == 'flag' and expr_type != 'bool':
            self.error("Type mismatch in assignment to flag")

    def visit_Show(self, node: Show):
        self.visit(node.expr)

    def visit_Take(self, node: Take):
        sym = self.lookup_var(node.name)
        # allowed to read text/num/bool
        return sym.type

    def visit_When(self, node: When):
        # each condition must be bool
        for cond, stmts in node.cases:
            ctype = self.visit(cond)
            if ctype != 'bool':
                self.error("When condition must be boolean")
            self.scopes.append({})
            for s in stmts:
                self.visit(s)
            self.scopes.pop()
        if node.else_block:
            self.scopes.append({})
            for s in node.else_block:
                self.visit(s)
            self.scopes.pop()

    def visit_Loop(self, node: Loop):
        # loop i = expr to expr
        # i must be num
        start_t = self.visit(node.start_expr)
        end_t = self.visit(node.end_expr)
        if start_t != 'num' or end_t != 'num':
            self.error("Loop bounds must be num")
        # new scope
        self.scopes.append({})
        self.declare_var(node.var, 'num')
        self.in_loop += 1
        for s in node.body:
            self.visit(s)
        self.in_loop -= 1
        self.scopes.pop()

    def visit_Break(self, node: Break):
        if self.in_loop == 0:
            self.error("break outside loop")

    def visit_FuncDef(self, node: FuncDef):
        # Register function
        if node.name in self.functions:
            self.error(f"Redeclaration of function '{node.name}'")
        self.functions[node.name] = FunctionSymbol(node.name, node.params)

        # new scope
        self.scopes.append({})
        # declare params as num/text/flag? NovaLang spec not explicit, assume dynamic?
        # For simplicity, assume numeric parameters (or accept any?)
        # We'll accept num only? No: allow dynamic but check usage.
        # Here allow all types: treat params as 'num' by default? 
        # Given spec unclear, we treat them as untyped (None). We'll assign type upon first assignment?
        for p in node.params:
            self.declare_var(p, 'num')  # simplistic; can be improved

        self.in_func += 1
        for s in node.body:
            self.visit(s)
        # back expr
        ret_type = self.visit(node.back_expr)
        self.in_func -= 1
        self.scopes.pop()

    def visit_FuncCall(self, node: FuncCall):
        if node.name not in self.functions:
            self.error(f"Call to undeclared function '{node.name}'")
        func = self.functions[node.name]
        if len(node.args) != len(func.params):
            self.error(f"Function '{node.name}' expects {len(func.params)} arguments")
        # type check args
        for arg in node.args:
            self.visit(arg)
        # assume return type 'num' for simplicity
        return 'num'

    def visit_BinOp(self, node: BinOp):
        lt = self.visit(node.left)
        rt = self.visit(node.right)
        op = node.op.type
        # arithmetic
        if op in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH):
            if lt == 'num' and rt == 'num':
                return 'num'
            if op == TokenType.PLUS and lt == 'text' and rt == 'text':
                return 'text'
            self.error("Invalid operands for arithmetic")
        # comparisons
        if op in (TokenType.GT, TokenType.LT, TokenType.GTEQ, TokenType.LTEQ, TokenType.EQEQ, TokenType.NOTEQ):
            # allow num-num or text-text for == or !=
            if lt == rt:
                return 'bool'
            self.error("Type mismatch in comparison")
        self.error("Unknown binary op")

    def visit_UnaryOp(self, node: UnaryOp):
        et = self.visit(node.expr)
        if node.op.type == TokenType.MINUS:
            if et == 'num':
                return 'num'
            self.error("Unary minus on non-num")
        return et

    def visit_Literal(self, node: Literal):
        return node.lit_type

    def visit_Identifier(self, node: Identifier):
        sym = self.lookup_var(node.name)
        return sym.type
