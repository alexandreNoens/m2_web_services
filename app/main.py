import base64
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models, schemas
from app.database import Base, engine, get_db


app = FastAPI(title="Miamzy API", version="1.0.0")
logger = logging.getLogger(__name__)


class ApiProblem(Exception):
    def __init__(self, status: int, title: str, detail: str, problem_type: str | None = None):
        self.status = status
        self.title = title
        self.detail = detail
        self.problem_type = problem_type


def problem_response(request: Request, status: int, title: str, detail: str, problem_type: str | None = None):
    body = schemas.Problem(
        type=problem_type or "about:blank",
        title=title,
        status=status,
        detail=detail,
        instance=request.url.path,
    )
    return JSONResponse(
        status_code=status,
        content=body.model_dump(mode="json", by_alias=True),
        media_type="application/problem+json",
    )


@app.exception_handler(ApiProblem)
async def api_problem_handler(request: Request, exc: ApiProblem):
    return problem_response(request, exc.status, exc.title, exc.detail, exc.problem_type)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        errors.append(f"{location}: {error['msg']}")
    return problem_response(
        request,
        422,
        "Donnees invalides",
        "; ".join(errors),
        "https://miamzy.dev/errors/validation",
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return problem_response(request, exc.status_code, "Erreur HTTP", str(exc.detail))


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled API error", exc_info=exc)
    return problem_response(
        request,
        500,
        "Erreur interne",
        "Une erreur interne est survenue.",
        "https://miamzy.dev/errors/internal",
    )


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(engine)


def encode_cursor(order: models.Order) -> str:
    payload = json.dumps(
        {"createdAt": order.created_at.isoformat(), "id": str(order.id)},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded).decode())
        return datetime.fromisoformat(data["createdAt"]), uuid.UUID(data["id"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise ApiProblem(422, "Curseur invalide", "Le curseur de pagination est invalide.")


@app.get("/v1/orders", response_model=schemas.OrderListResponse, response_model_by_alias=True)
def list_orders(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = None,
    db: Session = Depends(get_db),
):
    statement = select(models.Order).order_by(models.Order.created_at.desc(), models.Order.id.desc())
    if cursor:
        created_at, order_id = decode_cursor(cursor)
        statement = statement.where(
            or_(
                models.Order.created_at < created_at,
                and_(models.Order.created_at == created_at, models.Order.id < order_id),
            )
        )

    orders = list(db.scalars(statement.limit(limit + 1)))
    has_next_page = len(orders) > limit
    orders = orders[:limit]
    next_cursor = encode_cursor(orders[-1]) if has_next_page else None
    return schemas.OrderListResponse(data=orders, next_cursor=next_cursor)


@app.get("/v1/orders/{order_id}", response_model=schemas.Order, response_model_by_alias=True)
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db)):
    order = db.scalar(
        select(models.Order)
        .where(models.Order.id == order_id)
        .options(selectinload(models.Order.items))
    )
    if order is None:
        raise ApiProblem(404, "Commande introuvable", "Aucune commande ne correspond a cet identifiant.")
    return order


@app.post(
    "/v1/restaurants/{restaurant_id}/orders",
    response_model=schemas.Order,
    response_model_by_alias=True,
    status_code=201,
)
def create_order(
    restaurant_id: uuid.UUID,
    request: schemas.CreateOrderRequest,
    db: Session = Depends(get_db),
):
    restaurant = db.get(models.Restaurant, restaurant_id)
    if restaurant is None:
        raise ApiProblem(404, "Restaurant introuvable", "Aucun restaurant ne correspond a cet identifiant.")
    if not restaurant.is_open:
        raise ApiProblem(409, "Restaurant ferme", "Ce restaurant ne prend pas de commandes actuellement.")
    if db.get(models.User, request.user_id) is None:
        raise ApiProblem(404, "Utilisateur introuvable", "Aucun utilisateur ne correspond a cet identifiant.")

    requested_ids = {item.menu_item_id for item in request.items}
    menu_items = {
        item.id: item
        for item in db.scalars(select(models.MenuItem).where(models.MenuItem.id.in_(requested_ids)))
    }
    if len(menu_items) != len(requested_ids):
        raise ApiProblem(404, "Article introuvable", "Au moins un article demande est introuvable.")

    order_items = []
    total = 0
    for requested_item in request.items:
        menu_item = menu_items[requested_item.menu_item_id]
        if menu_item.restaurant_id != restaurant_id:
            raise ApiProblem(409, "Article invalide", "Un article n'appartient pas a ce restaurant.")
        if not menu_item.is_available:
            raise ApiProblem(409, "Article indisponible", f"L'article {menu_item.name} est indisponible.")
        total += menu_item.price_cents * requested_item.quantity
        order_items.append(
            models.OrderItem(
                menu_item_id=menu_item.id,
                name=menu_item.name,
                quantity=requested_item.quantity,
                unit_price_cents=menu_item.price_cents,
            )
        )

    now = datetime.now(timezone.utc)
    order = models.Order(
        id=uuid.uuid4(),
        restaurant_id=restaurant_id,
        user_id=request.user_id,
        status="pending_payment",
        total_amount_cents=total,
        currency="EUR",
        created_at=now,
        updated_at=now,
        items=order_items,
    )
    db.add(order)
    db.commit()
    return order


@app.post(
    "/v1/orders/{order_id}/payments",
    response_model=schemas.Payment,
    response_model_by_alias=True,
    status_code=201,
)
def create_payment(
    order_id: uuid.UUID,
    request: schemas.CreatePaymentRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=128),
    db: Session = Depends(get_db),
):
    fingerprint = hashlib.sha256(
        f"{order_id}:{request.method}:{request.card_token}".encode()
    ).hexdigest()
    existing = db.scalar(
        select(models.Payment).where(models.Payment.idempotency_key == idempotency_key)
    )
    if existing is not None:
        if existing.request_fingerprint != fingerprint:
            raise ApiProblem(
                409,
                "Cle d'idempotence deja utilisee",
                "Cette cle correspond deja a une autre requete de paiement.",
            )
        return existing

    order = db.get(models.Order, order_id)
    if order is None:
        raise ApiProblem(404, "Commande introuvable", "Aucune commande ne correspond a cet identifiant.")
    if order.status == "cancelled":
        raise ApiProblem(
            409,
            "Commande annulee",
            "Une commande annulee ne peut pas etre payee.",
            "https://miamzy.dev/errors/order-cancelled",
        )
    if request.card_token == "tok_declined":
        raise ApiProblem(402, "Paiement refuse", "Le prestataire de paiement a refuse la carte.")

    now = datetime.now(timezone.utc)
    payment = models.Payment(
        id=uuid.uuid4(),
        order_id=order.id,
        amount_cents=order.total_amount_cents,
        currency=order.currency,
        method=request.method,
        status="succeeded",
        paid_at=now,
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
    )
    order.status = "paid"
    order.updated_at = now
    db.add(payment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        concurrent = db.scalar(
            select(models.Payment).where(models.Payment.idempotency_key == idempotency_key)
        )
        if concurrent is not None and concurrent.request_fingerprint == fingerprint:
            return concurrent
        raise ApiProblem(409, "Cle d'idempotence deja utilisee", "Cette cle est deja utilisee.")
    return payment


@app.get(
    "/v1/users/{user_id}/profile",
    response_model=schemas.UserProfile,
    response_model_by_alias=True,
)
def get_user_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if user is None:
        raise ApiProblem(404, "Utilisateur introuvable", "Aucun utilisateur ne correspond a cet identifiant.")
    return user
