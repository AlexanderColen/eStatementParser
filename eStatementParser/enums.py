from enum import Enum


class BankEnum(Enum):
    BMO = 'BMO'
    SCOTIABANK = 'Scotiabank'


class MonthEnum(Enum):
    JANUARY = 'Jan'
    FEBRUARY = 'Feb'
    MARCH = 'Mar'
    APRIL = 'Apr'
    MAY = 'May'
    JUNE = 'Jun'
    JULY = 'Jul'
    AUGUST = 'Aug'
    SEPTEMBER = 'Sep'
    OCTOBER = 'Oct'
    NOVEMBER = 'Nov'
    DECEMBER = 'Dec'


class TransactionTypeEnum(Enum):
    BILL_PAYMENT = 'MB-Bill payment'
    ERROR_CORRECTION = 'Error correction'
    INCOMING_TRANSFER = 'MB-Transfer from'
    MISCELLANEOUS_PAYMENT = 'Misc. payment'
    OUTGOING_TRANSFER = 'Withdrawal'
    PURCHASE = 'Point of sale purchase'
    SALARY = 'Payroll dep.'
