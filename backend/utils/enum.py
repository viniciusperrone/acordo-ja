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

class MethodPayment(Enum):
    PIX = "PIX"
    BOLETO = "BOLETO"
    TED = "TED"
    CARTAO = "CARTAO"
    DINHEIRO = "DINHEIRO"

class UserRole(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    AGENT = "AGENT"

class NotificationType(Enum):
    NEW_LEAD = "NEW_LEAD"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    INSTALLMENT_OVERDUE = "INSTALLMENT_OVERDUE"
    AGREEMENT_CREATED = "AGREEMENT_CREATED"
    AGREEMENT_COMPLETED = "AGREEMENT_COMPLETED"
    DEBT_PAID = "DEBT_PAID"
    GENERAL = "GENERAL"
