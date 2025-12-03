#ifndef NOVA_TOKEN_HPP
#define NOVA_TOKEN_HPP

#include <string>
#include <ostream>

enum class TokenType {
    // Special
    EOF_T, IDENT, NUMBER, STRING, BOOL,

    // Keywords
    START, END, SHOW, TAKE, WHEN, ELSEWHEN, ELSE, LOOP, BREAK, FUNC, BACK,
    NUM, TEXT, FLAG, TRUE_T, FALSE_T,

    // Operators / punctuation
    PLUS, MINUS, STAR, SLASH,
    EQ, EQEQ, NOTEQ, GT, LT, GTEQ, LTEQ,
    ASSIGN, COMMA, LPAREN, RPAREN, LBRACE, RBRACE, TO
};

struct Token {
    TokenType type;
    std::string value;
    int line;
    int col;
    Token() : type(TokenType::EOF_T), value(""), line(0), col(0) {}
    Token(TokenType t, std::string v, int l, int c) : type(t), value(std::move(v)), line(l), col(c) {}
};

std::ostream& operator<<(std::ostream& os, const Token& t);

#endif // NOVA_TOKEN_HPP
