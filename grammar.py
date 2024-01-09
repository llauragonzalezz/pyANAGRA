"""
Filename:
Author: Laura González Pizarro
Description:
"""
import copy
import itertools
import conjuntos


class Grammar:

    def __init__(self, initial_token, terminals, non_terminals, productions):
        self.initial_token = initial_token
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions

    def copy(self):
        return Grammar(self.initial_token, self.terminals.copy(), self.non_terminals.copy(), copy.deepcopy(self.productions))

    def empty_languaje(self):
        gr = removal_underivable_non_terminals(self)
        return gr.productions[self.initial_token] == [[]]


    def has_cycles(self):
        for non_terminal in self.non_terminals:
            symbols = set(symbol for production in self.productions[non_terminal] if production is not None for symbol in production)
            if non_terminal in symbols:
                return True
            else:
                new_symbols = []
                while symbols != new_symbols:
                    for symbol in symbols & self.non_terminals:
                        new_symbols = symbols
                        new_symbols += set(symbol for production in self.productions[symbol] if production is not None for symbol in production)
                        if non_terminal in symbols:
                            return True
        return False


    def has_epsilon_productions(self):
        for non_terminal in self.non_terminals:
            if None in self.productions[non_terminal]:
                return True
        return False

    def has_no_terminals(self):
        old = set()
        new = set()
        for symbol in self.non_terminals:
            for production in self.productions[symbol]:
                if production is None or set(production) <= self.terminals:
                    new |= set(symbol)

        while old != new:
            old = new
            # Add all non-terminals that have at least one production made of all terminals or an epsilon production
            for symbol in self.non_terminals:
                for production in self.productions[symbol]:
                    if production is None or set(production) <= self.terminals | old:
                        new |= set(symbol)

        return new != self.non_terminals, self.non_terminals - new



def removal_unreachable_terminals(grammar):
    """
    Removes unreachable terminals of a given grammar

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
        A modified grammar after removing unreachable terminals.
    """
    gr = grammar.copy()
    old = set()
    new = set(symbol for production in gr.productions[gr.initial_token] if production is not None for symbol in production) | set(gr.initial_token)

    while old != new:
        new_symbols = new.difference(old)
        old = new

        # iterate over new sumbols
        for symbol in new_symbols:
            if symbol in gr.non_terminals:
                # add all terminal and non-terminal symbols that we can reach
                new |= set(symbol for production in gr.productions[symbol] if production is not None for symbol in production)

    # update terminals and non-terminal sets
    gr.terminals &= new
    # remove all unreachable non-terminals
    unreachable_symbols = gr.non_terminals.difference(new)
    gr.non_terminals &= set(symbol for symbol in new if symbol in gr.non_terminals)

    # keep productions of reachable non-terminals
    gr.productions = {key: value for key, value in gr.productions.items() if key not in unreachable_symbols}

    return gr


def removal_underivable_non_terminals(grammar):
    """
    Removes underivable non terminals of a given grammar

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
        A modified grammar after removing underivable non terminals.
    """
    gr = grammar.copy()

    old = set(gr.initial_token)
    new = set()

    # Add all non-terminals that have at least one production made of all terminals or an epsilon production
    for symbol in gr.non_terminals:
        for production in gr.productions[symbol]:
            if production is None or set(production) <= gr.terminals:
                new |= set(symbol)

    while old != new:
        old = new
        # Add all non-terminals that have at least one production made of all terminals or an epsilon production
        for symbol in gr.non_terminals:
            for production in gr.productions[symbol]:
                if production is None or set(production) <= gr.terminals | old:
                    new |= set(symbol)

    # Keep all productions made of elements in new or terminal symbols
    new_productions = dict()
    for symbol in new:
        productions_list = []
        for production in gr.productions[symbol]:
            if production is None or set(production) <= new | gr.terminals:
                productions_list.append(production)

        new_productions[symbol] = productions_list

    # In this case, the initial token is underivable, therefore, it produces the empty language
    if gr.initial_token not in new:
        new.add(gr.initial_token)
        new_productions[gr.initial_token] = [[]]

    return Grammar(gr.initial_token, gr.terminals, new, new_productions)


def removal_left_recursion(grammar):
    """
    Removes left recursion of a given grammar

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
        A modified grammar after removing left recursion(direct and indirect).

    list
        A sorted list of the non-terminals of the grammar.
    """
    gr = grammar.copy()

    nt_symbols = list(gr.non_terminals)

    # Change position of initial token to be the first one in the list
    if nt_symbols.index(gr.initial_token) != 0:
        pos_initial_token = nt_symbols.index(gr.initial_token)
        nt_symbols[pos_initial_token], nt_symbols[0] = nt_symbols[0], nt_symbols[pos_initial_token]

    # Dada una lista de tokens ponemos sus productions en funcion de tokens que esten anterior a este en la lista
    for i, symbol_i in enumerate(nt_symbols):
        if i > 0:
            for j, symbol_j in enumerate(nt_symbols[:i-1]):
                for production in gr.productions[symbol_i]:
                    # Si el primer token de la producción es un token anterior al de la parte izquierda de la producción
                    # lo sustituimos por todas las producciónes del token
                    if production is not None and production[0] == symbol_j:
                        print(gr.productions[symbol_i])
                        gr.productions[symbol_i].remove(production)
                        print(gr.productions[symbol_i])
                        for production_to_remplace in gr.productions[symbol_j]:
                            if production_to_remplace is None and production[1:] == []:
                                gr.productions[symbol_i].append(None)
                            elif production_to_remplace is None:
                                gr.productions[symbol_i].append(production[1:])
                            else:
                                gr.productions[symbol_i].append(production_to_remplace + production[1:])

        # Eliminamos la recursividad a izquierda directa que se haya podido generar
        gr = removal_direct_left_recursion(gr, symbol_i)

    print(gr.productions)
    return gr, nt_symbols


def removal_direct_left_recursion(grammar, symbol):
    """
    Removes direct left recursion from the given non-terminal symbol in the grammar

    Parameters
    ----------
    grammar: Grammar

    symbol: str
        The symbol for which direct left recursion needs to be removed.

    Returns
    -------
    Grammar
        A modified grammar after removing direct left recursion for the given symbol.
    """
    gr = grammar.copy()
    recursive_productions = list()
    non_recursive_productions = list()

    # There is direct left recursion if the first symbol of the production is the same as the left part of the production
    for production in gr.productions[symbol]:
        if production is not None and production[0] == symbol:
            recursive_productions.append(production[1:])
        else:
            non_recursive_productions.append(production)

    if recursive_productions != []:
        gr.productions[symbol].clear()
        # Create the symbol that removes the left recursion of the given symbol
        name = symbol + "_rec"
        gr.non_terminals.add(name)
        gr.productions[name] = [None]

        # Add to the new symbol the productions with left recursion so that it becomes right recursion
        for prod in recursive_productions:
            gr.productions[name].append(prod + [name])

        # Add to the symbol productions the rules that did not have recursion
        for prod in non_recursive_productions:
            gr.productions[symbol].append(prod + [name])

    return gr


def is_nullable(gr, symbol):
    """
    Checks if a symbol is nullable in the given grammar.

    Parameters
    ----------
    gr: Grammar

    symbol: str
        The symbol to check for nullability.

    Returns
    -------
    bool
        True if symbol is nullable. False otherwise
    """
    # symbol derivates epsilon (direct)
    if None in gr.productions[symbol]:
        return True

    # symbol =>* epsilon (indirect)
    for production in gr.productions[symbol]:
        if None in conjuntos.calculate_first_set_sentence(production, gr):
            return True

    return False



def removal_epsilon_productions(grammar):
    """
    Removes direct left recursion of a given grammar

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
        A modified grammar after removing direct left recursion.
    """
    gr = grammar.copy()

    # Calculates the set of nullable symbols
    nullable_tokens = {symbol for symbol in gr.non_terminals if is_nullable(gr, symbol)}
    for symbol in gr.non_terminals:
        if symbol in nullable_tokens and None in gr.productions[symbol]:
            gr.productions[symbol].remove(None)  # Remove epsilon-prod

        for production in gr.productions[symbol]:
            # Calculate nullable symbols in the production
            nullable_tokens_production = set(production) & nullable_tokens
            indexs_token_nullable = {production.index(null_token) for null_token in nullable_tokens_production}
            combinations = []

            # All possible combinations of the nullable symbol index
            for i in range(1, len(indexs_token_nullable) + 1):
                combinations.extend(list(x) for x in itertools.combinations(indexs_token_nullable, i))

            if len(nullable_tokens_production) == len(production):
                combinations.remove([*range(len(production))])

            # Add to the symbol productions all the possible combinations of occurrences of the nullable tokens in the production
            for combination in combinations:
                new_production = [x for i, x in enumerate(production) if i not in combination]
                if new_production not in gr.productions[symbol]:
                    gr.productions[symbol].append(new_production)

    return gr


def remove_unit_productions(grammar, symbol):
    """
    Removes unit productions of a given non-terminal symbol.

    Parameters
    ----------
    grammar: Grammar

    symbol: str
        The non-terminal symbol for which unit productions should be removed.

    Returns
    -------
    Grammar
        A modified grammar after removing unit productions of the given non-terminal.
    """
    gr = grammar.copy()

    old = set()
    new = set()

    # Add all symbols that are unit productions
    for production in gr.productions[symbol]:
        if production is not None and len(production) == 1 and production[0] in gr.non_terminals:
            gr.productions[symbol].remove(production)  # delete unit production
            new.add(production[0])

    while old != new:
        new_symbols = new.difference(old)
        old = new.copy()

        # Iterate over new tokens
        for new_symbol in new_symbols:
            added = False

            for production in gr.productions[new_symbol]:
                # Add all unit prodcutions that can be reached from a token.
                if production is not None and len(production) == 1 and production[0] in gr.non_terminals:
                    new.add(production[0])
                elif not added:
                    added = True
                    # For the grammar to be equivalent after eliminating the unit production, it is necessary to add
                    # all non-unit productions from the token of the unit production.
                    for production_to_add in gr.productions[new_symbol]:
                        if (len(production_to_add) > 1 or (len(production_to_add) == 1 and production_to_add[0] in gr.terminals)) and production_to_add not in gr.productions[symbol]:
                            gr.productions[symbol].append(production_to_add)

    return gr


def removal_cycles(grammar):
    """
    Removes cycles of a given grammar

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
        A modified grammar after removing cycles.
    """
    gr = grammar.copy()

    gr = removal_epsilon_productions(gr)

    gr = removal_underivable_non_terminals(gr)

    # Remove all unit productions of each non-terminal, therefore removing all possible cycles
    for symbol in gr.non_terminals:
        gr = remove_unit_productions(gr, symbol)

    return gr


def removal_nonsolitary_terminals(grammar):
    """
    Removes non-solitary terminal productions of a given grammar

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
        A modified grammar after removing cycles.
    """
    gr = grammar.copy()

    # Create productions for terminal-symbol
    for token in gr.terminals:
        name = "token_" + token
        gr.productions[name] = [[token]] # token_A -> A
        gr.non_terminals.add(name)

    # Remplace all terminals in productions with the previous productions
    for token in gr.non_terminals:
        for production in gr.productions[token]:
            if production is not None and len(production) > 1:
                for index, token_prod in enumerate(production):
                    if token_prod in gr.terminals:
                        production[index] = "token_" + token_prod

    return gr


def eliminate_long_productions(grammar):
    """
    Eliminates right-hand sides with more than 2 nonterminals in a grammar.

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
         A modified grammar after grouping productions into pairs.
    """
    gr = grammar.copy()

    chomsky_index = 1
    nt_tokens = gr.non_terminals.copy()
    # for each non-terminal
    for symbol in gr.non_terminals:
        # for each production
        for index, production in enumerate(gr.productions[symbol]):
            # if the production lenght is > 2 => group production
            if production is not None and len(production) > 2:
                new_production = "Chom_"+str(chomsky_index) #
                chomsky_index += 1
                nt_tokens.add(new_production)  # Add new non-terminal
                gr.productions[symbol][index] = [production[0], new_production]  # Change production of symbol
                last_symbol = new_production
                for token_prod in production[1:-2]:
                    new_production = "Chom_" + str(chomsky_index)
                    chomsky_index += 1
                    nt_tokens.add(new_production)  # Add new non-terminal
                    # Create production for new non-terminal (last_symbol)
                    gr.productions[last_symbol] = [[token_prod, new_production]]
                    last_symbol = new_production

                # Create production for new non-terminal (last_symbol)
                gr.productions[last_symbol] = [production[-2:]]

    return Grammar(gr.initial_token, gr.terminals, nt_tokens, gr.productions)


def chomsky_normal_form(grammar):
    """
    Tranform grammar into Chomsky normal form.

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
         A modified grammar after transforming into Chomsky normal form.
    """
    gr = grammar.copy()
    # Step 1: remove epilon productions
    gr = removal_epsilon_productions(gr)
    # Step 2: remove cycles
    gr = removal_cycles(gr)
    # Step 3: remove left recursion
    gr, _ = removal_left_recursion(gr)
    # Step 4: remove non-solitary terminals in productions
    gr = removal_nonsolitary_terminals(gr)
    # Step 5: eliminate long productions
    gr = eliminate_long_productions(gr)

    return gr


def left_factoring(grammar):
    """
    Tranform grammar into Chomsky normal form.

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
         A modified grammar after transforming into Chomsky normal form.
    """
    gr = grammar.copy()

    old_non_terminals = gr.non_terminals
    # for each non-terminal
    for symbol in old_non_terminals:
        old_productions = gr.productions[symbol].copy()
        times = 1
        # for each production
        for production in old_productions:
            if production in gr.productions[symbol] and production is not None and len(gr.productions[symbol]) > 1: # sino esta es que se ha reducido en alguna iteracion anterior
                # left factorize production by finding longest sufix in productions[symbol]
                gr, times = find_prefix(production, gr.productions[symbol], symbol, times, "_" + str(times), gr)

    return gr


def different_productions(reference_string, c_string):
    """
    Check if two strings represent different productions.

    Parameters
    ----------
    reference_string : str
        The reference string for comparison.

    c_string : str
        The string to compare with the reference.

    Returns
    -------
    Grammar
         True if the strings represent different productions, False otherwise.
    """
    return c_string is None or c_string == [] or reference_string[0] != c_string[0]



def find_prefix(reference_string, new_productions, name_prod, times, sufix, grammar):
    """
    Find the longest prefix in the given context.

    Parameters
    ----------
    reference_string : str
        The reference string used for finding the prefix.

    new_productions : List[str]
        List of new productions to consider.

    name_prod : str
        The name of the production to be modified.

    times : int
        The number of times to apply the modification.

    suffix : str
        The suffix to be added to the modified production.

    grammar : Grammar

    Returns
    -------
    Grammar
        A modified grammar after finding and applying the prefix.
    """
    gr = grammar.copy()

    prefix_productions = list()
    different = False
    # for each character in the reference string
    for index, character in enumerate(reference_string):
        for new_production in new_productions:
            # The moment when non-different strings does not match, the common prefix has been calculated.
            if not different_productions(reference_string, new_production) and (len(new_production) < index + 1 or character != new_production[index]):
                different = True
            elif not different_productions(reference_string, new_production) and character == new_production[index] and new_production not in prefix_productions:
                prefix_productions.append(new_production)

        if prefix_productions == []:  # There is not a common prefix
            return gr, times

        if different: # Left factorize
            # We add a non-terminal token that groups all productions with a common suffix.
            name = name_prod + sufix
            sufix = "'"
            # The productions of the new token contain all common strings without the prefix.
            gr.productions[name] = [prod[index:] for prod in prefix_productions]
            gr.non_terminals.add(name)
            # Replace productions with a prefix with one that is the "prefix + new token".
            new_productions.append(reference_string[:index] + [name])
            for prefix_prod in prefix_productions:
                new_productions.remove(prefix_prod)

            gr.productions[name_prod] = new_productions
            # Left factorize over the new token.
            gr, _ = find_prefix(gr.productions[name][0], gr.productions[name], name, 0, sufix, gr)
            return gr, times + 1

    return gr, times


def greibach_normal_form(grammar): # FIXME
    """
    Tranform grammar into Greibach normal form.

    Parameters
    ----------
    grammar: Grammar

    Returns
    -------
    Grammar
         A modified grammar after transforming into Greibach normal form.
    """
    gr = grammar.copy()

    # Step 1: remove left recursion
    gr, nt_tokens = removal_left_recursion(gr)
    # Step 1: remove cycles
    gr = removal_cycles(gr)

    # En el orden inverso al elegido para eliminar la recursividad a izquierda eliminamos todas las productions que
    # empiecen por no terminal
    for symbol in reversed(nt_tokens):
        productions_to_remove = []
        for production in gr.productions[symbol]:
            if production is not None and production[0] in gr.non_terminals:
                productions_to_remove.append(production)
                # Sustituimos en la producción el primer token por todas las productions que tiene
                for production_to_remplace in gr.productions[production[0]]:
                    print(production_to_remplace, production[1:])
                    if production_to_remplace is None and production[1:] == []:
                        gr.productions[symbol].append(None)
                    elif production_to_remplace is None:
                        gr.productions[symbol].append(production[1:])
                    else:
                        gr.productions[symbol].append(production_to_remplace + production[1:])

        for production in productions_to_remove:
            gr.productions[symbol].remove(production)

    # Eliminamos todas las productions que empiecen por no terminal de los tokens que se han añadido a la hora de
    # eliminar la recursividad a izquierda
    new_symbols = gr.non_terminals.difference(set(nt_tokens))
    for symbol in new_symbols:
        productions_to_remove = []
        for production in gr.productions[symbol]:
            if production is not None and production[0] in gr.non_terminals:
                productions_to_remove.append(production)
                # Sustituimos en la producción el primer token por todas las productions que tiene
                for production_to_remplace in gr.productions[production[0]]:
                    gr.productions[symbol].append(production_to_remplace + production[1:])
        for production in productions_to_remove:
            gr.productions[symbol].remove(production)

    return gr
