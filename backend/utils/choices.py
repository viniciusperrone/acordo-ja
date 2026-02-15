from enum import Enum

DEBT_STATUS_CHOICES = (
    ('PENDING', 'Pendente'),
    ('IN NEGOTIATION', 'Em negociação'),
    ('RENEGOTIATED', 'Renegociada'),
    ('PAID OFF','Quitada')
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