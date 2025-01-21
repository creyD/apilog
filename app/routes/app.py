from uuid import UUID

from creyPY.fastapi.crud import create_obj_from_data
from creyPY.fastapi.db.session import get_db
from creyPY.fastapi.pagination import Page, paginate
from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.app import Application
from app.schema.app import AppIN, AppOUT
from app.services.auth import verify

router = APIRouter(prefix="/app", tags=["apps"])


@router.post("/", status_code=201)
async def create_app(
    data: AppIN,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> AppOUT:
    obj = create_obj_from_data(
        data,
        Application,
        db,
        additional_data={"created_by_id": sub},
    )
    return AppOUT.model_validate(obj)


@router.delete("/{app_id}", status_code=204)
async def delete_app(
    app_id: UUID,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> None:
    obj = db.query(Application).filter_by(id=app_id, created_by_id=sub).one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(obj)
    db.commit()
    return None


@router.get("/")
async def get_apps(
    search: str | SkipJsonSchema[None] = None,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> Page[AppOUT]:
    the_select = select(Application).filter(Application.created_by_id == sub)
    if search:
        the_select = the_select.filter(Application.name.ilike(f"%{search}%"))
    return paginate(db, the_select)


@router.get("/{app_id}")
async def get_app(
    app_id: UUID,
    sub: str = Security(verify),
    db: Session = Depends(get_db),
) -> AppOUT:
    obj = db.query(Application).filter_by(id=app_id, created_by_id=sub).one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return AppOUT.model_validate(obj)
