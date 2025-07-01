from pydantic import BaseModel


class ProductShema(BaseModel):
    marketplace: str
    artikul: str
    name: str


class ProductHistoryShema(BaseModel):
    standart_price: float
    sell_price: float
    total_quantity: int
    rating: float


class ProductRequest(BaseModel):
    artikul: str
