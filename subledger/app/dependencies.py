from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.services import build_services


def get_db(request: Request) -> Session:
    return request.state.db


def get_services(db: Session = Depends(get_db)) -> dict:
    return build_services(db)
