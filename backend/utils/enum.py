from enum import Enum


class AgreementStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class InstallmentStatus(Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    OVERDUE = 'OVERDUE'
    CANCELLED = 'CANCELLED'


class DebtStatus(Enum):
    OPEN = "OPEN"
    IN_AGREEMENT = "IN_AGREEMENT"
    PAID = "PAID"
    DEFAULTED = "DEFAULTED"
    CANCELLED = "CANCELLED"
