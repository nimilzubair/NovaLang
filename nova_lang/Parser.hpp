#ifndef NOVA_PARSER_HPP
#define NOVA_PARSER_HPP

#include "token.hpp"
#include "ast.hpp"
#include <vector>
#include <memory>

class ParserError : public std::runtime_error { public: ParserError(const std::string& s): std::runtime_error(s){} };

class Parser {
private:
    const std::vector<Token>& tokens;
    size_t i = 0;
    const Token& current() const;
    Token advance();
    Token match(std::initializer_list<TokenType> types);
    // grammar helpers
    StmtList statements();
    ASTNodePtr statement();
    ASTNodePtr block(const Token& context_token);
    // productions
    ASTNodePtr var_decl();
    ASTNodePtr assign_or_func_call();
    ASTNodePtr show_stmt();
    ASTNodePtr take_stmt();
    ASTNodePtr when_stmt();
    ASTNodePtr loop_stmt();
    ASTNodePtr func_def();
    ASTNodePtr break_stmt();
    // expressions
    ASTNodePtr expr();
    ASTNodePtr equality();
    ASTNodePtr comparison();
    ASTNodePtr term();
    ASTNodePtr factor();
    ASTNodePtr unary();
    ASTNodePtr primary();
public:
    Parser(const std::vector<Token>& toks);
    std::unique_ptr<Program> parse();
};

#endif // NOVA_PARSER_HPP
