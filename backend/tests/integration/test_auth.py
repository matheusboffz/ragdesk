from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.models.conversation import Conversation, Message, MessageRole
from app.models.document import Chunk, Document
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User


def test_register_and_login_flow(client: TestClient) -> None:
    register_res = client.post(
        "/auth/register",
        json={
            "name": "Alice Silva",
            "email": "Alice@Example.com",
            "password": "StrongPassword123!",
            "role": "user",
        },
    )
    assert register_res.status_code == 201
    reg_data = register_res.json()
    assert "access_token" in reg_data
    assert reg_data["token_type"] == "bearer"
    assert reg_data["user"]["email"] == "alice@example.com"
    assert reg_data["user"]["role"] == "user"

    # Duplicate email returns 409 Conflict
    dup_res = client.post(
        "/auth/register",
        json={
            "name": "Alice Duplicate",
            "email": "alice@example.com",
            "password": "StrongPassword123!",
            "role": "user",
        },
    )
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    # Login with valid credentials returns 200
    login_res = client.post(
        "/auth/login",
        json={
            "email": "ALICE@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Access /auth/me with valid Bearer token
    me_res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["name"] == "Alice Silva"


def test_login_invalid_credentials_and_missing_token(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "name": "Bob User",
            "email": "bob@example.com",
            "password": "ValidPassword123!",
        },
    )

    wrong_pw = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "WrongPassword!"},
    )
    assert wrong_pw.status_code == 401
    assert wrong_pw.json()["error"]["code"] == "INVALID_CREDENTIALS"

    unauth_me = client.get("/auth/me")
    assert unauth_me.status_code == 401
    assert unauth_me.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_rbac_require_admin_dependency(client: TestClient) -> None:
    # Attach a test admin-only route to the app instance
    @client.app.get("/admin-only-check")  # type: ignore[union-attr]
    def admin_only_route(admin_user: User = Depends(require_admin)) -> dict[str, str]:
        return {"admin_email": admin_user.email}

    user_reg = client.post(
        "/auth/register",
        json={
            "name": "Regular User",
            "email": "user@ragdesk.dev",
            "password": "Password123!",
            "role": "user",
        },
    )
    user_token = user_reg.json()["access_token"]

    admin_reg = client.post(
        "/auth/register",
        json={
            "name": "Admin User",
            "email": "admin@ragdesk.dev",
            "password": "Password123!",
            "role": "admin",
        },
    )
    admin_token = admin_reg.json()["access_token"]

    # Regular user gets 403 Forbidden
    forbidden_res = client.get(
        "/admin-only-check",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert forbidden_res.status_code == 403
    assert forbidden_res.json()["error"]["code"] == "FORBIDDEN_ADMIN_ONLY"

    # Admin user gets 200 OK
    allowed_res = client.get(
        "/admin-only-check",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert allowed_res.status_code == 200
    assert allowed_res.json()["admin_email"] == "admin@ragdesk.dev"


def test_orm_models_and_relationships(db_session: Session) -> None:
    user = User(
        name="Model Tester",
        email="models@ragdesk.dev",
        password_hash="hashed",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()

    doc = Document(
        title="Política de Reembolso",
        filename="reembolso.pdf",
        content_type="application/pdf",
        file_size=2048,
        uploaded_by=user.id,
    )
    chunk = Chunk(
        chunk_index=0,
        page_number=1,
        content="O prazo de reembolso é de até 7 dias corridos.",
        embedding=[0.01] * 768,
    )
    doc.chunks.append(chunk)
    db_session.add(doc)
    db_session.commit()

    conv = Conversation(user_id=user.id, title="Dúvida sobre reembolso")
    msg = Message(
        role=MessageRole.ASSISTANT.value,
        content="O prazo é de 7 dias [reembolso.pdf, p. 1].",
        sources=[{"document": "reembolso.pdf", "page": 1}],
    )
    conv.messages.append(msg)
    db_session.add(conv)
    db_session.commit()

    ticket = Ticket(
        user_id=user.id,
        conversation_id=conv.id,
        question="Como funciona o plano enterprise internacional?",
        status=TicketStatus.OPEN.value,
    )
    db_session.add(ticket)
    db_session.commit()

    assert len(doc.chunks) == 1
    assert doc.chunks[0].page_number == 1
    assert len(conv.messages) == 1
    assert conv.messages[0].sources[0]["document"] == "reembolso.pdf"
    assert ticket.status == "open"
