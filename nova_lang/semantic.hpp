#ifndef NOVA_SEMANTIC_HPP
#define NOVA_SEMANTIC_HPP

#include "ast.hpp"
#include <string>
#include <map>

struct Symbol {
    std::string name;
    std::string type;
    Symbol() : name(""), type("unknown") {}
    Symbol(std::string n, std::string t) : name(std::move(n)), type(std::move(t)) {}
};

struct FunctionSymbol {
    std::string name;
    std::vector<std::string> params;
    FunctionSymbol() = default;
    FunctionSymbol(std::string n, std::vector<std::string> p) : name(std::move(n)), params(std::move(p)) {}
};

class SemanticError : public std::runtime_error { public: SemanticError(const std::string& s): std::runtime_error(s){} };

class SemanticAnalyzer {
private:
    std::vector<std::map<std::string, Symbol>> scopes;
    std::map<std::string, FunctionSymbol> functions;
    int in_loop = 0;
    int in_func = 0;
    void enter_scope();
    void exit_scope();
    void declare_var(const std::string& name, const std::string& type);
    Symbol* lookup_var(const std::string& name);
    std::string visit(ASTNode* node);
    // visitors
    std::string visit_Program(Program* node);
    std::string visit_VarDecl(VarDecl* node);
    std::string visit_Assign(Assign* node);
    std::string visit_Show(Show* node);
    std::string visit_Take(Take* node);
    std::string visit_When(When* node);
    std::string visit_Loop(Loop* node);
    std::string visit_Break(Break* node);
    std::string visit_FuncDef(FuncDef* node);
    std::string visit_FuncCall(FuncCall* node);
    std::string visit_BinOp(BinOp* node);
    std::string visit_UnaryOp(UnaryOp* node);
    std::string visit_Literal(Literal* node);
    std::string visit_Identifier(Identifier* node);
public:
    SemanticAnalyzer();
    void analyze(ASTNode* node);
};

#endif // NOVA_SEMANTIC_HPP
