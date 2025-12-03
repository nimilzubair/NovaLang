#ifndef NOVA_LEXER_HPP
#define NOVA_LEXER_HPP

#include "token.hpp"
#include <string>
#include <vector>

class Lexer {
private:
    std::string text;
    size_t pos = 0;
    int line = 1;
    int col = 1;
    char peek() const;
    char peekNext() const;
    char advanceChar();
    void addToken(std::vector<Token>& toks, TokenType ttype, const std::string& val, int l, int c);
    bool startsWith(const std::string& s) const;
public:
    Lexer(std::string s);
    std::vector<Token> tokenize();
};

#endif // NOVA_LEXER_HPP
