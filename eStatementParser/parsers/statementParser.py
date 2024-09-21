from ..enums import BankEnum
from pathlib import Path

import sys


class StatementParser:
    bank: BankEnum = None
    directory: str = ''
    path_list: list = []

    def __init__(self, directory: str, bank: BankEnum):
        self.bank = bank
        self.directory = directory
        print(f'Initializing {bank.value}Parser...')

    def read(self):
        print(f'Directory to extract from: "{self.directory}"')

        self.path_list = list(Path(self.directory).glob('*.pdf'))
        if len(self.path_list) == 0:
            print(f'No PDF files were found in "{self.directory}".')
            sys.exit(0)

    # TODO: Add method to store transaction(s).
