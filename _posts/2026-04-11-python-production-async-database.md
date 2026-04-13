---
layout: post
title: "Async Database Operations"
description: "SQLAlchemy async sessions, MongoDB Motor, connection pooling — async database patterns for FastAPI"
categories: [python-production]
series: python-production
module: 2
module_order: 203
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-async-database
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Synchronous database calls block the event loop. While one request waits for a database query, all other requests queue up. With async I/O, the event loop serves other requests while waiting for the database response.

## The Blueprint's In-Memory Store

Our blueprint uses an in-memory dict to keep things focused on the architecture patterns:

```python
_items: dict[str, ItemResponse] = {}
```

This is intentional — the blueprint teaches observability and deployment, not ORM configuration. But here's how you'd extend it.

## Pattern 1: SQLAlchemy Async (PostgreSQL)

### Setup

```python
# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/mydb",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Dependency Injection

```python
from fastapi import Depends

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/{item_id}")
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

FastAPI's `Depends()` injects the session — and ensures it's closed after the request.

### Connection Pooling

| Parameter | Value | Why |
|-----------|-------|-----|
| `pool_size` | 20 | Max persistent connections |
| `max_overflow` | 10 | Extra connections under burst load |
| `pool_pre_ping` | True | Test connection before using (detects stale connections) |

## Pattern 2: MongoDB Motor (Async)

```python
# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.myapp

async def get_db():
    return db

@router.post("/", status_code=201)
async def create_item(item: ItemCreate):
    doc = item.model_dump()
    result = await db.items.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return ItemResponse(**doc)
```

Motor is fully async-native — no thread pool hacks.

## Connection Lifecycle

Initialize in lifespan, close on shutdown:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create engine
    app.state.engine = create_async_engine(...)
    
    yield
    
    # Shutdown — dispose connections
    await app.state.engine.dispose()
```

## When to Use Which

| Database | Async Driver | Use Case |
|----------|-------------|----------|
| PostgreSQL | `asyncpg` | Relational data, transactions |
| MySQL | `aiomysql` | Legacy MySQL systems |
| MongoDB | `motor` | Document store, flexible schema |
| Redis | `redis.asyncio` | Cache, sessions, pub/sub |

## Next Step

In the next lesson, we cover API versioning strategies — URL-based, header-based, and backward compatibility patterns.
