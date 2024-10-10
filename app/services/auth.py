from uuid import UUID

from creyPY.fastapi.db.session import get_db
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyQuery
from sqlalchemy.orm import Session

from app.models.auth import APIKey

load_dotenv()


async def verify(
    request: Request,
    api_key_query: str = Security(APIKeyQuery(name="api-key", auto_error=False)),
    db: Session = Depends(get_db),
) -> str:
    if api_key_query:
        key_info = db.query(APIKey).filter_by(id=UUID(api_key_query)).one_or_none()
        if key_info is None:
            raise HTTPException(status_code=401, detail="Invalid API key.")
        return f"API-KEY: {key_info.note}"
    raise HTTPException(status_code=401, detail="No API key.")
