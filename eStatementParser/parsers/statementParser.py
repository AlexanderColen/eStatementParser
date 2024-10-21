from ..enums import BankEnum
from decimal import Decimal
from pathlib import Path

import sys


class StatementParser:
    # Fields
    bank: BankEnum = None
    directory: str = ''
    path_list: list = []

    # Constants
    amount_regex_pattern = r'(\d+,)?\d+\.\d{2}'

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

    @staticmethod
    def convert_amount_to_decimal(value: str) -> Decimal:
        return Decimal(value.replace(',', '').strip())
