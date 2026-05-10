import pytest
from order import Order

def test_正常訂單():
    order = Order(order_id="A001", product_name="鍵盤", quantity=2, price_per_unit=999.0)
    assert order.total_price() == 1998.0

def test_quantity錯誤():
    with pytest.raises(Exception):
        Order(order_id="A002", product_name="滑鼠", quantity=0, price_per_unit=500.0)

def test_price錯誤():
    with pytest.raises(Exception):
        Order(order_id="A003", product_name="螢幕", quantity=1, price_per_unit=-100.0)