## PyANAGRA
PyANAGRA is a tool designed to facilitate the analysis of context-free grammars and syntax analysis. This tool offers 
the ability to open and edit grammars written in Bison. It provides functionality to compute the first and follow sets,
perform common grammar transformations, and convert grammars to normal forms.

For LL(1) analysis, PyANAGRA displays the analysis table. For SLR, LR, and LALR analyses, presents the expanded 
grammar, along with the ACTION and GO TO tables, visual representation of the automaton and in text format.

Aditionally, provides an interactive simulation of inputs showcasing the evolution of the stack, input and triggered production and 
a graphical representation of syntax tree.

## Features
- Calculate First, First set of a sentence form and Follow set of a grammar
- Removal of unreacheable symbols of a grammar
- Removal of underivable non-terminals of a grammar
- Removal of left recursion of a grammar
- Removal of cycles of a grammar
- Removal of annulable symbols of a grammar
- Left factoring of a grammar
- Chomsky normal form
- Greibach normal form
- LL(1) Analysis analysis table
- SLR, LR, LALR analysis expanded grammar, automaton, action and go to table
- Simulate inputs interactive

![tablasSLR.png](..%2F..%2F..%2Fmemoria%2FtablasSLR.png)

![automataSLR.png](..%2F..%2F..%2Fmemoria%2FautomataSLR.png)

![arbol.png](..%2F..%2F..%2Fmemoria%2Farbol.png)
## Requirements
- PyQt5
- Networkx
- PyGraphviz
