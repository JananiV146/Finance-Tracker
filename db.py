import os
import certifi
from typing import Any, Dict, List, Optional

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from bson import ObjectId


def _client() -> MongoClient:
    # Use Atlas connection string (replace <username> and <password>)
    uri = os.environ.get(
        "MONGODB_URI",
        "mongodb+srv://jananivenkatachalam14:jananivenkatachalam@userauthentication.iagkujk.mongodb.net/?retryWrites=true&w=majority&appName=userAuthentication"
    )
    # Add TLS certs for SSL handshake (only for Atlas connections).
    # Try a normal secure connection first; if that fails in development
    # attempt a fallback that allows invalid certs so the app can run.
    if "mongodb+srv" in uri or uri.startswith("mongodb+srv:"):
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
            # verify quickly
            client.admin.command("ping")
            return client
        except Exception as e:
            # Diagnostic output to help the developer debug TLS issues.
            print("Warning: secure connection to MongoDB Atlas failed:", str(e))
            # Development fallback: try allowing invalid certs (not for production).
            try:
                client = MongoClient(
                    uri,
                    tls=True,
                    tlsAllowInvalidCertificates=True,
                    serverSelectionTimeoutMS=5000,
                )
                client.admin.command("ping")
                print("Connected to MongoDB Atlas using tlsAllowInvalidCertificates=True (development fallback)")
                return client
            except Exception as e2:
                print("Fallback connection also failed:", str(e2))
                raise
    else:
        return MongoClient(uri, tls=False)


def _db():
    name = os.environ.get("MONGODB_DB", "finance_tracker")
    return _client()[name]


def ensure_indexes() -> None:
    db = _db()
    # Unique username
    db.users.create_index([("username", ASCENDING)], unique=True)
    # Transactions indexes
    db.transactions.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
    db.transactions.create_index([("user_id", ASCENDING), ("type", ASCENDING)])
    db.transactions.create_index([("user_id", ASCENDING), ("category", ASCENDING)])
    # Budgets unique per (user_id, month, category)
    db.budgets.create_index(
        [("user_id", ASCENDING), ("month", ASCENDING), ("category", ASCENDING)],
        unique=True,
    )


# ------------------ Users ------------------
def users_col() -> Collection:
    return _db().users


def create_user(username: str, password_hash: str) -> str:
    res = users_col().insert_one({"username": username, "password_hash": password_hash})
    return str(res.inserted_id)


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    u = users_col().find_one({"username": username})
    if not u:
        return None
    u["id"] = str(u["_id"])
    return u


def find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    u = users_col().find_one({"_id": oid}, {"username": 1})
    if not u:
        return None
    return {"id": str(u["_id"]), "username": u["username"]}


def update_user_password(user_id: str, password_hash: str) -> bool:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return False
    res = users_col().update_one(
        {"_id": oid}, {"$set": {"password_hash": password_hash}}
    )
    return res.matched_count > 0


# ------------------ Transactions ------------------
def tx_col() -> Collection:
    return _db().transactions


def list_transactions(user_id: str) -> List[Dict[str, Any]]:
    cur = tx_col().find({"user_id": user_id}).sort(
        [("date", DESCENDING), ("_id", DESCENDING)]
    )
    rows = []
    for d in cur:
        d["id"] = str(d["_id"])
        rows.append(d)
    return rows


def insert_transaction(
    user_id: str,
    date: str,
    ttype: str,
    amount: float,
    category: str,
    description: str = "",
) -> str:
    res = tx_col().insert_one(
        {
            "user_id": user_id,
            "date": date,  # YYYY-MM-DD
            "type": ttype,
            "amount": float(amount),
            "category": category,
            "description": description or "",
        }
    )
    return str(res.inserted_id)


def find_transaction(user_id: str, tx_id: str) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(tx_id)
    except Exception:
        return None
    d = tx_col().find_one({"_id": oid, "user_id": user_id})
    if not d:
        return None
    d["id"] = str(d["_id"])
    return d


def update_transaction(user_id: str, tx_id: str, fields: Dict[str, Any]) -> bool:
    try:
        oid = ObjectId(tx_id)
    except Exception:
        return False
    res = tx_col().update_one({"_id": oid, "user_id": user_id}, {"$set": fields})
    return res.matched_count > 0


def delete_transaction(user_id: str, tx_id: str) -> bool:
    try:
        oid = ObjectId(tx_id)
    except Exception:
        return False
    res = tx_col().delete_one({"_id": oid, "user_id": user_id})
    return res.deleted_count > 0


def totals(user_id: str) -> Dict[str, float]:
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$type", "total": {"$sum": "$amount"}}},
    ]
    inc = 0.0
    exp = 0.0
    for r in tx_col().aggregate(pipeline):
        if r["_id"] == "income":
            inc = float(r["total"])
        elif r["_id"] == "expense":
            exp = float(r["total"])
    return {"income": inc, "expense": exp}


def recent_transactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    cur = tx_col().find({"user_id": user_id}).sort(
        [("date", DESCENDING), ("_id", DESCENDING)]
    ).limit(limit)
    rows = []
    for d in cur:
        d["id"] = str(d["_id"])
        rows.append(d)
    return rows


def spend_by_category(user_id: str, month: str) -> Dict[str, float]:
    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "type": "expense",
                "date": {"$regex": f"^{month}"},  # YYYY-MM
            }
        },
        {"$group": {"_id": "$category", "spent": {"$sum": "$amount"}}},
    ]
    out: Dict[str, float] = {}
    for r in tx_col().aggregate(pipeline):
        out[r["_id"]] = float(r["spent"])
    return out


def month_income_expense(
    user_id: str, months: List[str]
) -> Dict[str, Dict[str, float]]:
    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "date": {"$regex": f"^({'|'.join(months)})"},
            }
        },
        {"$project": {"m": {"$substr": ["$date", 0, 7]}, "type": 1, "amount": 1}},
        {
            "$group": {
                "_id": {"m": "$m", "t": "$type"},
                "total": {"$sum": "$amount"},
            }
        },
    ]
    res: Dict[str, Dict[str, float]] = {m: {"income": 0.0, "expense": 0.0} for m in months}
    for r in tx_col().aggregate(pipeline):
        m = r["_id"]["m"]
        t = r["_id"]["t"]
        if m in res and t in res[m]:
            res[m][t] = float(r["total"])
    return res


# ------------------ Budgets ------------------
def budget_col() -> Collection:
    return _db().budgets


def list_budgets(user_id: str) -> List[Dict[str, Any]]:
    cur = budget_col().find({"user_id": user_id}).sort(
        [("month", DESCENDING), ("category", ASCENDING)]
    )
    rows: List[Dict[str, Any]] = []
    for b in cur:
        b["id"] = str(b["_id"])
        rows.append(b)
    return rows


def add_budget(
    user_id: str, month: str, amount: float, category: Optional[str]
) -> Optional[str]:
    try:
        res = budget_col().insert_one(
            {
                "user_id": user_id,
                "month": month,
                "category": category,
                "amount": float(amount),
            }
        )
        return str(res.inserted_id)
    except Exception:
        return None


def find_budget(user_id: str, bid: str) -> Optional[Dict[str, Any]]:
    try:
        oid = ObjectId(bid)
    except Exception:
        return None
    b = budget_col().find_one({"_id": oid, "user_id": user_id})
    if not b:
        return None
    b["id"] = str(b["_id"])
    return b


def update_budget(
    user_id: str, bid: str, month: str, amount: float, category: Optional[str]
) -> bool:
    try:
        oid = ObjectId(bid)
    except Exception:
        return False
    try:
        res = budget_col().update_one(
            {"_id": oid, "user_id": user_id},
            {"$set": {"month": month, "category": category, "amount": float(amount)}},
        )
        return res.matched_count > 0
    except Exception:
        return False


def delete_budget(user_id: str, bid: str) -> bool:
    try:
        oid = ObjectId(bid)
    except Exception:
        return False
    res = budget_col().delete_one({"_id": oid, "user_id": user_id})
    return res.deleted_count > 0


def budgets_for_month(user_id: str, month: str) -> List[Dict[str, Any]]:
    cur = budget_col().find({"user_id": user_id, "month": month}).sort(
        [("category", ASCENDING)]
    )
    rows = []
    for b in cur:
        rows.append({"category": b.get("category"), "amount": float(b.get("amount", 0))})
    return rows
