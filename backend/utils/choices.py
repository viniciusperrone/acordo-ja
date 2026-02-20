from enum import Enum

DEBT_STATUS_CHOICES = (
    ("OPEN", "Aberta"),
    ("IN_AGREEMENT", "Em Acordo"),
    ("PAID", "Quitada"),
    ("DEFAULTED", "Inadimplente"),
    ("CANCELLED", "Cancelada"),
)

INSTALLMENT_STATUS_CHOICES = (
    ('PENDING', 'Pendente'),
    ('PAID', 'Paga'),
    ('OVERDUE', 'Atrasada'),
    ('CANCELLED', 'Cancelada'),
)

AGREEMENT_STATUS_CHOICES = (
    ('DRAFT', 'Rascunho'),
    ('ACTIVE', 'Ativo'),
    ('CANCELLED', 'Cancelado'),
    ('COMPLETED',  'Concluído')
)
