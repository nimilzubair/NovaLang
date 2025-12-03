#include "lexer.hpp"
#include <cctype>
#include <stdexcept>
#include <unordered_map>

Lexer::Lexer(std::string s) : text(std::move(s)), pos(0), line(1), col(1) {}

char Lexer::peek() const { return pos < text.size() ? text[pos] : '\0'; }
char Lexer::peekNext() const { return pos + 1 < text.size() ? text[pos+1] : '\0'; }

char Lexer::advanceChar() {
    char c = peek();
    pos++;
    if (c == '\n') { line++; col = 1; }
    else col++;
    return c;
}

void Lexer::addToken(std::vector<Token>& toks, TokenType ttype, const std::string& val, int l, int c) {
    toks.emplace_back(ttype, val, l, c);
}

bool Lexer::startsWith(const std::string& s) const {
    if (pos + s.size() > text.size()) return false;
    return text.compare(pos, s.size(), s) == 0;
}

std::vector<Token> Lexer::tokenize() {
    std::vector<Token> toks;
    static const std::unordered_map<std::string, TokenType> kw = {
        {"start", TokenType::START}, {"end", TokenType::END}, {"show", TokenType::SHOW},
        {"take", TokenType::TAKE}, {"when", TokenType::WHEN}, {"elsewhen", TokenType::ELSEWHEN},
        {"else", TokenType::ELSE}, {"loop", TokenType::LOOP}, {"break", TokenType::BREAK},
        {"func", TokenType::FUNC}, {"back", TokenType::BACK}, {"num", TokenType::NUM},
        {"text", TokenType::TEXT}, {"flag", TokenType::FLAG}, {"to", TokenType::TO},
        {"true", TokenType::BOOL}, {"false", TokenType::BOOL}
    };

    while (pos < text.size()) {
        char c = peek();
        if (c == ' ' || c == '\t' || c == '\r') { advanceChar(); continue; }
        if (c == '\n') { advanceChar(); continue; }
        if (c == '#') { // comment
            while (peek() != '\n' && peek() != '\0') advanceChar();
            continue;
        }

        int start_line = line, start_col = col;

        // Numbers
        if (std::isdigit(c)) {
            std::string num;
            while (std::isdigit(peek())) num.push_back(advanceChar());
            addToken(toks, TokenType::NUMBER, num, start_line, start_col);
            continue;
        }

        // Identifiers / keywords / bools
        if (std::isalpha(c) || c == '_') {
            std::string id;
            while (std::isalnum(peek()) || peek() == '_') id.push_back(advanceChar());
            std::string lower = id;
            for (auto& ch : lower) ch = (char)std::tolower(ch);
            auto it = kw.find(lower);
            if (it != kw.end()) {
                TokenType tt = it->second;
                if (tt == TokenType::BOOL) {
                    addToken(toks, TokenType::BOOL, lower, start_line, start_col);
                } else {
                    addToken(toks, tt, lower, start_line, start_col);
                }
            } else {
                addToken(toks, TokenType::IDENT, id, start_line, start_col);
            }
            continue;
        }

        // Strings
        if (c == '"') {
            advanceChar(); // consume "
            std::string s;
            while (peek() != '"' && peek() != '\0') {
                char ch = advanceChar();
                if (ch == '\\' && peek() != '\0') {
                    char esc = advanceChar();
                    if (esc == 'n') s.push_back('\n');
                    else if (esc == '"') s.push_back('"');
                    else s.push_back(esc);
                } else s.push_back(ch);
            }
            if (peek() != '"') throw std::runtime_error("Unterminated string");
            advanceChar(); // consume closing "
            addToken(toks, TokenType::STRING, s, start_line, start_col);
            continue;
        }

        // Two-char ops
        if (startsWith("==")) { addToken(toks, TokenType::EQEQ, "==", start_line, start_col); advanceChar(); advanceChar(); continue; }
        if (startsWith("!=")) { addToken(toks, TokenType::NOTEQ, "!=", start_line, start_col); advanceChar(); advanceChar(); continue; }
        if (startsWith(">=")) { addToken(toks, TokenType::GTEQ, ">=", start_line, start_col); advanceChar(); advanceChar(); continue; }
        if (startsWith("<=")) { addToken(toks, TokenType::LTEQ, "<=", start_line, start_col); advanceChar(); advanceChar(); continue; }

        // Single char ops/punct
        switch (c) {
            case '+': addToken(toks, TokenType::PLUS, "+", start_line, start_col); advanceChar(); break;
            case '-': addToken(toks, TokenType::MINUS, "-", start_line, start_col); advanceChar(); break;
            case '*': addToken(toks, TokenType::STAR, "*", start_line, start_col); advanceChar(); break;
            case '/': addToken(toks, TokenType::SLASH, "/", start_line, start_col); advanceChar(); break;
            case '=': addToken(toks, TokenType::ASSIGN, "=", start_line, start_col); advanceChar(); break;
            case '>': addToken(toks, TokenType::GT, ">", start_line, start_col); advanceChar(); break;
            case '<': addToken(toks, TokenType::LT, "<", start_line, start_col); advanceChar(); break;
            case ',': addToken(toks, TokenType::COMMA, ",", start_line, start_col); advanceChar(); break;
            case '(' : addToken(toks, TokenType::LPAREN, "(", start_line, start_col); advanceChar(); break;
            case ')' : addToken(toks, TokenType::RPAREN, ")", start_line, start_col); advanceChar(); break;
            case '{' : addToken(toks, TokenType::LBRACE, "{", start_line, start_col); advanceChar(); break;
            case '}' : addToken(toks, TokenType::RBRACE, "}", start_line, start_col); advanceChar(); break;
            default:
                {
                    std::string msg = "Unexpected character: ";
                    msg.push_back(c);
                    throw std::runtime_error(msg);
                }
        }
    }

    addToken(toks, TokenType::EOF_T, "", line, col);
    return toks;
}
