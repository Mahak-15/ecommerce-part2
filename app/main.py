from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
import os
import random
import secrets
import sqlite3

from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .database import get_connection, initialise_database

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialise_database()
    yield

app = FastAPI(
    title="FORMA Store API",
    description="FORMA product catalogue, visitor analytics, and admin tools.",
    version="2.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/admin/", include_in_schema=False)
def admin_home():
    return FileResponse(STATIC_DIR / "admin" / "index.html")

@app.get("/admin/css-generator", include_in_schema=False)
def css_generator_home():
    return FileResponse(STATIC_DIR / "admin" / "css-generator.html")

@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok", "service": "FORMA Store API"}

@app.get("/api/categories", tags=["Products"])
def get_categories():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT DISTINCT category FROM products ORDER BY category"
        ).fetchall()
    return [row["category"] for row in rows]

@app.get("/api/products", tags=["Products"])
def get_products(
    q: Optional[str] = Query(default=None, max_length=100),
    category: Optional[str] = Query(default=None, max_length=50),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="id", pattern="^(id|name|price)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot be greater than max_price")
    conditions, parameters = [], []
    if q and q.strip():
        conditions.append("(name LIKE ? OR description LIKE ?)")
        term = f"%{q.strip()}%"
        parameters.extend([term, term])
    if category and category.strip():
        conditions.append("category = ?")
        parameters.append(category.strip())
    if min_price is not None:
        conditions.append("price >= ?")
        parameters.append(min_price)
    if max_price is not None:
        conditions.append("price <= ?")
        parameters.append(max_price)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM products" + where, parameters).fetchone()[0]
        rows = connection.execute(
            f"""SELECT id,name,description,price,image_url,category,stock
                FROM products {where}
                ORDER BY {sort_by} {order.upper()} LIMIT ? OFFSET ?""",
            [*parameters, limit, offset]
        ).fetchall()
    return {"items":[dict(row) for row in rows],"total":total,"limit":limit,
            "offset":offset,"sort_by":sort_by,"order":order}

@app.get("/api/products/{product_id}", tags=["Products"])
def get_product(product_id: int):
    if product_id < 1:
        raise HTTPException(status_code=422, detail="Product ID must be positive")
    with get_connection() as connection:
        product = connection.execute(
            """SELECT id,name,description,price,image_url,category,stock
               FROM products WHERE id=?""", (product_id,)
        ).fetchone()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(product)

# Local educational demo only: these are TEST-NET documentation addresses.
IP_COUNTRIES = [
    ("203.0.113.10", "Australia"),
    ("198.51.100.20", "India"),
    ("192.0.2.30", "United States"),
    ("203.0.113.40", "United Kingdom"),
    ("198.51.100.50", "Germany"),
]
SIMULATED_PATHS = ["/", "/api/products", "/api/categories"]

def require_admin(authorization: Optional[str] = Header(default=None)):
    expected = os.getenv("FORMA_ADMIN_TOKEN", "forma-admin-local")
    supplied = authorization or ""
    if not secrets.compare_digest(supplied, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Admin token missing or incorrect")

class SimulationRequest(BaseModel):
    count: int = Field(default=25, ge=1, le=500)

@app.post("/api/admin/analytics/simulate", tags=["Admin"], dependencies=[Depends(require_admin)])
def simulate_visits(payload: SimulationRequest):
    rows = []
    for _ in range(payload.count):
        ip, country = random.choice(IP_COUNTRIES)
        rows.append((ip, country, random.choice(SIMULATED_PATHS),
                     "FORMA analytics simulator", 1))
    with get_connection() as connection:
        connection.executemany(
            """INSERT INTO analytics_events
               (ip_address,country,request_path,user_agent,is_simulated)
               VALUES (?,?,?,?,?)""", rows
        )
    return {"inserted": len(rows), "message": "Simulated analytics events saved."}

@app.get("/api/admin/analytics/summary", tags=["Admin"], dependencies=[Depends(require_admin)])
def analytics_summary():
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM analytics_events").fetchone()[0]
        unique_ips = connection.execute("SELECT COUNT(DISTINCT ip_address) FROM analytics_events").fetchone()[0]
        simulated = connection.execute("SELECT COUNT(*) FROM analytics_events WHERE is_simulated=1").fetchone()[0]
        countries = connection.execute(
            """SELECT country,COUNT(*) AS visits FROM analytics_events
               GROUP BY country ORDER BY visits DESC,country ASC"""
        ).fetchall()
        daily = connection.execute(
            """SELECT date(created_at) AS day,COUNT(*) AS visits FROM analytics_events
               GROUP BY date(created_at) ORDER BY day DESC LIMIT 7"""
        ).fetchall()
    return {"total_visits":total,"unique_ips":unique_ips,"simulated_visits":simulated,
            "countries":[dict(r) for r in countries],"daily":[dict(r) for r in reversed(daily)]}

@app.get("/api/admin/analytics/events", tags=["Admin"], dependencies=[Depends(require_admin)])
def analytics_events(limit: int = Query(default=50, ge=1, le=200),
                     offset: int = Query(default=0, ge=0)):
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT id,ip_address,country,request_path,user_agent,is_simulated,created_at
               FROM analytics_events ORDER BY id DESC LIMIT ? OFFSET ?""",
            (limit,offset)
        ).fetchall()
    return {"items":[dict(r) for r in rows],"limit":limit,"offset":offset}

@app.delete("/api/admin/analytics", tags=["Admin"], dependencies=[Depends(require_admin)])
def clear_analytics():
    with get_connection() as connection:
        connection.execute("DELETE FROM analytics_events")
    return {"deleted":True}
