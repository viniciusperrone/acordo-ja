from enum import Enum


class AgreementStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
