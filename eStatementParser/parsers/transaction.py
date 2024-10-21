from datetime import date
from decimal import Decimal


class Transaction:
    amount: Decimal = None
    description: str = None
    leftover_balance: Decimal = None
    posted_date: date = None
    type: str = None

    def __str__(self):
        return f'{self.type} | {self.posted_date} ' \
               f'| {self.amount} | {self.description}'

    def is_complete(self) -> bool:
        return self.amount is not None \
               and self.description is not None \
               and self.leftover_balance is not None \
               and self.posted_date is not None \
               and self.type is not None

    def save(self):
        # TODO: Figure out how to store.
        pass
