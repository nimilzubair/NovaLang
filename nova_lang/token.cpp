#include "token.hpp"
#include <iostream>

static std::string tokenTypeName(TokenType t) {
    switch (t) {
        case TokenType::EOF_T: return "EOF";
        case TokenType::IDENT: return "IDENT";
        case TokenType::NUMBER: return "NUMBER";
        case TokenType::STRING: return "STRING";
        case TokenType::BOOL: return "BOOL";
        case TokenType::START: return "START";
        case TokenType::END: return "END";
        case TokenType::SHOW: return "SHOW";
        case TokenType::TAKE: return "TAKE";
        case TokenType::WHEN: return "WHEN";
        case TokenType::ELSEWHEN: return "ELSEWHEN";
        case TokenType::ELSE: return "ELSE";
        case TokenType::LOOP: return "LOOP";
        case TokenType::BREAK: return "BREAK";
        case TokenType::FUNC: return "FUNC";
        case TokenType::BACK: return "BACK";
        case TokenType::NUM: return "NUM";
        case TokenType::TEXT: return "TEXT";
        case TokenType::FLAG: return "FLAG";
        case TokenType::TRUE_T: return "TRUE";
        case TokenType::FALSE_T: return "FALSE";
        case TokenType::PLUS: return "PLUS";
        case TokenType::MINUS: return "MINUS";
        case TokenType::STAR: return "STAR";
        case TokenType::SLASH: return "SLASH";
        case TokenType::EQ: return "EQ";
        case TokenType::EQEQ: return "EQEQ";
        case TokenType::NOTEQ: return "NOTEQ";
        case TokenType::GT: return "GT";
        case TokenType::LT: return "LT";
        case TokenType::GTEQ: return "GTEQ";
        case TokenType::LTEQ: return "LTEQ";
        case TokenType::ASSIGN: return "ASSIGN";
        case TokenType::COMMA: return "COMMA";
        case TokenType::LPAREN: return "LPAREN";
        case TokenType::RPAREN: return "RPAREN";
        case TokenType::LBRACE: return "LBRACE";
        case TokenType::RBRACE: return "RBRACE";
        case TokenType::TO: return "TO";
    }
    return "UNKNOWN";
}

std::ostream& operator<<(std::ostream& os, const Token& t) {
    os << tokenTypeName(t.type) << "('" << t.value << "') @" << t.line << ":" << t.col;
    return os;
}
