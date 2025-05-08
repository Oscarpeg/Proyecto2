import re

reserved_words = {
    'False': 'False', 'None': 'None', 'True': 'True', 'and': 'and',
    'as': 'as', 'assert': 'assert', 'async': 'async', 'await': 'await',
    'break': 'break', 'class': 'class', 'continue': 'continue', 'def': 'def',
    'del': 'del', 'elif': 'elif', 'else': 'else', 'except': 'except',
    'finally': 'finally', 'for': 'for', 'from': 'from', 'global': 'global',
    'if': 'if', 'import': 'import', 'in': 'in', 'is': 'is', 'lambda': 'lambda',
    'nonlocal': 'nonlocal', 'not': 'not', 'or': 'or', 'pass': 'pass',
    'raise': 'raise', 'return': 'return', 'try': 'try', 'while': 'while',
    'with': 'with', 'yield': 'yield', 'bool': 'bool', 'print': 'print'
}

special_symbols = {
    '!=': 'tk_dif', '<=': 'tk_menor_igual', '>=': 'tk_mayor_igual', '->': 'tk_ejecuta',
    '+': 'tk_suma', '-': 'tk_resta', '*': 'tk_mult', '/': 'tk_div', '%': 'tk_mod',
    '=': 'tk_asig', '==': 'tk_igual', '<': 'tk_menor', '>': 'tk_mayor',
    '(': 'tk_par_izq', ')': 'tk_par_der', '[': 'tk_cor_izq', ']': 'tk_cor_der',
    '{': 'tk_llave_izq', '}': 'tk_llave_der', ',': 'tk_coma', ':': 'tk_dos_puntos',
    '.': 'tk_punto', ';': 'tk_punto_y_coma'
}

invalid_chars = {'¿', '¡', '$', '°', '@', '¬'}

def get_token_type(token):
    if token in reserved_words:
        return reserved_words[token]
    elif token.isdigit():
        return 'tk_entero'
    elif token in special_symbols:
        return special_symbols[token]
    elif token.isidentifier():
        return 'id'
    else:
        return 'error'

def lexer(input_text):
    tokens = []
    lines = input_text.split('\n')
    row = 1

    for line in lines:
        column = 1
        print(f"Procesando línea {row}: {line}")  # Imprimir cada línea que se procesa
        comment_pos = line.find('#')
        if comment_pos != -1:
            line = line[:comment_pos]

        while column <= len(line):
            # Verificar símbolos de dos caracteres primero (como '==', '!=', etc.)
            if column < len(line):
                two_chars = line[column - 1: column + 1]
                if two_chars in special_symbols:
                    tokens.append({
                        "tipo": special_symbols[two_chars],
                        "valor": two_chars,
                        "linea": row,
                        "col": column
                    })
                    print(f"Token generado: {two_chars} (tipo: {special_symbols[two_chars]})")  # Depuración
                    column += 2
                    continue

            char = line[column - 1]

            if char in special_symbols:
                tokens.append({
                    "tipo": special_symbols[char],
                    "valor": char,
                    "linea": row,
                    "col": column
                })
                print(f"Token generado: {char} (tipo: {special_symbols[char]})")  # Depuración
                column += 1
                continue

            if char.isdigit():
                start_pos = column
                num = char
                column += 1
                while column <= len(line) and line[column - 1].isdigit():
                    num += line[column - 1]
                    column += 1
                tokens.append({
                    "tipo": "tk_entero",
                    "valor": num,
                    "linea": row,
                    "col": start_pos
                })
                print(f"Token generado: {num} (tipo: tk_entero)")  # Depuración
                continue

            if char.isalpha() or char == '_':
                start_pos = column
                ident = char
                column += 1
                while column <= len(line) and (line[column - 1].isalnum() or line[column - 1] == '_'):
                    ident += line[column - 1]
                    column += 1
                tipo = get_token_type(ident)
                if tipo == 'error':
                    print(f">>> Error léxico(linea:{row},posicion:{start_pos})")
                    return None
                tokens.append({
                    "tipo": tipo,
                    "valor": ident,
                    "linea": row,
                    "col": start_pos
                })
                print(f"Token generado: {ident} (tipo: {tipo})")  # Depuración
                continue

            if char == '"':
                start_pos = column
                token_str = char
                column += 1
                while column <= len(line) and line[column - 1] != '"':
                    token_str += line[column - 1]
                    column += 1
                if column > len(line):
                    print(f">>> Error léxico(linea:{row},posicion:{start_pos})")
                    return None
                token_str += '"'
                tokens.append({
                    "tipo": "tk_cadena",
                    "valor": token_str,
                    "linea": row,
                    "col": start_pos
                })
                print(f"Token generado: {token_str} (tipo: tk_cadena)")  # Depuración
                column += 1
                continue

            if char in invalid_chars:
                print(f">>> Error léxico(linea:{row},posicion:{column})")
                return None

            column += 1
        row += 1

    return tokens

