def calculate_first_set_token(token, recursive_tokens, terminal_tokens, non_terminal_tokens, productions):
    first_set = set()

    if token in terminal_tokens:
        first_set.add(token)
        return first_set

    if token in non_terminal_tokens and None in productions[token]:
        first_set.add(None)

    for production in productions[token]:
        if production is not None:
            epsilon = True
            for token_prod in production:
                if token_prod not in recursive_tokens:
                    first_set_tok = calculate_first_set_token(token_prod, recursive_tokens | {token_prod}, terminal_tokens, non_terminal_tokens, productions)
                    first_set |= first_set_tok.difference({None})
                    if None not in first_set_tok:
                        epsilon = False
                        break
            if epsilon:
                first_set |= {None}

    return first_set


def calculate_first_set(terminal_tokens, non_terminal_tokens, productions):
    first_set = dict()
    for token in terminal_tokens | non_terminal_tokens:
        print("Llamo a PRI(", token, ") con", {token})
        first_set[token] = calculate_first_set_token(token, {token}, terminal_tokens, non_terminal_tokens, productions)
    return first_set


def calculate_follow_set(starting_token, terminal_tokens, non_terminal_tokens, productions):
    siguiente_viejo = dict()
    follow_set = dict()
    follow_set[starting_token] = {"$"}
    while follow_set != siguiente_viejo:
        siguiente_viejo = follow_set.copy()
        for token in non_terminal_tokens:
            for production in productions[token]:
                if production is not None:
                    for index, token_prod in enumerate(production):
                        first_set_beta = set()
                        if token_prod in non_terminal_tokens: # A -> a B b
                            epsilon = True
                            # Calculate Pri(þ)
                            for t in production[index+1:]:
                                first_set_tok = calculate_first_set_token(t, set(t), terminal_tokens, non_terminal_tokens, productions)
                                first_set_beta |= first_set_tok.difference({None})
                                if None not in first_set_tok:
                                    epsilon = False
                                    break

                            if epsilon:
                                first_set_beta |= {None}

                            if token_prod in follow_set:
                                follow_set[token_prod] |= first_set_beta.difference({None})
                            else:
                                follow_set[token_prod] = first_set_beta.difference({None})

                            if index == len(production) or None in first_set_beta:  # A -> a B  or A -> a B b con eps in PRI(b)
                                if token_prod in follow_set and token in follow_set:
                                    follow_set[token_prod] |= follow_set[token]
                                elif token in follow_set:
                                    follow_set[token_prod] = follow_set[token]

    return follow_set


def calculate_table(starting_token, terminal_tokens, non_terminal_tokens, productions):
    follow_set = calculate_follow_set(starting_token, terminal_tokens, non_terminal_tokens, productions)
    table = dict()

    for non_terminal_token in non_terminal_tokens:
        for token_terminal in terminal_tokens | {"$"}:
            table[non_terminal_token, token_terminal] = []

    for token in non_terminal_tokens:
        for production in productions[token]:
            first_set_token = set()
            if production is not None:
                epsilon = True
                for t in production:
                    first_set = calculate_first_set_token(t, set(t), terminal_tokens, non_terminal_tokens, productions)
                    first_set_token |= first_set.difference({None})
                    if None not in first_set:
                        epsilon = False
                        break

                if epsilon:
                    first_set_token |= {None}
            else:
                first_set_token = {None}

            for elemento in first_set_token & terminal_tokens:
                #print("table[", token, ",", elemento, "] = ", production)
                table[token, elemento].append(production)

            if None in first_set_token:
                for b in terminal_tokens & follow_set[token]:
                    table[token, b].append(production)
                if "$" in follow_set[token]:
                    table[token, "$"].append(production)

    for non_terminal_token in non_terminal_tokens:
        for token_terminal in terminal_tokens | {"$"}:
            if table[non_terminal_token, token_terminal] == dict():
                table[non_terminal_token, token_terminal] = "error"  # TODO: que pongo
                # error

    return table
