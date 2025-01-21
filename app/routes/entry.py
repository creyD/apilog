from datetime import datetime
from typing import Callable
from uuid import UUID

from creyPY.fastapi.crud import create_obj_from_data
from creyPY.fastapi.db.session import get_db
from creyPY.fastapi.order_by import order_by
from creyPY.fastapi.pagination import Page, paginate
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_filters import FilterValues, create_filters
from fastapi_filters.ext.sqlalchemy import apply_filters
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

from app.models.entry import LogEntry, LogType, TransactionType
from app.schema.entry import LogIN, LogOUT
from app.services.auth import verify

router = APIRouter(prefix="/log", tags=["logging"])


@router.post("/", status_code=201)
async def create_log(
    data: LogIN,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> LogOUT:
    obj = create_obj_from_data(
        data,
        LogEntry,
        db,
        additional_data={"created_by_id": sub},
    )
    return LogOUT.model_validate(obj)


@router.delete("/{log_id}", status_code=204)
async def delete_log(
    log_id: UUID,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> None:
    obj = db.query(LogEntry).filter_by(id=log_id, created_by_id=sub).one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(obj)
    db.commit()
    return None


@router.get("/{log_id}")
async def get_log(
    log_id: UUID,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> LogOUT:
    obj = db.query(LogEntry).filter_by(id=log_id, created_by_id=sub).one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return LogOUT.model_validate(obj)


@router.get("/")
async def get_logs(
    search: str | SkipJsonSchema[None] = None,
    order_by_query: Callable[[Select], Select] = Depends(order_by),
    filters: FilterValues = Depends(
        create_filters(
            created_by_id=str,
            environment=str,
            l_type=LogType,
            t_type=TransactionType,
            application=UUID,
            object_reference=str,
            author=str,
            created_at=datetime,
        )
    ),
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> Page[LogOUT]:
    """
    Filter logs of your systems. Searching works only for author and message. Use filters for the rest.
    """
    the_select = apply_filters(select(LogEntry).filter(LogEntry.created_by_id == sub), filters)
    if search:
        the_select = the_select.filter(
            LogEntry.message.ilike(f"%{search}%") | LogEntry.author.ilike(f"%{search}%")
        )
    return paginate(db, order_by_query(the_select))


@router.delete("/", status_code=200, operation_id="log_delete_many")
async def delete_logs(
    application: UUID,
    environment: str | SkipJsonSchema[None] = None,
    l_type: LogType | SkipJsonSchema[None] = None,
    t_type: TransactionType | SkipJsonSchema[None] = None,
    object_reference: str | SkipJsonSchema[None] = None,
    author: str | SkipJsonSchema[None] = None,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> int:
    filters = {
        "application": application,
        "created_by_id": sub,
    }

    if environment is not None:
        filters["environment"] = environment
    if l_type is not None:
        filters["l_type"] = l_type
    if t_type is not None:
        filters["t_type"] = t_type
    if object_reference is not None:
        filters["object_reference"] = object_reference
    if author is not None:
        filters["author"] = author

    query = db.query(LogEntry).filter_by(**filters)
    the_impact = query.count()
    query.delete(synchronize_session=False)
    db.commit()
    return the_impact
