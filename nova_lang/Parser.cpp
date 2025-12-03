// Parser.cpp — corrected version

#include "parser.hpp"
#include <sstream>
#include <stdexcept>

Parser::Parser(const std::vector<Token>& toks) : tokens(toks), i(0) {
    if (tokens.empty()) throw ParserError("Empty token stream");
}

const Token& Parser::current() const {
    if (i < tokens.size()) return tokens[i];
    static Token eof_t(TokenType::EOF_T, "", 0, 0);
    return eof_t;
}

Token Parser::advance() {
    if (i < tokens.size()) return tokens[i++];
    return Token(TokenType::EOF_T, "", tokens.back().line, tokens.back().col);
}

Token Parser::match(std::initializer_list<TokenType> types) {
    for (auto t : types) {
        if (current().type == t) {
            return advance();
        }
    }
    std::ostringstream ss;
    ss << "Expected token(s) at " << current().line << ":" << current().col;
    throw ParserError(ss.str());
}

std::unique_ptr<Program> Parser::parse() {
    match({TokenType::START});
    StmtList stmts = statements();
    match({TokenType::END});
    match({TokenType::EOF_T});
    return std::make_unique<Program>(std::move(stmts));
}

StmtList Parser::statements() {
    StmtList stmts;
    while (current().type != TokenType::END &&
           current().type != TokenType::RBRACE &&
           current().type != TokenType::EOF_T) {
        stmts.push_back(statement());
    }
    return stmts;
}

ASTNodePtr Parser::statement() {
    TokenType t = current().type;
    if (t == TokenType::NUM || t == TokenType::TEXT || t == TokenType::FLAG) return var_decl();
    else if (t == TokenType::IDENT) return assign_or_func_call();
    else if (t == TokenType::SHOW) return show_stmt();
    else if (t == TokenType::TAKE) return take_stmt();
    else if (t == TokenType::WHEN) return when_stmt();
    else if (t == TokenType::LOOP) return loop_stmt();
    else if (t == TokenType::BREAK) { match({TokenType::BREAK}); return std::make_unique<Break>(); }
    else if (t == TokenType::FUNC) return func_def();
    else {
        std::ostringstream ss; ss << "Unexpected token at " << current().line << ":" << current().col; 
        throw ParserError(ss.str());
    }
}

ASTNodePtr Parser::var_decl() {
    Token vt = match({TokenType::NUM, TokenType::TEXT, TokenType::FLAG});
    Token name = match({TokenType::IDENT});
    match({TokenType::ASSIGN});
    ASTNodePtr ex = expr();
    return std::make_unique<VarDecl>(vt.value, name.value, std::move(ex));
}

ASTNodePtr Parser::assign_or_func_call() {
    Token name = match({TokenType::IDENT});
    if (current().type == TokenType::ASSIGN) {
        match({TokenType::ASSIGN});
        ASTNodePtr e = expr();
        return std::make_unique<Assign>(name.value, std::move(e));
    } else if (current().type == TokenType::LPAREN) {
        match({TokenType::LPAREN});
        std::vector<ASTNodePtr> args;
        if (current().type != TokenType::RPAREN) {
            args.push_back(expr());
            while (current().type == TokenType::COMMA) { match({TokenType::COMMA}); args.push_back(expr()); }
        }
        match({TokenType::RPAREN});
        return std::make_unique<FuncCall>(name.value, std::move(args));
    } else {
        std::ostringstream ss; ss << "Expected assign or func-call at " << current().line << ":" << current().col; throw ParserError(ss.str());
    }
}

ASTNodePtr Parser::show_stmt() { match({TokenType::SHOW}); ASTNodePtr e = expr(); return std::make_unique<Show>(std::move(e)); }
ASTNodePtr Parser::take_stmt() { match({TokenType::TAKE}); Token id = match({TokenType::IDENT}); return std::make_unique<Take>(id.value); }

ASTNodePtr Parser::when_stmt() {
    // We'll collect cases as (condition ASTNodePtr, StmtList)
    std::vector<std::pair<ASTNodePtr, StmtList>> cases;
    StmtList else_block;

    Token when_tok = match({TokenType::WHEN});
    ASTNodePtr cond = expr();

    // block() returns ASTNodePtr (Program). Extract statements from it.
    ASTNodePtr block_node = block(when_tok);
    Program* prog = dynamic_cast<Program*>(block_node.get());
    if (!prog) throw ParserError("Internal parser error: expected Program node from block()");
    StmtList body = std::move(prog->statements);
    cases.emplace_back(std::move(cond), std::move(body));

    while (current().type == TokenType::ELSEWHEN) {
        Token t = match({TokenType::ELSEWHEN});
        ASTNodePtr cond2 = expr();
        ASTNodePtr block_node2 = block(t);
        Program* prog2 = dynamic_cast<Program*>(block_node2.get());
        if (!prog2) throw ParserError("Internal parser error: expected Program node from block()");
        StmtList b2 = std::move(prog2->statements);
        cases.emplace_back(std::move(cond2), std::move(b2));
    }

    if (current().type == TokenType::ELSE) {
        Token t = match({TokenType::ELSE});
        ASTNodePtr else_node = block(t);
        Program* prog_else = dynamic_cast<Program*>(else_node.get());
        if (!prog_else) throw ParserError("Internal parser error: expected Program node from block()");
        else_block = std::move(prog_else->statements);
    }

    return std::make_unique<When>(std::move(cases), std::move(else_block));
}

ASTNodePtr Parser::loop_stmt() {
    Token loop_t = match({TokenType::LOOP});
    Token var = match({TokenType::IDENT});
    match({TokenType::ASSIGN});
    ASTNodePtr s = expr();
    match({TokenType::TO});
    ASTNodePtr e = expr();

    ASTNodePtr block_node = block(loop_t);
    Program* prog = dynamic_cast<Program*>(block_node.get());
    if (!prog) throw ParserError("Internal parser error: expected Program node from block()");
    StmtList body = std::move(prog->statements);

    return std::make_unique<Loop>(var.value, std::move(s), std::move(e), std::move(body));
}

ASTNodePtr Parser::func_def() {
    match({TokenType::FUNC});
    Token name = match({TokenType::IDENT});
    match({TokenType::LPAREN});
    std::vector<std::string> params;
    if (current().type != TokenType::RPAREN) {
        params.push_back(match({TokenType::IDENT}).value);
        while (current().type == TokenType::COMMA) { match({TokenType::COMMA}); params.push_back(match({TokenType::IDENT}).value); }
    }
    match({TokenType::RPAREN});
    match({TokenType::LBRACE});
    StmtList body;
    ASTNodePtr back_expr;
    while (current().type != TokenType::BACK) {
        if (current().type == TokenType::RBRACE) throw ParserError("Function must contain a 'back' statement");
        body.push_back(statement());
    }
    match({TokenType::BACK});
    back_expr = expr();
    match({TokenType::RBRACE});
    return std::make_unique<FuncDef>(name.value, std::move(params), std::move(body), std::move(back_expr));
}

ASTNodePtr Parser::block(const Token& context_token) {
    if (current().type != TokenType::LBRACE) {
        std::ostringstream ss;
        ss << "Expected LBRACE at " << context_token.line << ":" << context_token.col << " (after '" << context_token.value << "')";
        throw ParserError(ss.str());
    }
    match({TokenType::LBRACE});
    StmtList stmts = statements();
    match({TokenType::RBRACE});
    // Return a Program node containing the block statements
    return std::make_unique<Program>(std::move(stmts));
}

// Expressions
ASTNodePtr Parser::expr() { return equality(); }

ASTNodePtr Parser::equality() {
    ASTNodePtr node = comparison();
    while (current().type == TokenType::EQEQ || current().type == TokenType::NOTEQ) {
        Token op = advance();
        ASTNodePtr right = comparison();
        node = std::make_unique<BinOp>(std::move(node), op.type, op.value, std::move(right));
    }
    return node;
}

ASTNodePtr Parser::comparison() {
    ASTNodePtr node = term();
    while (current().type == TokenType::GT || current().type == TokenType::LT || current().type == TokenType::GTEQ || current().type == TokenType::LTEQ) {
        Token op = advance();
        ASTNodePtr right = term();
        node = std::make_unique<BinOp>(std::move(node), op.type, op.value, std::move(right));
    }
    return node;
}

ASTNodePtr Parser::term() {
    ASTNodePtr node = factor();
    while (current().type == TokenType::PLUS || current().type == TokenType::MINUS) {
        Token op = advance();
        ASTNodePtr right = factor();
        node = std::make_unique<BinOp>(std::move(node), op.type, op.value, std::move(right));
    }
    return node;
}

ASTNodePtr Parser::factor() {
    ASTNodePtr node = unary();
    while (current().type == TokenType::STAR || current().type == TokenType::SLASH) {
        Token op = advance();
        ASTNodePtr right = unary();
        node = std::make_unique<BinOp>(std::move(node), op.type, op.value, std::move(right));
    }
    return node;
}

ASTNodePtr Parser::unary() {
    if (current().type == TokenType::MINUS) {
        Token op = advance();
        ASTNodePtr e = unary();
        return std::make_unique<UnaryOp>(op.type, op.value, std::move(e));
    }
    return primary();
}

ASTNodePtr Parser::primary() {
    Token t = current();
    if (t.type == TokenType::NUMBER) {
        advance();
        return std::make_unique<Literal>(t.value, "num");
    } else if (t.type == TokenType::STRING) {
        advance();
        return std::make_unique<Literal>(t.value, "text");
    } else if (t.type == TokenType::BOOL) {
        advance();
        return std::make_unique<Literal>(t.value, "bool");
    } else if (t.type == TokenType::IDENT) {
        advance();
        if (current().type == TokenType::LPAREN) {
            match({TokenType::LPAREN});
            std::vector<ASTNodePtr> args;
            if (current().type != TokenType::RPAREN) {
                args.push_back(expr());
                while (current().type == TokenType::COMMA) { match({TokenType::COMMA}); args.push_back(expr()); }
            }
            match({TokenType::RPAREN});
            return std::make_unique<FuncCall>(t.value, std::move(args));
        }
        return std::make_unique<Identifier>(t.value);
    } else if (t.type == TokenType::LPAREN) {
        match({TokenType::LPAREN});
        ASTNodePtr n = expr();
        match({TokenType::RPAREN});
        return n;
    }
    std::ostringstream ss; ss << "Unexpected token in expression at " << t.line << ":" << t.col; throw ParserError(ss.str());
}
