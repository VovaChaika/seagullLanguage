import traceback

import Seagull_stack


def is_undefined(variable_type):
    return variable_type == 'undefined'


def is_nullable(variable_value):
    return variable_value == 'null'


class SeagullInterpreter:
    operator_mapping = {
        '+': '+', '-': '-', '*': '*', '/': '/', '^': '**', '=': '=',
        '<': '<', '<=': '<=', '==': '==', '!=': '!=', '>=': '>=', '>': '>', '&&': 'and', '||': 'or'
    }

    type_mapping = {'real': 'float', 'integer': 'int', 'boolean': 'bool'}

    run_time_errors = {
        'types_mismatch': ('%s\n\tТипи операндів відрізняються: %s %s %s.', 1),
        'undefined_var': ('%s\n\tНевідома змінна \'%s\'.', 2),
        'zero_division': ('%s\n\tДілення на нуль: %s %s %s.', 3),
        'invalid_operand_types': ('%s\n\tНевалідний тип одного або декількох операндів: %s %s %s.', 4),
        'undefined': ('%s\n\tНевизначена змінна \'%s\' не може використовуватись в операціях.', 5),
        'invalid_operator': ('%s\n\tНевідомий оператор %s', 322),
    }

    def __init__(back, postfix_notation, ident_table, const_table):
        back.tableOfLabel = {}
        back.command_track = []
        back.postfix_notation = postfix_notation

        back.ident_table = ident_table
        back.const_table = const_table
        back.stack = Seagull_stack.Stack()

        back.success = True

    def interpret(back):
        try:
            i = 0
            num_it = len(back.postfix_notation)
            max_it = 10000
            current_it = 0
            while i < num_it and current_it < max_it:
                print(back.ident_table)
                current_it += 1
                lex = None
                tok = None
                var_type = None
                if len(back.postfix_notation[0]) > 2:
                    lex, tok, var_type = back.postfix_notation.pop(0)
                else:
                    lex, tok = back.postfix_notation.pop(0)
                back.command_track.append((num_it, lex, tok))
                if tok in ('integer', 'real', 'boolean', 'ident'):
                    back.stack.push((lex, tok))
                    next_instr = num_it + 1
                    if tok == 'ident' and var_type:
                        back.ident_table[lex] = (
                            back.ident_table[lex][0],
                            var_type,
                            back.ident_table[lex][2]
                        )
                else:
                    back.do_action(lex, tok)
                    next_instr = num_it + 1
                num_it = next_instr
            return back.command_track

            # if self.to_view:
            #     self.stepToPrint(i + 1, lex, tok)
        except SystemExit as e:
            print('SeagullInterpreter: Аварійне завершення програми з кодом {0}'.format(e))
            return False
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        print('SeagullInterpreter: Інтерпретатор завершив роботу успішно')
        return True

    def do_action(back, lex, tok):
        if lex == "=" and tok == "assign_op":
            lex_right, tok_right = back.stack.pop()
            value_right, type_right = back.check_token_and_lexeme(tok_right, lex_right)
            lex_left, tok_left = back.stack.pop()
            _, type_left = back.check_token_and_lexeme(tok_left, lex_left)

            if type_left != type_right:
                back.fail_runtime('types_mismatch', type_left, lex, type_right)

            if tok_left == 'ident':
                _type = back.ident_table[lex_left][1]

            else:
                _type = type_left

            try:
                back.ident_table[lex_left] = (
                    back.ident_table[lex_left][0],
                    _type,
                    eval(f"{back.type_mapping[_type]}({value_right})")
                )
            except KeyError:
                back.fail_runtime('undefined', lex_left)
        elif tok in ('add_op', 'mult_op', 'pow_op'):
            lex_right, tok_right = back.stack.pop()
            lex_left, tok_left = back.stack.pop()

            if (tok_right, tok_left) in (('integer', 'real'), ('real', 'integer')):
                back.fail_runtime('types_mismatch', lex_left, lex, lex_right)

            back.process_operator((lex_left, tok_left), lex, (lex_right, tok_right))

        elif tok in ('rel_op', 'bool_op'):
            lex_right, tok_right = back.stack.pop()
            lex_left, tok_left = back.stack.pop()
            print()
            if lex not in ('==', '!=', '&&', '||') and not all(
                    (tok in ('integer', 'real', 'ident', 'boolean') for tok in (tok_right, tok_left))):
                back.fail_runtime('invalid_operand_types', lex_left, lex, lex_right)

            back.process_operator((lex_left, tok_left), lex, (lex_right, tok_right))
        elif tok == 'unar_minus':
            lex_right, tok_right = back.stack.pop()
            try:
                lex_left, tok_left = 0, back.ident_table[lex_right][1]
            except KeyError:
                lex_left, tok_left = 0, back.ident_table[lex_right][1]

            # add 0 to table of consts
            back.push_to_consts_table(tok_left, lex_left)

            back.process_operator((lex_left, tok_left), lex, (lex_right, tok_right))



    def run_operator(back, left, lex, right):
        lex_left, type_left, value_left = left
        lex_right, type_right, value_right = right

        if back.ident_table.get(lex_left, None) and is_nullable(value_left):
            back.fail_runtime('nullable', lex_left)
        if back.ident_table.get(lex_right, None) and is_nullable(value_right):
            back.fail_runtime('nullable', lex_right)
        if operator := back.operator_mapping.get(lex, None):
            try:
                print(f"CALC: {value_left} {operator} {value_right}")
                calc_result = eval(f"{value_left} {operator} {value_right}")
            except ZeroDivisionError:
                back.fail_runtime('zero_division', value_left, operator, value_right)
            else:
                if lex == "/" and type_right:
                    calc_result = int(calc_result)
                if lex in ('<', '<=', '==', '!=', '>=', '>',):
                    _type = 'bool'
                else:
                    _type = type_left
                back.stack.push((calc_result, _type))
                back.push_to_consts_table(_type, calc_result)
        else:
            back.fail_runtime('invalid_operator', operator)

    def check_token_and_lexeme(back, token, lexeme):
        lexeme = str(lexeme)
        if token == 'ident':
            if is_undefined(back.ident_table[lexeme][1]):
                back.fail_runtime('undefined_var', lexeme)

            return back.ident_table[lexeme][2], back.ident_table[lexeme][1]
        else:
            return back.const_table[lexeme][2], back.const_table[lexeme][1]

    def fail_runtime(back, error: str, *args):
        error_msg, error_code = back.run_time_errors.get(error, (None, None))
        print(error_msg % ('SeagullInterpreterError:', *args))
        exit(error_code)

    def process_operator(back, left, lex, right):
        lex_left, tok_left = left
        lex_right, tok_right = right

        value_left, type_left = back.check_token_and_lexeme(tok_left, lex_left)
        value_right, type_right = back.check_token_and_lexeme(tok_right, lex_right)

        back.run_operator((lex_left, type_left, value_left), lex, (lex_right, type_right, value_right))

    def push_to_consts_table(back, token, value):
        if not back.const_table.get(str(value), None):
            index = len(back.const_table) + 1
            back.const_table[str(value)] = (index, token, value)

    def processing_colon(back, num_it):
        # global instrNum
        m = back.stack.pop()
        return num_it + 1

    def getBoolValue(back, param):
        pass