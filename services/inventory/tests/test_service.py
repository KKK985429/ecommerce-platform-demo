from __future__ import annotations

import pytest

from services.inventory.service import get_inventory, reserve_inventory


def test_reserve_inventory_increases_reserved_qty(seeded_db):
    db, ids = seeded_db

    reserve_inventory(
        db,
        order_id=1,
        items=[{"product_id": ids["product_id"], "quantity": 2}],
    )
    inventory = get_inventory(db, ids["product_id"])

    assert inventory.reserved_qty == 2


def test_get_inventory_returns_data_even_with_bug_flags(seeded_db, monkeypatch):
    """Regression test: bug flags no longer cause AttributeError."""
    db, ids = seeded_db
    monkeypatch.setenv("BUG_INVENTORY_MISSING_ROW", "true")
    monkeypatch.setenv("BUG_INVENTORY_BROKEN_PRODUCT_ID", str(ids["product_id"]))

    inventory = get_inventory(db, ids["product_id"])
    assert inventory is not None
    assert inventory.product_id == ids["product_id"]
    assert inventory.total_qty == 10
