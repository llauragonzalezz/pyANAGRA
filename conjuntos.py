"""
Filename:
Author: Laura González Pizarro
Description:
"""

def calculate_first_set_token(token, recursive_tokens, terminal_tokens, non_terminal_tokens, productions):
    """
    Calculates the 'first' set of a given token in the context of a grammar.

    Parameters
    ----------
    token : str
        The token for which the 'first' set is being calculated.

    recursive_tokens : set
        A set containing tokens encountered during the current 'first' set calculation.
        This is used to prevent infinite recursion when calculating the 'first' set.

    terminal_tokens : set
        A set containing terminal tokens.

    non_terminal_tokens : set
        A set containing non-terminal tokens.

    productions : dict
        A dictionary representing the productions of the grammar.

    Returns
    -------
    set
        A set containing the 'first' set of the given token.
    """
    first_set = set()

    # Case token is a terminal token
    if token in terminal_tokens:
        first_set.add(token)
        return first_set

    # Case token has an epsilon-production
    if token in non_terminal_tokens and None in productions[token]:
        first_set.add(None)

    # Iterate over the production of a given token
    for production in productions[token]:
        # If
        if production is not None:
            epsilon = True
            # Iterate over tokens of a given production
            for index, token_prod in enumerate(production):
                # Stop if token_prod in recursive_tokens to prevent infinite recursion
                if token_prod not in recursive_tokens:
                    first_set_tok = calculate_first_set_token(token_prod, recursive_tokens | {token_prod}, terminal_tokens, non_terminal_tokens, productions)
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


def calculate_first_set(terminal_tokens, non_terminal_tokens, productions):
    """
    Calculates the 'first' set of all tokens in the context of a grammar.

    Parameters
    ----------
    terminal_tokens : set
        A set containing terminal tokens.

    non_terminal_tokens : set
        A set containing non-terminal tokens.

    productions : dict
        A dictionary representing the productions of the grammar.

    Returns
    -------
    dict
        A dictionary containing the 'first' set of all tokens of the grammar.
    """
    first_set = dict()
    for token in terminal_tokens | non_terminal_tokens:
        first_set[token] = calculate_first_set_token(token, {token}, terminal_tokens, non_terminal_tokens, productions)
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

def calculate_first_set_sentence(elements, terminal_tokens, non_terminal_tokens, productions):
    """
    Calculates the 'first' set of a given sentence form in the context of a grammar.

    Parameters
    ----------
    elements: set
        A set containing the tokens of the sentence form.

    token: str
        A string representing the left part of the production

    terminal_tokens : set
        A set containing terminal tokens.

    non_terminal_tokens : set
        A set containing non-terminal tokens.

    productions : dict
        A dictionary representing the productions of the grammar.

    Returns
    -------
    set
        A set containing the 'first' set of the given sentence form.
    """
    first_set = calculate_first_set(terminal_tokens, non_terminal_tokens, productions)
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


def calculate_follow_set(starting_token, terminal_tokens, non_terminal_tokens, productions):
    """
    Calculates the 'follow' set of all tokens in the context of a grammar.

    Parameters
    ----------
    starting_token: str
        The stating_token of the grammar

    terminal_tokens : set
        A set containing terminal tokens.

    non_terminal_tokens : set
        A set containing non-terminal tokens.

    productions : dict
        A dictionary representing the productions of the grammar.

    Returns
    -------
    dict
        A dictionary containing the 'follow' set of all tokens of the grammar.
    """
    old_follow_set = dict()
    follow_set = dict()
    follow_set[starting_token] = {"$"}
    first_set = calculate_first_set(terminal_tokens, non_terminal_tokens, productions)
    # While nothing is added to follow_set
    while follow_set != old_follow_set:
        old_follow_set = follow_set.copy()
        # Iterate over non-terminal tokens
        for token in non_terminal_tokens:
            # Iterate over the productions of a given token
            for production in productions[token]:
                # If it's not an epsilon production
                if production is not None:
                    # Iterate over the tokens of a given production
                    for index, token_prod in enumerate(production):
                        first_set_beta = set()
                        if token_prod in non_terminal_tokens: # A -> a B b
                            epsilon = True
                            # Calculate Pri(þ)
                            first_set_beta = calculate_first_set_sentence(production[index+1:], terminal_tokens, non_terminal_tokens, productions)

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
