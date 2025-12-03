#include <iostream>
#include <fstream>
#include "lexer.hpp"
#include "parser.hpp"
#include "semantic.hpp"

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <file.nova>\n";
        return 1;
    }

    std::ifstream in(argv[1]);
    if (!in.is_open()) {
        std::cerr << "Cannot open file\n";
        return 1;
    }
    std::string source((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
    try {
        Lexer lx(source);
        auto tokens = lx.tokenize();
        std::cout << "Tokens: " << tokens.size() << "\n";
        // debug print:
        for (auto &t : tokens) std::cout << t << "\n";

        Parser p(tokens);
        auto ast = p.parse();
        std::cout << "Parsed AST\n";

        SemanticAnalyzer sem;
        sem.analyze(ast.get());
        std::cout << "Semantic analysis OK\n";

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
