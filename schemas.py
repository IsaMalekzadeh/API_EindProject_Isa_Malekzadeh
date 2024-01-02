from pydantic import BaseModel


class DrinkBase(BaseModel):
    name: str
    description: str


class DrinkCreate(DrinkBase):
    pass


class Drink(DrinkBase):
    id: int

    class Config:
        orm_mode = True


class StockBase(BaseModel):
    quantity: int
    price: float


class StockCreate(StockBase):
    pass


class Stock(StockBase):
    id: int
    drink: Drink

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True