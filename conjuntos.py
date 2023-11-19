"""
Filename:
Author: Laura González Pizarro
Description:
"""

def calculate_first_set_token(token, recursive_tokens, gr):
    """
    Calculates the 'first' set of a given symbol in the context of a grammar.

    Parameters
    ----------
    token : str
        The token for which the 'first' set is being calculated.

    recursive_tokens : set
        A set containing tokens encountered during the current 'first' set calculation.
        This is used to prevent infinite recursion when calculating the 'first' set.

    gr : Grammar
        A set containing the terminal symbols of the grammar.

    Returns
    -------
    set
        A set containing the 'first' set of the given token.
    """
    first_set = set()

    # Case token is a terminal token
    if token in gr.terminals:
        first_set.add(token)
        return first_set

    # Case token has an epsilon-production
    if token in gr.non_terminals and None in gr.productions[token]:
        first_set.add(None)

    # Iterate over the production of a given token
    for production in gr.productions[token]:
        # If
        if production is not None:
            epsilon = True
            # Iterate over tokens of a given production
            for index, token_prod in enumerate(production):
                # Stop if token_prod in recursive_tokens to prevent infinite recursion
                if token_prod not in recursive_tokens:
                    first_set_tok = calculate_first_set_token(token_prod, recursive_tokens | {token_prod}, gr)
                    first_set |= first_set_tok.difference({None})
                    if None not in first_set_tok:
                        epsilon = False
                        break
                else:
                    epsilon = False
                    break
            # Only add epsilon if all tokens have epsilon in their first set
            if epsilon:
                first_set |= {None}

    return first_set


def calculate_first_set(gr):
    """
    Calculates the 'first' set of all symbols in the context of a grammar.

    Parameters
    ----------
    gr : Grammar
        A set containing the terminal symbols of the grammar.

    Returns
    -------
    dict
        A dictionary containing the 'first' set of all symbols of the grammar.
    """
    first_set = dict()
    for token in gr.terminals | gr.non_terminals:
        first_set[token] = calculate_first_set_token(token, {token}, gr)
    return first_set


def calculate_first_set_sentence_fs(elements, first_set):
    """
        Calculates the 'first' set of a given sentence form in the context of a grammar.

        Parameters
        ----------
        elements: set
            A set containing the tokens of the sentence form.

        first_set : dict
            A dictionary containing the 'first' of the grammar.

        Returns
        -------
        set
            A set containing the 'first' set of the given sentence form.
        """
    first_set_sentence = set()
    epsilon = True
    # Iterate over elements of a given sentence form
    for element in elements:
        first_set_sentence |= first_set[element].difference({None})
        if None not in first_set[element]:
            epsilon = False
            break

    # Only add epsilon if all tokens have epsilon in their first set
    if epsilon:
        first_set_sentence.add(None)

    return first_set_sentence

def calculate_first_set_sentence(elements, gr):
    """
    Calculates the 'first' set of a given sentence form in the context of a grammar.

    Parameters
    ----------
    elements: set
        A set containing the tokens of the sentence form.

    terminal_tokens : set
        A set containing the terminal symbols of the grammar.

    non_terminal_tokens : set
        A set containing the non-terminal symbols of the grammar.

    productions : dict
        A dictionary representing the productions of the grammar.

    Returns
    -------
    set
        A set containing the 'first' set of the given sentence form.
    """
    first_set = calculate_first_set(gr)
    first_set_sentence = set()
    epsilon = True
    # Iterate over elements of a given sentence form
    for element in elements:
        first_set_sentence |= first_set[element].difference({None})
        if None not in first_set[element]:
            epsilon = False
            break

    # Only add epsilon if all tokens have epsilon in their first set
    if epsilon:
        first_set_sentence.add(None)

    return first_set_sentence


def calculate_follow_set(gr):
    """
    Calculates the 'follow' set of all tokens in the context of a grammar.
    Parameters
    ----------
    initial_token: str
        The initial token of the grammar

    terminals : set
        A set containing the terminal symbols of the grammar.

    non_terminals : set
        A set containing the non-terminal symbols of the grammar.

    productions : dict
        A dictionary representing the productions of the grammar.

    Returns
    -------
    dict
        A dictionary containing the 'follow' set of all symbols of the grammar.
    """

    old_follow_set = dict()
    follow_set = dict()
    follow_set[gr.initial_token] = {"$"}
    # While nothing is added to follow_set
    while follow_set != old_follow_set:
        old_follow_set = follow_set.copy()
        # Iterate over non-terminal tokens
        for token in gr.non_terminals:
            # Iterate over the productions of a given token
            for production in gr.productions[token]:
                # If it's not an epsilon production
                if production is not None:
                    # Iterate over the tokens of a given production
                    for index, token_prod in enumerate(production):
                        first_set_beta = set()
                        if token_prod in gr.non_terminals: # A -> a B b
                            # Calculate Pri(þ)
                            first_set_beta = calculate_first_set_sentence(production[index+1:], gr)

                            # Add Pri(b)\{e} to FOLLOW(B)
                            if token_prod in follow_set:
                                follow_set[token_prod] |= first_set_beta.difference({None})
                            else:
                                follow_set[token_prod] = first_set_beta.difference({None})

                            # Case A -> a B or A -> a B b and eps in PRI(b)
                            if index == len(production) or None in first_set_beta:
                                # Add FOLLOW(A) to FOLLOW(B)
                                if token_prod in follow_set and token in follow_set:
                                    follow_set[token_prod] |= follow_set[token]
                                elif token in follow_set:
                                    follow_set[token_prod] = follow_set[token]

    return follow_set
