tableOfLanguageTokens = {'program': 'keyword', 'if': 'keyword', 'then': 'keyword', 'rof': 'keyword', '=': 'assign_op',
                         '.': 'punct', ' ': 'ws', '\t': 'ws', '\n': 'eol', '-': 'add_op', '+': 'add_op', '*': 'mult_op',
                         '/': 'mult_op',
                         '(': 'par_op', ')': 'par_op', '{': 'start_block',
                         '}': 'end_block', 'by': 'keyword', ',': 'punct', '||': 'bool_op', '&&': 'bool_op',
                         'true': 'boolean', 'false': 'boolean', ';': 'op_end', ':': 'punct', '<': 'rel_op', '>': 'rel_op',
                         '>=': 'rel_op', '-': 'unar_minus', '<=': 'rel_op', '==': 'rel_op', '^': 'pow_op', '\n\r': 'eol', '\r\n': 'eol',
                         'to': 'keyword', 'do': 'keyword', 'for': 'keyword', 'scan': 'keyword', 'out': 'keyword',
                         'boolean': 'keyword', 'real': 'keyword', 'integer': 'keyword', '!=': 'rel_op',
                         }

tableIdentFloatInt = {2: 'ident', 4: 'integer', 6: 'real', 15: 'real'}

classes = {
    'Digit': '0123456789',
    'Dot': '.',
    'WhiteSpace': ' \t',
    'EndOfLine': '\n\r',
    'Operators': '+-*/^(){}:;=<>!,&|',
    'ScientificNotation': '-',
    'Letter': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
}

stf = {
    (0, 'WhiteSpace'): 0,
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,
    (0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'other'): 4,
    (3, 'Dot'): 5, (5, 'Digit'): 5, (5, 'other'): 6,
    (0, '!'): 7, (7, '='): 8, (7, 'other'): 102,
    (0, '='): 9, (0, '<'): 9, (0, '>'): 9, (9, '='): 10, (9, 'other'): 11,
    (0, '+'): 13, (0, '-'): 13, (0, '*'): 13, (0, '/'): 13, (0, '^'): 13,
    (0, '('): 13, (0, ')'): 13, (0, '{'): 13, (0, '}'): 13, (0, ':'): 13, (0, ';'): 13, (0, ','): 13,
    (0, '&'): 16, (16, '&'): 17,
    (0, '|'): 18, (18, '|'): 19,
    (0, 'EndOfLine'): 12,
    (0, 'other'): 101,
    (16, 'other'): 103,
    (18, 'other'): 104,
    (3, 'ScientificNotation'): 14, (14, 'Digit'): 14, (14, 'other'): 15, (5, 'ScientificNotation'): 14
}

states = {
    'initial': (0,),
    'star': (2, 4, 6, 11, 15),
    'error': (101, 102, 103, 104),
    'final': (2, 4, 6, 8, 10, 11, 12, 13, 15, 101, 102, 103, 104, 17, 19),
    'endOfLine': (12,),
    'operators': (8, 10, 11, 13),
    'double_operators': (8, 10, 17, 19),
    'const': (4, 6, 15),
    'identifier': (2,)
}

errorsDescription = {
    101: "SeagullLexerError: у рядку %s нерозпізнаний символ %s",
    102: "SeagullLexerError: у рядку %s очікувався символ '=', а не %s",
    103: "SeagullLexerError: у рядку %s очікувався символ '&', а не %s",
    104: "SeagullLexerError: у рядку %s очікувався символ '|', а не %s",
}