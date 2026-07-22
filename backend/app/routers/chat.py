"""
Модуль API-маршрутів для внутрішнього чату (Chat Router).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, OrderRequest, ChatMessage
from app.schemas import ChatMessageCreate, ChatMessageResponse
from app.routers.auth import get_current_client

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Внутрішній Чат (In-App Chat)"]
)


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def send_chat_message(
    data: ChatMessageCreate,
    sender_type: str = Query("client", description="client або manager"),
    current_client: Optional[Client] = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Надсилання повідомлення у чат по запиту (клієнтом або менеджером).
    """
    req = db.query(OrderRequest).filter(OrderRequest.id == data.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Запит не знайдено")

    client_id = current_client.id if current_client else req.client_id

    new_msg = ChatMessage(
        request_id=req.id,
        client_id=client_id,
        sender_type=sender_type,
        message=data.message.strip(),
        attachment_url=data.attachment_url
    )

    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    return new_msg


@router.get("/messages/{request_id}", response_model=List[ChatMessageResponse])
def get_chat_messages(
    request_id: int,
    db: Session = Depends(get_db)
):
    """Отримання історії чату по запиту"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.request_id == request_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages
