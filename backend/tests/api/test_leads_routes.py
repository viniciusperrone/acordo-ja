import pytest

from leads.models import Lead
from notifications.models import Notification


@pytest.mark.api
class TestLeadsRoutes:
    """
    API tests for lead creation endpoints.

    Covers successful lead creation, notification dispatching,
    and request validation scenarios.
    """
    def test_create_lead_success(self, client, session):
        response = client.post(
            '/leads/add',
            json={
                'name': 'João Test',
                'email': 'joao@test.com',
                'document': '529.982.247-25',
                'phone': '11999999999'
            }
        )

        assert response.status_code == 201

        lead = Lead.query.filter_by(email='joao@test.com').first()

        assert lead is not None
        assert lead.name == 'João Test'

    def test_create_lead_creates_notification(self, client, session, admin_user, manager_user, agent_user):
        response = client.post(
            '/leads/add',
            json={
                'name': 'João Test',
                'email': 'joao@test.com',
                'document': '529.982.247-25',
                'phone': '11999999999'
            }
        )

        assert response.status_code == 201

        notifications = Notification.query.all()

        assert len(notifications) == 3

        user_ids = [str(n.user_id) for n in notifications]
        assert str(admin_user.id) in user_ids
        assert str(manager_user.id) in user_ids
        assert str(agent_user.id) in user_ids

    def test_create_lead_without_document(self, client):
        response = client.post(
            '/leads/add',
            json={'name': 'Test'}
        )

        assert response.status_code == 400

    def test_create_lead_without_name_returns_400(self, client):
        response = client.post(
            "/leads/add",
            json={
                "email": "joao@test.com",
                "document": "529.982.247-25",
                "phone": "11999999999",
            },
        )

        assert response.status_code == 400
