class SeagullParser:

    ERR_TOKEN_MISMATCH = 1
    ERR_GET_SYMB = 2
    ERR_UNEXP_END_OF_PROG = 3
    ERR_INSTR_MISMATCH = 4
    ERR_EXP_FACTOR_MISMATCH = 5
    ERR_BOOL_EXPR_MISMATCH = 6

    def __init__(back, table_of_tokens: dict[int, tuple], const_table):
        back.tableOfForHiddenId = {}
        back.table_of_tokens = table_of_tokens
        back.num_row = 1
        back.token_count = len(table_of_tokens)
        back.postfix_notation = []
        back.tableOfLabel = {}
        back.f_success = True
        back.hidden_table = {}
        back.const_table = const_table

    def parse_token(back, lexeme, token, ident):
        if back.num_row > back.token_count+1:
            back.fail_parse(back.ERR_UNEXP_END_OF_PROG, (lexeme, token, back.num_row))

        line_num, lex, tok = back.get_symb()
        back.num_row += 1

        if (lex, tok) == (lexeme, token):
            print(ident + 'parseToken: В рядку {0} токен {1}'.format(line_num, (lexeme, token)))
            return True
        else:
            back.fail_parse(back.ERR_TOKEN_MISMATCH, (line_num, lex, tok, lexeme, token))
            return False

    def get_symb(back):
        return back.get_row(back.num_row)

    def parse_statement_list(back):
        print('\t parseStatementList():')
        if back.parse_statement():
            back.parse_statement_list()
        return True

    def parse_statement(back):
        print('\t\t parseStatement():')
        num_line, lex, tok = back.get_symb()
        if tok == 'ident':
            back.postfix_notation.append((lex, tok, None))
            back.num_row += 1
            if back.get_symb()[-1] == 'assign_op':
                back.get_back()
                back.parse_assign()
            else:
                back.get_back()
                back.parse_expression()
            back.parse_token(';', 'op_end', '\t' * 2)
            return True

        elif (lex, tok) == ('if', 'keyword'):
            back.parse_if()
            return True

        elif (lex, tok) == ('for', 'keyword'):
            back.parse_for()
            return True

        elif (lex, tok) == ('out', 'keyword'):
            back.parse_print()
            back.parse_token(';', 'op_end', '\t' * 2)
            return True
        elif (lex, tok) == ('scan', 'keyword'):
            back.parse_scan()
            back.parse_token(';', 'op_end', '\t' * 2)
            return True
        elif lex in ('integer', 'real', 'boolean') and tok == 'keyword':
            back.parse_declaration()
            back.parse_token(';', 'op_end', '\t' * 2)
            return True
        elif (lex, tok) == ('}', 'end_block'):
            return False
        else:
            return False

    def fail_parse(back, error_code, what: tuple):
        back.f_success = False
        if error_code == back.ERR_UNEXP_END_OF_PROG:
            (lexeme, token, num_row) = what
            print(
                'SeagullParser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
                'номером {1}. \n\t Очікувалось - {0}'.format(
                    (lexeme, token), num_row))
        if error_code == back.ERR_GET_SYMB:
            (num_row) = what
            print(
                'SeagullParser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
                'номером {0}. \n\t Останній запис - {1}'.format(
                    num_row, back.table_of_tokens[num_row - 1]))
        elif error_code == back.ERR_TOKEN_MISMATCH:
            (num_line, lexeme, token, lex, tok) = what
            print('SeagullParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
                num_line, lexeme, token, lex, tok))
        elif error_code == back.ERR_INSTR_MISMATCH:
            (num_line, lex, tok, expected) = what
            print(
                'SeagullParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(num_line,
                                                                                                               lex, tok,
                                                                                                               expected))
        elif error_code == back.ERR_EXP_FACTOR_MISMATCH:
            (num_line, lex, tok, expected) = what
            print(
                'SeagullParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(num_line,
                                                                                                               lex, tok,
                                                                                                               expected))
        elif error_code == back.ERR_BOOL_EXPR_MISMATCH:
            (num_line, lex, tok, expected) = what
            print(
                'SeagullParser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(num_line,
                                                                                                               lex, tok,
                                                                                                               expected))

        exit(error_code)

    def parse_assign(back):
        print('\t' * 4 + 'parseAssign():')
        num_line, lex, tok = back.get_symb()

        back.num_row += 1

        print('\t' * 5 + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
        if back.parse_token('=', 'assign_op', '\t' * 5):
            back.parse_expression()
            back.postfix_notation.append(('=', 'assign_op', None))
            return True
        else:
            return False

    def parse_expression(back):
        print('\t' * 5 + 'parseExpression():')
        num_row, lex, tok = back.get_symb()
        arithm_expr_parse_result = back.parse_arithm_expression()
        bool_expr_parse_result = back.parse_bool_expr()
        if arithm_expr_parse_result == False and bool_expr_parse_result == False:
            num_line, lex, tok = back.get_symb()
            back.fail_parse(back.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'boolean, bool_op, rel_op, integer, real, ident або \'(\' Expression '
                                                 '\')\''))
        return True

    def parse_power(back):
        print('\t' * 6 + 'parsePower():')
        back.parse_factor()
        num_line, lex, tok = back.get_symb()
        if tok == 'pow_op':
            back.num_row += 1
            back.parse_power()
            back.postfix_notation.append((lex, tok, None))
        return True

    def parse_term(back):
        print('\t' * 6 + 'parseTerm():')
        if back.parse_power():
            numLine, lex, tok = back.get_symb()
            if tok == 'mult_op':
                back.num_row += 1
                print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
                back.parse_term()
                back.postfix_notation.append((lex, tok, None))
            if (lex, tok) == ('-', 'unar_minus'):
                back.num_row += 1
                print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
                back.parse_term()
            else:
                F = False
            return True
        else:
            return False

    def parse_factor(back):
        print('\t' * 7 + 'parseFactor():')
        num_line, lex, tok = back.get_symb()
        print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lex, tok):{1}'.format(num_line, (lex, tok)))

        if tok in ('integer', 'real', 'ident', 'boolean'):
            back.postfix_notation.append((lex, tok, None))
            back.num_row += 1
            print('\t' * 7 + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))

        elif lex == '(':
            back.num_row += 1
            back.parse_arithm_expression()
            back.parse_token(')', 'par_op', '\t' * 7)
            print('\t' * 7 + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
        else:
            return False
        return True

    def parse_if(back):
        _, lex, tok = back.get_symb()
        if lex == 'if' and tok == 'keyword':
            back.num_row += 1
            back.parse_bool_expr()
            back.parse_token('{', 'start_block', '\t' * 5)
            back.parse_statement_list()
            back.postfix_notation.append((':', 'colon'))
            back.parse_token('}', 'end_block', '\t' * 5)
            return True
        else:
            return False

    def parse_bool_expr(back):
        num_line, lex, tok = back.get_symb()
        print('\t' * 6 + 'parse_bool_expr: ' + 'в рядку {0} - {1}'.format(num_line, (lex, tok)))
        if tok == 'boolean':
            back.num_row += 1
            back.parse_bool_expr()
            back.postfix_notation.append((lex, tok, None))
        elif tok == 'ident':
            back.num_row += 1
            back.parse_bool_expr()
            back.postfix_notation.append((lex, tok, None))
        elif tok == 'rel_op':
            back.num_row += 1
            back.parse_arithm_expression()
            back.parse_bool_expr()
            back.postfix_notation.append((lex, tok, None))
            return True
        elif tok == 'bool_op':
            back.num_row += 1
            back.parse_bool_expr()
            back.postfix_notation.append((lex, tok, None))
            return True
        else:
            return False

    def parse_program(back):
        try:
            back.parse_token('program', 'keyword', '')
            num_line, lex, tok = back.get_symb()
            if (tok) == ('ident'):
                back.num_row += 1
            else:
                print('SeagullParser: Немає імені програми після ключового слова `program`'); return False
            back.parse_token('{', 'start_block', '')
            back.parse_statement_list()
            back.parse_token('}', 'end_block', '')
            print('SeagullParser: Синтаксичний аналіз завершився успішно')
            return True
        except SystemExit as e:
            print('SeagullParser: Аварійне завершення програми з кодом {0}'.format(e))

    def parse_for(back):
        num_line, lex, tok = back.get_symb()
        if (lex, tok) == ('for', 'keyword'):
            back.num_row += 1
            back.parse_assign()
            back.postfix_notation.append((lex, tok))

            back.parse_token('by', 'keyword', '')
            back.postfix_notation.append(('=', 'assign_op'))
            back.postfix_notation.append((':', 'colon'))
            back.parse_expression()
            back.parse_token('to', 'keyword', '')
            back.postfix_notation.append(('=', 'assign_op'))
            back.postfix_notation.append(('0', 'integer'))
            back.postfix_notation.append(('==', 'rel_op'))
            back.postfix_notation.append((lex, tok))
            back.postfix_notation.append((lex, tok))
            back.postfix_notation.append(('+', 'add_op'))
            back.postfix_notation.append(('=', 'assign_op'))
            back.postfix_notation.append((':', 'colon'))
            back.postfix_notation.append(('0', 'intnum'))
            back.postfix_notation.append(('=', 'assign_op'))
            back.postfix_notation.append((lex, tok))
            back.parse_expression()
            back.parse_token('do', 'keyword', '\t' * 5)

            back.postfix_notation.append(('-', 'add_op'))
            back.postfix_notation.append(('*', 'mult_op'))
            back.postfix_notation.append(('0', 'intnum'))
            back.postfix_notation.append(('<', 'rel_op'))

            back.parse_statement()

            back.parse_token('rof', 'keyword', '')

            back.postfix_notation.append((':', 'colon'))

            return True
        else:
            return False

    def parse_print(back):
        _, lex, tok = back.get_symb()
        if (lex, tok) == ('out', 'keyword'):
            back.num_row += 1
            back.parse_token('(', 'par_op', '\t' * 5)
            back.parse_factor()
            back.parse_inner_print()
            back.parse_token(')', 'par_op', '\t' * 5)
            back.postfix_notation.append((lex, tok))
            return True
        else:
            return False

    def parse_inner_print(back):
        _, lex, tok = back.get_symb()
        if (lex, tok) == (',', 'punct'):
            back.num_row += 1
            back.parse_factor()
            back.parse_inner_print()
            return True
        else:
            return False

    def parse_scan(back):
        _, lex, tok = back.get_symb()
        if (lex, tok) == ('scan', 'keyword'):
            back.num_row += 1
            back.parse_token('(', 'par_op', '\t' * 5)
            back.parse_var_list()
            back.parse_token(')', 'par_op', '\t' * 5)
            back.postfix_notation.append((lex, tok))
            return True
        else:
            return False

    def parse_declaration(back):
        num_line, lex, tok = back.get_symb()
        back.num_row += 1
        if lex in ('integer', 'real', 'boolean') and tok == 'keyword':
            back.parse_var_init_list(lex)

        else:
            back.fail_parse(back.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'integer, real, boolean, ident або \'(\' Expression \')\''))

    def parse_arithm_expression(back):
        if back.parse_term():
            num_line, lex, tok = back.get_symb()
            if tok in 'add_op':
                back.num_row += 1
                print('\t' * 6 + 'parse_arithm_expression: ' + f'в рядку {num_line} - {(lex, tok)}')
                back.parse_arithm_expression()
                back.postfix_notation.append((lex, tok, None))
            return True
        else:
            return False

    def parse_var_init_list(back, var_type):
        num_line, lex, tok = back.get_symb()
        back.num_row += 1

        if tok == 'ident':
            print('\t' * 5 + f'в рядку {num_line} - {(lex, tok)}')
            back.postfix_notation.append((lex, tok, var_type))
            pass
        else:
            back.fail_parse(back.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'bracket_op, int, float, bool, ident або \'(\' Expression \')\''))
        num_line, lex, tok = back.get_symb()
        if lex == '=' and tok == 'assign_op':
            back.get_back()
            back.parse_assign()

        num_line, lex, tok = back.get_symb()
        if lex == ',' and tok == 'punct':
            back.num_row += 1
            back.parse_var_init_list(var_type)

    def get_row(back, index):
        if index > back.token_count:
            back.fail_parse(back.ERR_GET_SYMB, (index,))
        num_line, lexeme, token, _ = back.table_of_tokens[index]
        return num_line, lexeme, token

    def parse_var_list(back):
        num_line, lex, tok = back.get_symb()
        back.num_row += 1

        if tok == 'ident':
            print('\t' * 5 + f'в рядку {num_line} - {(lex, tok)}')
            back.postfix_notation.append((lex, tok, ''))
            pass
        else:
            back.fail_parse(back.ERR_EXP_FACTOR_MISMATCH,
                            (num_line, lex, tok, 'bracket_op, int, float, bool, ident або \'(\' Expression \')\''))

        num_line, lex, tok = back.get_symb()
        if lex == ',' and tok == 'punct':
            back.num_row += 1
            back.parse_var_list()

    def get_back(back):
        back.num_row -= 1