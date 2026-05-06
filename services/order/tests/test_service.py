from __future__ import annotations

from decimal import Decimal

import pytest

from services.order.schemas import OrderCreate
from services.order.service import create_order, get_user_orders


def test_create_order_service_moves_to_paid_and_calculates_amount(seeded_db):
    db, ids = seeded_db

    order = create_order(
        db,
        OrderCreate(
            user_id=ids["user_id"],
            items=[{"product_id": ids["product_id"], "quantity": 1}],
        ),
    )

    assert order.status == "paid"
    assert Decimal(order.final_amount) == Decimal("102.59")


def test_bug_index_error_no_longer_raises_for_user_without_orders(seeded_db, monkeypatch):
    db, ids = seeded_db
    monkeypatch.setenv("BUG_INDEX_ERROR", "true")

    # After fix: should return empty list without raising IndexError
    result = get_user_orders(db, ids["second_user_id"])
    assert result == []


def test_bug_coupon_lookup_key_error_no_longer_raises_for_unknown_coupon(seeded_db, monkeypatch):
    db, ids = seeded_db
    monkeypatch.setenv("BUG_ORDER_COUPON_KEY", "true")

    # After fix: unknown coupon codes should not cause KeyError; should create order successfully
    order = create_order(
        db,
        OrderCreate(
            user_id=ids["user_id"],
            items=[{"product_id": ids["product_id"], "quantity": 1}],
            coupon_code="FLASH50",
        ),
    )
    assert order.status == "paid"
