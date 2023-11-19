import grammar

def extend_grammar(gr):
    initial_token_extended = gr.initial_token + "*"
    gr.productions[initial_token_extended] = [['.', gr.initial_token]]
    return grammar.Grammar(initial_token_extended, gr.terminals, {initial_token_extended} | gr.non_terminals, gr.productions)
