from ..enums import BankEnum, MonthEnum, ScotiaBankTransactionTypeEnum
from .statementParser import StatementParser
from .transaction import Transaction
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import io
import re


class ScotiaParser(StatementParser):
    def __init__(self, directory: str):
        super().__init__(directory=directory, bank=BankEnum.SCOTIABANK)

    def read(self):
        super().read()

        # TODO: Remove debug path list change
        # self.path_list = self.path_list[:1]

        for path in self.path_list:
            str_path = str(path)
            print(f'Parsing file: {str_path}')

            input_file = open(str_path, 'rb')
            pdf_resource_manager = PDFResourceManager()
            return_data = io.StringIO()
            text_converter = TextConverter(
                pdf_resource_manager, return_data, laparams=LAParams()
            )
            interpreter = PDFPageInterpreter(
                pdf_resource_manager, text_converter
            )
            for page in PDFPage.get_pages(input_file):
                interpreter.process_page(page)

            raw_txt = return_data.getvalue()

            # Define some variables used to track how to parse next.
            start_parsing = False
            next_transaction_type = None
            transaction = None

            # Loop over text line-by-line while ignoring empty lines & newlines.
            for line in [line for line in raw_txt.split('\n') if line != '']:
                # Only start parsing after finding a specific line
                # to skip useless header information.
                if not start_parsing:
                    start_parsing = line == 'deposited ($)'
                    continue

                # TODO: Figure out why parsing is not chronological
                # print(f'Line: {line}')
                # If the transaction type is not set, set what is coming next.
                if next_transaction_type is None:
                    for transaction_type in ScotiaBankTransactionTypeEnum:
                        if transaction_type.value in line:
                            next_transaction_type = transaction_type.value
                            transaction = Transaction()
                            print(f'MATCHED AS: {next_transaction_type}')
                            break
                # Otherwise
                else:
                    print(f'Parsing as: {next_transaction_type}')
                    # Reset variables after parsing transaction finished.
                    if transaction.is_complete():
                        transaction.save()
                        # Clear for next parse.
                        next_transaction_type = None
                    else:
                        # Try to match on dollar amounts.
                        if re.search(f'^{self.amount_regex_pattern}$', line):
                            if Transaction.amount is None:
                                Transaction.amount = float(line.replace(',', ''))
                        elif line.startswith(tuple([month.value for month in MonthEnum])):
                            if Transaction.posted_date is None:
                                Transaction.posted_date = line
                        else:
                            Transaction.description = line
                            Transaction.type = next_transaction_type
                        # TODO: Stop parsing when line matched 'Page X from X'?
