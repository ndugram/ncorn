# Примеры

## Базовое приложение FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Example App")

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root():
    return {"message": "Hello from ncorn!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 1 or item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.post("/items")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

Запуск:

```bash
ncorn example:app
```

## REST API с CRUD операциями

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

items = {}
item_id = 0

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items")
async def create_item(item: Item):
    global item_id
    item_id += 1
    items[item_id] = item
    return {"id": item_id, **item.dict()}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items[item_id].dict()}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item
    return {"id": item_id, **item.dict()}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"deleted": True}
```

## Параметры запроса и валидация

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

class User(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    age: int = Field(ge=0, le=150)

@app.get("/users")
async def list_users(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return {"limit": limit, "offset": offset, "users": []}

@app.post("/users")
async def create_user(user: User):
    return user
```

## Типы тела запроса

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

class Order(BaseModel):
    items: List[Item]
    priority: bool = False

@app.post("/order")
async def create_order(order: Order):
    total = sum(item.price for item in order.items)
    return {
        "items": order.items,
        "total": total,
        "priority": order.priority,
    }
```

## Обработка ошибок

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/error")
async def trigger_error():
    raise HTTPException(status_code=400, detail="Custom error message")
```

## Зависимости

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def get_current_user():
    return {"username": "user123"}

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return user
```

## Кастомная конфигурация

```python
from ncorn.config import Config
from ncorn.server import HTTPServer
from myapp import app

config = Config(
    host="0.0.0.0",
    port=9000,
    workers=4,
    max_body_size=32 * 1024 * 1024,
    rate_limit_requests=200,
    rate_limit_window=60.0,
)

server = HTTPServer(app, config)
```

## Тестирование с cURL

```bash
# GET запрос
curl http://localhost:8000/

# POST запрос
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "price": 9.99}'
```
