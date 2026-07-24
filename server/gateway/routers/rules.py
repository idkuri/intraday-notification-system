from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from lib.exceptions import DomainValidationError, NotFoundError
from lib.schemas.rules import RuleCreate, RuleRead, RuleUpdate

from gateway.deps import get_actor_username, get_rule_service
from rules.rule_service import RuleService

router = APIRouter()


@router.get("", response_model=list[RuleRead])
def list_rules(
    service: RuleService = Depends(get_rule_service),
    actor: str = Depends(get_actor_username),
) -> list[RuleRead]:
    return service.list_rules(actor=actor)


@router.get("/{rule_id}", response_model=RuleRead)
def get_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service),
    actor: str = Depends(get_actor_username),
) -> RuleRead:
    try:
        return service.require_rule(rule_id, actor=actor)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=RuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: RuleCreate,
    service: RuleService = Depends(get_rule_service),
    actor: str = Depends(get_actor_username),
) -> RuleRead:
    try:
        return service.create_rule(data, actor=actor)
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{rule_id}", response_model=RuleRead)
def update_rule(
    rule_id: str,
    data: RuleUpdate,
    service: RuleService = Depends(get_rule_service),
    actor: str = Depends(get_actor_username),
) -> RuleRead:
    try:
        return service.update_rule(rule_id, data, actor=actor)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service),
    actor: str = Depends(get_actor_username),
) -> Response:
    try:
        service.delete_rule(rule_id, actor=actor)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def register_router(app: FastAPI | APIRouter) -> None:
    """Mount the rules routes on ``app``."""
    app.include_router(router, prefix="/rules", tags=["rules"])
