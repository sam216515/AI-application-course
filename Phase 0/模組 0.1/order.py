from pydantic import BaseModel, field_validator
from typing import Optional

class Order(BaseModel):
    order_id: str
    product_name: str
    quantity: int
    price_per_unit: float
    note: Optional[str] = None


    @field_validator("quantity")
    @classmethod
    def quantity_validcheck(cls, v):
        if v < 1:
            raise ValueError("數量必須是1或以上")
        return v

    @field_validator("price_per_unit")
    @classmethod
    def price_vaild(cls, v):
        if v <= 0:
            raise ValueError("價格必須是0以上")
        return v


    def total_price(self):
        return self.quantity * self.price_per_unit



order = Order(order_id="A001", product_name="鍵盤", quantity=2, price_per_unit=999.0)
print(order.total_price())  # 應該印出 1998.0

try:
    bad = Order(order_id="A002", product_name="滑鼠", quantity=0, price_per_unit=500.0)
except Exception as e:
    print(e)

try:
    bad2 = Order(order_id="A003", product_name="螢幕", quantity=1, price_per_unit=-100.0)
except Exception as e:
    print(e)