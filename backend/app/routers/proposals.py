"""
Модуль API-маршрутов для составления смет эксперта (Proposals Router).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OrderRequest, Proposal, ProposalItem, ProposalAlternative
from app.schemas import ProposalCreate, ProposalResponse

router = APIRouter(
    prefix="/api/v1/proposals",
    tags=["Сметы и Ответы Эксперта (Proposals)"]
)


@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(
    data: ProposalCreate,
    db: Session = Depends(get_db)
):
    """
    (Для Админа) Формирование и отправка сметы подбора клиенту.
    
    Принимает категории, оригинальные OE номера и варианты аналогов с ценами.
    Переводит статус запроса клиенту в "completed" (Обработан).
    """
    # 1. Проверяем наличие запроса
    req = db.query(OrderRequest).filter(OrderRequest.id == data.request_id).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запрос с ID {data.request_id} не найден"
        )

    # 2. Проверяем, нет ли уже сметы по этому запросу
    existing_prop = db.query(Proposal).filter(Proposal.request_id == data.request_id).first()
    if existing_prop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Смета по этому запросу уже была составлена ранее!"
        )

    # 3. Создаем шапку сметы
    new_proposal = Proposal(
        request_id=req.id,
        car_id=req.car_id,
        manager_comment=data.manager_comment
    )
    db.add(new_proposal)
    db.flush()

    # 4. Добавляем позиции и варианты аналогов
    for item_in in data.items:
        new_item = ProposalItem(
            proposal_id=new_proposal.id,
            category_name=item_in.category_name,
            oem_number=item_in.oem_number
        )
        db.add(new_item)
        db.flush()

        for alt_in in item_in.alternatives:
            new_alt = ProposalAlternative(
                item_id=new_item.id,
                brand=alt_in.brand,
                part_number=alt_in.part_number,
                price=alt_in.price,
                delivery_term=alt_in.delivery_term or "1-2 дня"
            )
            db.add(new_alt)

    # 5. Обновляем статус запроса на "completed"
    req.status = "completed"

    db.commit()
    db.refresh(new_proposal)

    return new_proposal


@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal_by_id(proposal_id: int, db: Session = Depends(get_db)):
    """Получение деталей сметы по её ID"""
    prop = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Смета не найдена")
    return prop
