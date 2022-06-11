from Seagull_lexer import SeagullLexer
from Seagull_parser import SeagullParser
from Seagull_interpreter import SeagullInterpreter
import pprint

if __name__ == '__main__':
    with open('test.Seagull', 'r') as source_file:
        source_code = source_file.read()

        lexer = SeagullLexer(source_code)
        lexer.lex()
        lexer.print_symbols_table()
        lexer.print_ids_table()
        lexer.print_const_table()

        if lexer.f_success:
            parser = SeagullParser(lexer.tableOfSymb, lexer.tableOfConst)
            parser.parse_program()
            pprint.pprint(parser.postfix_notation)

            if parser.f_success:
                translator = SeagullInterpreter(parser.postfix_notation, lexer.tableOfId, lexer.tableOfConst)
                translator.interpret()
                if translator.success:
                    print(translator.ident_table)
                    print(translator.const_table)