#ifndef NOVA_AST_HPP
#define NOVA_AST_HPP

#include <vector>
#include <memory>
#include <string>
#include "token.hpp"
struct ASTNode { virtual ~ASTNode() = default; };
using ASTNodePtr = std::unique_ptr<ASTNode>;
using StmtList = std::vector<ASTNodePtr>;

// Statements
struct Program : ASTNode {
    StmtList statements;
    Program(StmtList s = {}) : statements(std::move(s)) {}
};

struct VarDecl : ASTNode {
    std::string vartype;
    std::string name;
    ASTNodePtr expr;
    VarDecl(std::string vt, std::string n, ASTNodePtr e) : vartype(std::move(vt)), name(std::move(n)), expr(std::move(e)) {}
};

struct Assign : ASTNode {
    std::string name;
    ASTNodePtr expr;
    Assign(std::string n, ASTNodePtr e) : name(std::move(n)), expr(std::move(e)) {}
};

struct Show : ASTNode {
    ASTNodePtr expr;
    Show(ASTNodePtr e) : expr(std::move(e)) {}
};

struct Take : ASTNode {
    std::string name;
    Take(std::string n) : name(std::move(n)) {}
};

struct When : ASTNode {
    // pair: condition, statements
    std::vector<std::pair<ASTNodePtr, StmtList>> cases;
    StmtList else_block;
    When(std::vector<std::pair<ASTNodePtr, StmtList>> c = {}, StmtList e = {}) : cases(std::move(c)), else_block(std::move(e)) {}
};

struct Loop : ASTNode {
    std::string var;
    ASTNodePtr start_expr;
    ASTNodePtr end_expr;
    StmtList body;
    Loop(std::string v, ASTNodePtr s, ASTNodePtr e, StmtList b) : var(std::move(v)), start_expr(std::move(s)), end_expr(std::move(e)), body(std::move(b)) {}
};

struct Break : ASTNode {};

// Functions
struct FuncDef : ASTNode {
    std::string name;
    std::vector<std::string> params;
    StmtList body;
    ASTNodePtr back_expr;
    FuncDef(std::string n, std::vector<std::string> p, StmtList b, ASTNodePtr be) : name(std::move(n)), params(std::move(p)), body(std::move(b)), back_expr(std::move(be)) {}
};

struct FuncCall : ASTNode {
    std::string name;
    std::vector<ASTNodePtr> args;
    FuncCall(std::string n, std::vector<ASTNodePtr> a) : name(std::move(n)), args(std::move(a)) {}
};

// Expressions
struct BinOp : ASTNode {
    ASTNodePtr left;
    // store operator as token-ish string for simplicity
    TokenType op_type;
    std::string op_value;
    ASTNodePtr right;
    BinOp(ASTNodePtr l, TokenType ot, std::string ov, ASTNodePtr r) : left(std::move(l)), op_type(ot), op_value(std::move(ov)), right(std::move(r)) {}
};

struct UnaryOp : ASTNode {
    TokenType op_type;
    std::string op_value;
    ASTNodePtr expr;
    UnaryOp(TokenType ot, std::string ov, ASTNodePtr e) : op_type(ot), op_value(std::move(ov)), expr(std::move(e)) {}
};

struct Literal : ASTNode {
    std::string value;
    std::string lit_type; // "num","text","bool"
    Literal(std::string v, std::string t) : value(std::move(v)), lit_type(std::move(t)) {}
};

struct Identifier : ASTNode {
    std::string name;
    Identifier(std::string n) : name(std::move(n)) {}
};

#endif // NOVA_AST_HPP
