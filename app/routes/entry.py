from creyPY.fastapi.crud import (
    create_obj_from_data,
)
from creyPY.fastapi.db.session import get_db
from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session

from app.services.auth import verify
from app.schema.entry import LogIN, LogOUT
from app.models.entry import LogEntry
from fastapi_pagination.ext.sqlalchemy import paginate
from creyPY.fastapi.pagination import Page
from uuid import UUID

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
        additonal_data={"created_by_id": sub},
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
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> Page[LogOUT]:
    the_select = db.query(LogEntry).filter_by(created_by_id=sub)
    return paginate(the_select)
