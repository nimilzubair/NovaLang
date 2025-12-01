"""
Recursive descent parser for NovaLang
"""

from .token import TokenType
from .ast_nodes import *

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.current = tokens[0]

    def advance(self):
        self.i += 1
        if self.i < len(self.tokens):
            self.current = self.tokens[self.i]
        return self.current

    def match(self, *types):
        if self.current.type in types:
            t = self.current
            self.advance()
            return t
        expected = ', '.join(t.name for t in types)
        raise ParserError(f"Expected {expected} at line {self.current.line}, col {self.current.col}, got {self.current.type}")

    def parse(self):
        # Expect start ... end
        self.match(TokenType.START)
        statements = self.statements()
        self.match(TokenType.END)
        self.match(TokenType.EOF)
        return Program(statements)

    def statements(self):
        stmts = []
        while self.current.type not in (TokenType.END, TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.statement())
        return stmts

    def statement(self):
        t = self.current.type
        if t in (TokenType.NUM, TokenType.TEXT, TokenType.FLAG):
            return self.var_decl()
        elif t == TokenType.IDENT:
            return self.assign_or_func_call()
        elif t == TokenType.SHOW:
            return self.show_stmt()
        elif t == TokenType.TAKE:
            return self.take_stmt()
        elif t == TokenType.WHEN:
            return self.when_stmt()
        elif t == TokenType.LOOP:
            return self.loop_stmt()
        elif t == TokenType.BREAK:
            self.match(TokenType.BREAK)
            return Break()
        elif t == TokenType.FUNC:
            return self.func_def()
        else:
            raise ParserError(f"Unexpected token {self.current.type} at line {self.current.line}")

    def var_decl(self):
        vartype_token = self.match(TokenType.NUM, TokenType.TEXT, TokenType.FLAG)
        vartype = vartype_token.value
        name = self.match(TokenType.IDENT).value
        self.match(TokenType.ASSIGN)
        expr = self.expr()
        return VarDecl(vartype, name, expr)

    def assign_or_func_call(self):
        name = self.match(TokenType.IDENT).value
        if self.current.type == TokenType.ASSIGN:
            self.match(TokenType.ASSIGN)
            expr = self.expr()
            return Assign(name, expr)
        elif self.current.type == TokenType.LPAREN:
            # func call
            self.match(TokenType.LPAREN)
            args = []
            if self.current.type != TokenType.RPAREN:
                args.append(self.expr())
                while self.current.type == TokenType.COMMA:
                    self.match(TokenType.COMMA)
                    args.append(self.expr())
            self.match(TokenType.RPAREN)
            return FuncCall(name, args)
        else:
            raise ParserError(f"Expected assignment or func call at line {self.current.line}")

    def show_stmt(self):
        self.match(TokenType.SHOW)
        expr = self.expr()
        return Show(expr)

    def take_stmt(self):
        self.match(TokenType.TAKE)
        name = self.match(TokenType.IDENT).value
        return Take(name)

    def when_stmt(self):
        cases = []
        else_block = None

        # when cond { stmts }
        self.match(TokenType.WHEN)
        cond = self.expr()
        block = self.block()
        cases.append((cond, block))

        # elsewhen*
        while self.current.type == TokenType.ELSEWHEN:
            self.match(TokenType.ELSEWHEN)
            cond = self.expr()
            block = self.block()
            cases.append((cond, block))

        # else optional
        if self.current.type == TokenType.ELSE:
            self.match(TokenType.ELSE)
            else_block = self.block()

        return When(cases, else_block)

    def loop_stmt(self):
        self.match(TokenType.LOOP)
        var = self.match(TokenType.IDENT).value
        self.match(TokenType.ASSIGN)
        start_expr = self.expr()
        self.match(TokenType.TO)
        end_expr = self.expr()
        body = self.block()
        return Loop(var, start_expr, end_expr, body)

    def func_def(self):
        self.match(TokenType.FUNC)
        name = self.match(TokenType.IDENT).value
        self.match(TokenType.LPAREN)
        params = []
        if self.current.type != TokenType.RPAREN:
            params.append(self.match(TokenType.IDENT).value)
            while self.current.type == TokenType.COMMA:
                self.match(TokenType.COMMA)
                params.append(self.match(TokenType.IDENT).value)
        self.match(TokenType.RPAREN)
        # body { stmts back expr }
        self.match(TokenType.LBRACE)
        body = []
        back_expr = None
        while self.current.type != TokenType.BACK:
            if self.current.type == TokenType.RBRACE:
                raise ParserError("Function must contain a 'back' statement")
            body.append(self.statement())
        self.match(TokenType.BACK)
        back_expr = self.expr()
        self.match(TokenType.RBRACE)
        return FuncDef(name, params, body, back_expr)

    def block(self):
        self.match(TokenType.LBRACE)
        stmts = self.statements()
        self.match(TokenType.RBRACE)
        return stmts

    # Expression grammar:
    # expr -> equality
    def expr(self):
        return self.equality()

    def equality(self):
        node = self.comparison()
        while self.current.type in (TokenType.EQEQ, TokenType.NOTEQ):
            op = self.current
            self.advance()
            right = self.comparison()
            node = BinOp(node, op, right)
        return node

    def comparison(self):
        node = self.term()
        while self.current.type in (TokenType.GT, TokenType.LT, TokenType.GTEQ, TokenType.LTEQ):
            op = self.current
            self.advance()
            right = self.term()
            node = BinOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while self.current.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current
            self.advance()
            right = self.factor()
            node = BinOp(node, op, right)
        return node

    def factor(self):
        node = self.unary()
        while self.current.type in (TokenType.STAR, TokenType.SLASH):
            op = self.current
            self.advance()
            right = self.unary()
            node = BinOp(node, op, right)
        return node

    def unary(self):
        if self.current.type in (TokenType.MINUS,):
            op = self.current
            self.advance()
            expr = self.unary()
            return UnaryOp(op, expr)
        return self.primary()

    def primary(self):
        t = self.current
        if t.type == TokenType.NUMBER:
            self.advance()
            return Literal(int(t.value), 'num')
        elif t.type == TokenType.STRING:
            self.advance()
            return Literal(t.value.strip('"'), 'text')
        elif t.type == TokenType.BOOL:
            self.advance()
            return Literal(True if t.value == 'true' else False, 'bool')
        elif t.type == TokenType.IDENT:
            # Could be func call
            name = t.value
            self.advance()
            if self.current.type == TokenType.LPAREN:
                # call
                self.match(TokenType.LPAREN)
                args = []
                if self.current.type != TokenType.RPAREN:
                    args.append(self.expr())
                    while self.current.type == TokenType.COMMA:
                        self.match(TokenType.COMMA)
                        args.append(self.expr())
                self.match(TokenType.RPAREN)
                return FuncCall(name, args)
            return Identifier(name)
        elif t.type == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            node = self.expr()
            self.match(TokenType.RPAREN)
            return node
        else:
            raise ParserError(f"Unexpected token {t.type} at line {t.line}")
