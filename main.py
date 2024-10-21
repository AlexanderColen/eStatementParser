from eStatementParser.enums import BankEnum
from eStatementParser.parsers.bmoParser import BMOParser
from eStatementParser.parsers.scotiaParser import ScotiaParser
from eStatementParser.parsers.statementParser import StatementParser


if __name__ == '__main__':
    # TODO: Parse command line arguments instead of hardcoding.
    bank: BankEnum = BankEnum.BMO
    parser: StatementParser = None

    if bank == BankEnum.BMO:
        # For debugging purposes.
        directory = r'C:\Users\Alex\Downloads\eStatements\bmo_statements'
        parser = BMOParser(directory=directory)
    elif bank == BankEnum.SCOTIABANK:
        # For debugging purposes.
        directory = r'C:\Users\Alex\Downloads\eStatements\scotia_statements'
        parser = ScotiaParser(directory=directory)
    else:
        # Await input for which bank.
        while bank is None:
            bank_choice = input('Please input the bank to parse for:\n>>> ')
            for b in BankEnum:
                if b.value in bank_choice:
                    bank = b
                    break
        directory = input('Please input the directory to parse from:\n>>> ')

    if parser is not None:
        parser.read()
