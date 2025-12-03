#include "semantic.hpp"
#include <stdexcept>
#include <typeinfo>

SemanticAnalyzer::SemanticAnalyzer() {
    scopes.emplace_back();
}

void SemanticAnalyzer::enter_scope() { scopes.emplace_back(); }
void SemanticAnalyzer::exit_scope() { if (!scopes.empty()) scopes.pop_back(); }

void SemanticAnalyzer::declare_var(const std::string& name, const std::string& type) {
    if (scopes.back().count(name)) throw SemanticError("Redeclaration of variable '" + name + "'");
    scopes.back().emplace(name, Symbol(name, type));
}

Symbol* SemanticAnalyzer::lookup_var(const std::string& name) {
    for (auto it = scopes.rbegin(); it != scopes.rend(); ++it) {
        if (it->count(name)) return &((*it)[name]);
    }
    throw SemanticError("Use of undeclared variable '" + name + "'");
    return nullptr;
}

void SemanticAnalyzer::analyze(ASTNode* node) {
    visit(node);
}

std::string SemanticAnalyzer::visit(ASTNode* node) {
    if (!node) return "";
    if (auto p = dynamic_cast<Program*>(node)) return visit_Program(p);
    if (auto v = dynamic_cast<VarDecl*>(node)) return visit_VarDecl(v);
    if (auto a = dynamic_cast<Assign*>(node)) return visit_Assign(a);
    if (auto s = dynamic_cast<Show*>(node)) return visit_Show(s);
    if (auto t = dynamic_cast<Take*>(node)) return visit_Take(t);
    if (auto w = dynamic_cast<When*>(node)) return visit_When(w);
    if (auto lp = dynamic_cast<Loop*>(node)) return visit_Loop(lp);
    if (dynamic_cast<Break*>(node)) return visit_Break(dynamic_cast<Break*>(node));
    if (auto f = dynamic_cast<FuncDef*>(node)) return visit_FuncDef(f);
    if (auto fc = dynamic_cast<FuncCall*>(node)) return visit_FuncCall(fc);
    if (auto b = dynamic_cast<BinOp*>(node)) return visit_BinOp(b);
    if (auto u = dynamic_cast<UnaryOp*>(node)) return visit_UnaryOp(u);
    if (auto l = dynamic_cast<Literal*>(node)) return visit_Literal(l);
    if (auto id = dynamic_cast<Identifier*>(node)) return visit_Identifier(id);

    throw SemanticError("Unhandled AST node in semantic analyzer");
}

std::string SemanticAnalyzer::visit_Program(Program* node) {
    for (auto &s : node->statements) visit(s.get());
    return "";
}

std::string SemanticAnalyzer::visit_VarDecl(VarDecl* node) {
    std::string expr_t = visit(node->expr.get());
    std::string declared = node->vartype;
    if (declared == "num" && expr_t != "num") throw SemanticError("Type mismatch: expected num");
    if (declared == "text" && expr_t != "text") throw SemanticError("Type mismatch: expected text");
    if (declared == "flag" && expr_t != "bool") throw SemanticError("Type mismatch: expected flag");
    declare_var(node->name, declared);
    return declared;
}

std::string SemanticAnalyzer::visit_Assign(Assign* node) {
    Symbol* s = lookup_var(node->name);
    std::string expr_t = visit(node->expr.get());
    if (s->type == "num" && expr_t != "num") throw SemanticError("Type mismatch in assignment to num");
    if (s->type == "text" && expr_t != "text") throw SemanticError("Type mismatch in assignment to text");
    if (s->type == "flag" && expr_t != "bool") throw SemanticError("Type mismatch in assignment to flag");
    return s->type;
}

std::string SemanticAnalyzer::visit_Show(Show* node) {
    return visit(node->expr.get());
}

std::string SemanticAnalyzer::visit_Take(Take* node) {
    Symbol* s = lookup_var(node->name);
    return s->type;
}

std::string SemanticAnalyzer::visit_When(When* node) {
    for (auto &c : node->cases) {
        std::string ct = visit(c.first.get());
        if (ct != "bool") throw SemanticError("When condition must be boolean");
        enter_scope();
        for (auto &s : c.second) visit(s.get());
        exit_scope();
    }
    if (!node->else_block.empty()) {
        enter_scope();
        for (auto &s : node->else_block) visit(s.get());
        exit_scope();
    }
    return "";
}

std::string SemanticAnalyzer::visit_Loop(Loop* node) {
    std::string s1 = visit(node->start_expr.get());
    std::string s2 = visit(node->end_expr.get());
    if (s1 != "num" || s2 != "num") throw SemanticError("Loop bounds must be num");
    enter_scope();
    declare_var(node->var, "num");
    in_loop++;
    for (auto &st : node->body) visit(st.get());
    in_loop--;
    exit_scope();
    return "";
}

std::string SemanticAnalyzer::visit_Break(Break* /*node*/) {
    if (in_loop == 0) throw SemanticError("break outside loop");
    return "";
}

std::string SemanticAnalyzer::visit_FuncDef(FuncDef* node) {
    if (functions.count(node->name)) throw SemanticError("Redeclaration of function '" + node->name + "'");
    functions.emplace(node->name, FunctionSymbol(node->name, node->params));
    enter_scope();
    for (auto &p : node->params) declare_var(p, "num"); // simplistic; mark params as num
    in_func++;
    for (auto &s : node->body) visit(s.get());
    std::string ret = visit(node->back_expr.get());
    in_func--;
    exit_scope();
    return "";
}

std::string SemanticAnalyzer::visit_FuncCall(FuncCall* node) {
    if (!functions.count(node->name)) throw SemanticError("Call to undeclared function '" + node->name + "'");
    const auto &fs = functions.at(node->name);
    if (fs.params.size() != node->args.size()) throw SemanticError("Function '" + node->name + "' called with incorrect number of arguments");
    for (auto &a : node->args) visit(a.get());
    return "num";
}

std::string SemanticAnalyzer::visit_BinOp(BinOp* node) {
    std::string lt = visit(node->left.get());
    std::string rt = visit(node->right.get());
    auto op = node->op_type;
    if (op == TokenType::PLUS || op == TokenType::MINUS || op == TokenType::STAR || op == TokenType::SLASH) {
        if (lt == "num" && rt == "num") return "num";
        if (op == TokenType::PLUS && lt == "text" && rt == "text") return "text";
        throw SemanticError("Invalid operands for arithmetic");
    }
    if (op == TokenType::GT || op == TokenType::LT || op == TokenType::GTEQ || op == TokenType::LTEQ || op == TokenType::EQEQ || op == TokenType::NOTEQ) {
        if (lt == rt) return "bool";
        throw SemanticError("Type mismatch in comparison");
    }
    throw SemanticError("Unknown binary op");
}

std::string SemanticAnalyzer::visit_UnaryOp(UnaryOp* node) {
    std::string et = visit(node->expr.get());
    if (node->op_type == TokenType::MINUS) {
        if (et == "num") return "num";
        throw SemanticError("Unary minus on non-num");
    }
    return et;
}

std::string SemanticAnalyzer::visit_Literal(Literal* node) {
    return node->lit_type;
}

std::string SemanticAnalyzer::visit_Identifier(Identifier* node) {
    Symbol* s = lookup_var(node->name);
    return s->type;
}
