import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app import models
from app.database import Base, SessionLocal, engine


NAMESPACE = uuid.UUID("ca42e9e2-43bb-4ab5-b91f-94a06fc445df")
RESTAURANT_COUNT = 20
USER_COUNT = 100
ORDER_COUNT = 5_000
MENU_ITEMS_PER_RESTAURANT = 5


def stable_uuid(resource: str, number: int) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{resource}-{number}")


def seed_database():
    Base.metadata.create_all(engine)
    rng = random.Random(42)
    now = datetime.now(timezone.utc).replace(microsecond=0)

    users = [
        models.User(
            id=stable_uuid("user", index),
            first_name=f"Prenom{index}",
            last_name=f"Utilisateur{index}",
            email=f"user{index}@example.test",
            phone=f"060000{index:04d}",
            password_hash="$2b$12$demonstration-hash-not-a-real-password",
            created_at=now - timedelta(days=365 - index),
        )
        for index in range(1, USER_COUNT + 1)
    ]
    restaurants = [
        models.Restaurant(
            id=stable_uuid("restaurant", index),
            name=f"Restaurant Miamzy {index}",
            is_open=index % 10 != 0,
        )
        for index in range(1, RESTAURANT_COUNT + 1)
    ]

    menu_items = []
    menu_names = ["Burger classique", "Pizza margherita", "Bowl vegetarien", "Tacos poulet", "Tiramisu"]
    for restaurant_index, restaurant in enumerate(restaurants, start=1):
        for item_index, name in enumerate(menu_names, start=1):
            menu_items.append(
                models.MenuItem(
                    id=stable_uuid("menu-item", (restaurant_index - 1) * MENU_ITEMS_PER_RESTAURANT + item_index),
                    restaurant_id=restaurant.id,
                    name=name,
                    price_cents=700 + restaurant_index * 15 + item_index * 175,
                    is_available=item_index != MENU_ITEMS_PER_RESTAURANT,
                )
            )

    orders = []
    for index in range(1, ORDER_COUNT + 1):
        restaurant_index = (index - 1) % RESTAURANT_COUNT
        restaurant = restaurants[restaurant_index]
        user = users[(index - 1) % USER_COUNT]
        menu_item = menu_items[restaurant_index * MENU_ITEMS_PER_RESTAURANT + index % 4]
        quantity = rng.randint(1, 3)
        created_at = now - timedelta(minutes=index)
        status = "cancelled" if index % 17 == 0 else "paid" if index % 3 == 0 else "pending_payment"
        orders.append(
            models.Order(
                id=stable_uuid("order", index),
                restaurant_id=restaurant.id,
                user_id=user.id,
                status=status,
                total_amount_cents=menu_item.price_cents * quantity,
                currency="EUR",
                created_at=created_at,
                updated_at=created_at,
                items=[
                    models.OrderItem(
                        menu_item_id=menu_item.id,
                        name=menu_item.name,
                        quantity=quantity,
                        unit_price_cents=menu_item.price_cents,
                    )
                ],
            )
        )

    with SessionLocal() as db:
        # Le seed est rejouable et remet la base dans un etat de demonstration connu.
        for model in (
            models.Payment,
            models.OrderItem,
            models.Order,
            models.MenuItem,
            models.Restaurant,
            models.User,
        ):
            db.execute(delete(model))
        db.add_all(users)
        db.add_all(restaurants)
        db.flush()
        db.add_all(menu_items)
        db.flush()
        db.add_all(orders)
        db.commit()

    print(f"Seed termine: {RESTAURANT_COUNT} restaurants et {ORDER_COUNT} commandes.")
    print(f"Restaurant de test: {stable_uuid('restaurant', 1)}")
    print(f"Article de test: {stable_uuid('menu-item', 1)}")
    print(f"Utilisateur de test: {stable_uuid('user', 1)}")
    print(f"Commande de test: {stable_uuid('order', 1)}")


if __name__ == "__main__":
    seed_database()
