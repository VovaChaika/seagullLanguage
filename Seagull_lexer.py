from Seagull_grammar import *


class SeagullLexer:
    tableOfId = {}  # Таблиця ідентифікаторів
    tableOfConst = {}  # Таблиць констант
    tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)

    def __init__(back, source_code):
        back.tableOfLanguageTokens = tableOfLanguageTokens
        back.tableIdentFloatInt = tableIdentFloatInt
        back.classes = classes
        back.stf = stf
        back.states = states
        back.errorsDescription = errorsDescription

        # f = open('test.Seagull', 'r')
        back.sourceCode = source_code + ' '
        # f.close()

        # ознака успішності розбору
        back.f_success = True

        back.state = states['initial'][0]

        back.lenCode = len(back.sourceCode) - 1  # номер останнього символа у файлі з кодом програми
        back.numLine = 1  # лексичний аналіз починаємо з першого рядка
        back.numChar = 0  # з першого символа (в Python'і нумерація - з 0)
        back.char = ''  # ще не брали жодного символа
        back.lexeme = ''  # ще не починали розпізнавати лексеми

    def lex(back):
        try:
            while back.numChar < back.lenCode:
                back.char = back.next_char()
                back.state = back.next_state(back.state, back.class_of_char(back.char))
                if back.is_initial_state(back.state):
                    back.lexeme = ''
                elif back.is_final_state(back.state):
                    back.processing()
                else:
                    back.lexeme += back.char
            print('SeagullLexer: Лексичний аналіз завершено успішно')
            print('-' * 30)
            # pprint.pprint('tableOfSymb:{0}'.format(self.tableOfSymb))
            # pprint.pprint('tableOfId:{0}'.format(self.tableOfId))
            # pprint.pprint('tableOfConst:{0}'.format(self.tableOfConst))

        except SystemExit as e:
            back.f_success = False
            print('SeagullLexer: Аварійне завершення програми з кодом {0}'.format(e))

    def get_index(back):
        if back.state in back.states['const'] or back.lexeme in ('true', 'false'):
            return back.get_or_set_id_index(back.state, back.lexeme, back.tableOfConst)
        elif back.state in back.states['identifier']:
            return back.get_or_set_id_index(back.state, back.lexeme, back.tableOfId)

    def processing(back):
        if back.state in back.states['endOfLine']:
            back.numLine += 1
            back.state = back.states['initial'][0]
        elif back.state in (back.states['const'] + back.states['identifier']):
            token = back.get_token(back.state, back.lexeme)
            if token != 'keyword':
                index = back.get_index()
                back.tableOfSymb[len(back.tableOfSymb) + 1] = (back.numLine, back.lexeme, token, index)
            else:
                back.tableOfSymb[len(back.tableOfSymb) + 1] = (back.numLine, back.lexeme, token, '')
            back.lexeme = ''
            back.state = back.states['initial'][0]
            back.numChar = back.put_char_back(back.numChar)
        elif back.state in back.states['operators']:
            if not back.lexeme or back.state in back.states['double_operators']:
                back.lexeme += back.char
            token = back.get_token(back.state, back.lexeme)
            back.tableOfSymb[len(back.tableOfSymb) + 1] = (back.numLine, back.lexeme, token, '')
            if back.state in back.states['star']:
                back.numChar = back.put_char_back(back.numChar)
            back.lexeme = ''
            back.state = back.states['initial'][0]
        elif back.state in back.states['double_operators']:
            if back.state in back.states['double_operators']:
                back.lexeme += back.char
            token = back.get_token(back.state, back.lexeme)
            back.tableOfSymb[len(back.tableOfSymb) + 1] = (back.numLine, back.lexeme, token, '')
            if back.state in back.states['star']:
                back.numChar = back.put_char_back(back.numChar)
            back.lexeme = ''
            back.state = back.states['initial'][0]
        elif back.state in back.states['error']:
            back.fail()

    def fail(back):
        print(back.numLine)
        if back.state == 101:
            print('Lexer: у рядку ', back.numLine, ' неочікуваний символ ' + back.char)
            exit(101)
        if back.state == 102:
            print('Lexer: у рядку ', back.numLine, ' очікувався символ =, а не ' + back.char)
            exit(102)
        if back.state == 103:
            print('Lexer: у рядку ', back.numLine, ' очікувався символ &, а не ' + back.char)
            exit(103)
        if back.state == 104:
            print('Lexer: у рядку ', back.numLine, ' очікувався символ &, а не ' + back.char)
            exit(104)

    def is_initial_state(back, state):
        return state in back.states['initial']

    def is_final_state(back, state):
        return state in back.states['final']

    def next_state(back, state, class_ch):
        result = None
        for t in class_ch:
            step = (state, t)
            if step in back.stf:
                result = back.stf[step]
        if result is None:
            result = back.stf[(state, 'other')]
        return result

    def next_char(back):
        char = back.sourceCode[back.numChar]
        back.numChar += 1
        return char

    @staticmethod
    def put_char_back(num_char):
        return num_char - 1

    def class_of_char(back, char):
        result = []
        for key, value in back.classes.items():
            if char in value:
                if key == "Operators":
                    result.append(char)
                else:
                    result.append(key)
        return result

    def get_token(back, state, lexeme):
        try:
            return back.tableOfLanguageTokens[lexeme]
        except KeyError:
            return back.tableIdentFloatInt[state]

    def get_or_set_id_index(back, state, lexeme, table):
        index = table.get(lexeme)
        if not index:
            index = len(table) + 1
            if (token := back.get_token(state, lexeme)) == 'ident':
                token = 'undefined'
            table[lexeme] = (index, token)

            # For identifiers
            if lexeme in ('true', 'false'):
                table[lexeme] += (eval(lexeme.title()),)
            elif state in back.states['identifier']:
                table[lexeme] += ('null',)
            elif token == 'real':
                table[lexeme] += (eval(f"float({lexeme})"),)
            elif token == 'integer':
                table[lexeme] += (eval(f"int({lexeme})"),)
            else:
                table[lexeme] += (eval(f"{token}({lexeme})"),)

        return index

    def print_symbols_table(back):
        print('\n{:^46s}'.format('Таблиця символів'))
        print(*('-' for _ in range(23)))
        print('{0:^3s} | {1:^10s} | {2:^17s} | {3:^6s}'.format('#', 'Лексема', 'Токен', 'Індекс'))
        print(*('-' for _ in range(23)))
        for value in back.tableOfSymb.values():
            if value[3] == '':
                print('{0:<3d} | {1:<10s} | {2:<17s} |'.format(*value[0: 3]))
            else:
                print('{0:<3d} | {1:<10s} | {2:<17s} | {3:<6d}'.format(value[0], value[1], value[2], value[3][0] if isinstance(value[3],tuple) else value[3]))
        print(*('-' for _ in range(23)))

    def print_ids_table(back):
        print('\n{:^26s}'.format('Таблиця ідентифікаторів'))
        print(*('-' for _ in range(13)))
        print('{0:^15s} | {1:^8s}'.format('Назва', 'Індекс'))
        print(*('-' for _ in range(13)))
        for value in back.tableOfId.items():
            print('{0:^15s} | {1}'.format(*value))
        print(*('-' for _ in range(13)))

    def print_const_table(back):
        print('\n{:^26s}'.format('Таблиця констант'))
        print(*('-' for _ in range(13)))
        print('{0:^15s} | {1:^8s}'.format('Константа', 'Індекс'))
        print(*('-' for _ in range(13)))
        for value in back.tableOfConst.items():
            print('{0:^15s} | {1}'.format(*value))
        print(*('-' for _ in range(13)))