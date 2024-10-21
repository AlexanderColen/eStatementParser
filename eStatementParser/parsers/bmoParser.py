from ..enums import BankEnum, MonthEnum, BMOTransactionTypeEnum
from .statementParser import StatementParser
from .transaction import Transaction
from decimal import Decimal
from PyPDF2 import PdfReader

import re


class BMOParser(StatementParser):
    def __init__(self, directory: str):
        super().__init__(directory=directory, bank=BankEnum.BMO)

    def read(self):
        super().read()
        month_regex_pattern = f"({'|'.join([month.value for month in MonthEnum])})"

        for path in self.path_list:
            str_path = str(path)
            print(f'Parsing file: {str_path}')

            input_file = open(str_path, 'rb')
            pdf_reader = PdfReader(input_file)

            for i in range(0, len(pdf_reader.pages)):
                page_text = pdf_reader.pages[i].extract_text()

                # Clean up weirdly parsed characters.
                page_text = page_text.replace('/2a', '*')
                page_text = page_text.replace('/2b', '+')
                page_text = page_text.replace('/2c', ',')
                page_text = page_text.replace('/2d', '-')
                page_text = page_text.replace('/2e', '.')
                page_text = page_text.replace('/2f', '/')
                page_text = page_text.replace('/26', '&')
                page_text = page_text.replace('/27', "'")
                page_text = page_text.replace('/28', '(')
                page_text = page_text.replace('/29', ')')
                page_text = page_text.replace('/3a', ':')

                # Clean up numbers.
                for n in range(0, 10):
                    page_text = page_text.replace(f'/{n}', f'{n}')

                # Prepare to store transaction.
                transaction = None
                statement_started = False
                do_parse = False

                # Loop over text line-by-line.
                for line in page_text.splitlines():
                    # Only start parsing after finding a specific line
                    # to skip useless header information.
                    if not statement_started:
                        statement_started = "Here's what happened in your account" in line
                        continue
                    else:
                        # Quit parsing with closing totals.
                        if re.search(month_regex_pattern
                                     + r' \d{2} Closing totals '
                                     + self.amount_regex_pattern
                                     + ' '
                                     + self.amount_regex_pattern, line) \
                                or re.search(r'^Page \d+ of \d+', line):
                            do_parse = False
                            continue

                    if not do_parse:
                        if re.search(month_regex_pattern
                                     + r' \d{2} Opening balance '
                                     + self.amount_regex_pattern, line) \
                                or re.search(r'Primary Chequing Account # [0-9 -]+ \(continued\)', line):
                            do_parse = True
                        continue

                    # New transactions follow format:
                    # <MONTH> <DAY> <TYPE>, <DESCRIPTION> <AMOUNT IN/OUT> <BALANCE>
                    if transaction is None:
                        # Month + Day
                        date_match = re.search('^' + month_regex_pattern + r' \d{2}(?= \w+)', line)
                        if date_match:
                            transaction = Transaction()
                            transaction.posted_date = line[:6]
                        else:
                            # Sometimes the day contains a space.
                            date_match = re.search('^' + month_regex_pattern + r' \d \d(?= \w+)', line)
                            transaction = Transaction()
                            transaction.posted_date = line[:5] + line[6]

                        line = line.replace(f'{date_match.group()} ', '', 1)

                        if transaction is None:
                            print(line)

                        # Type
                        for transaction_type in BMOTransactionTypeEnum:
                            if line.startswith(transaction_type.value):
                                transaction.type = transaction_type.value
                                line = line.replace(f'{transaction.type}, ', '', 1)
                                break

                        # Description
                        if transaction.type == BMOTransactionTypeEnum.ONLINE_TRANSFER.value:
                            transaction.description = re.search(f'^TF \d+', line).group()
                        elif transaction.type == BMOTransactionTypeEnum.INCOMING_TRANSFER.value:
                            transaction.description = transaction.type
                        else:
                            transaction.description = re.search(f'^.+[^ {self.amount_regex_pattern}]', line).group()

                        line = line.replace(f'{transaction.description} ', '', 1)

                        # Amount in/out
                        self.match_amount(line=line, transaction=transaction)
                        # Leftover would be balance.
                        self.match_amount(line=line, transaction=transaction, leftover=True)
                        # Handle potential completion.
                        transaction = self.check_transaction_completion(transaction=transaction)
                    # Continue parsing from previous line.
                    else:
                        description_part_match = re.search(f'^.+[^{self.amount_regex_pattern}][^ {self.amount_regex_pattern}]', line).group()
                        transaction.description += f' {description_part_match}'

                        line = line.replace(f'{description_part_match}', '', 1)

                        # Amount in/out
                        self.match_amount(line=line, transaction=transaction)
                        # Leftover would be balance.
                        self.match_amount(line=line, transaction=transaction, leftover=True)
                        # Handle potential completion.
                        transaction = self.check_transaction_completion(transaction=transaction)

            input_file.close()

    def match_amount(
        self,
        line: str,
        transaction: Transaction,
        leftover: bool = False
    ) -> (str, Transaction):
        if leftover:
            leftover_balance_match = re.search(f'^{self.amount_regex_pattern}', line)
            if leftover_balance_match is None:
                return line, transaction

            transaction.leftover_balance = self.convert_amount_to_decimal(leftover_balance_match.group())
        else:
            amount_match = re.search(f'^{self.amount_regex_pattern}[^{self.amount_regex_pattern}]', line)
            if amount_match is None:
                return line, transaction

            amount = amount_match.group()

            transaction.amount = self.convert_amount_to_decimal(value=amount)
            line = line.replace(f'{amount} ', '', 1)

            # Multiply by minus one for outgoing determined by type.
            if transaction.type in [
                BMOTransactionTypeEnum.DEBIT_PURCHASE.value,
                BMOTransactionTypeEnum.ONLINE_TRANSFER.value,
                BMOTransactionTypeEnum.PRE_AUTHORIZED.value
            ]:
                transaction.amount *= -1

        return line, transaction

    @staticmethod
    def check_transaction_completion(transaction: Transaction) -> Transaction:
        # Reset variables after parsing transaction finished.
        if transaction.is_complete():
            print(transaction)
            transaction.save()
            # Clear for next parse.
            transaction = None

        return transaction