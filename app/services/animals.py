import os
from typing import Dict, Any, List, Optional, Tuple
from bson import ObjectId
from CRUD import AnimalShelter  
from app.utils.security import whitelist_filters
from app.utils.pagination import keyset_query
from app.utils.cache import make_signature, lru128

# Expect env vars like MONGO_URI, DB_NAME, COLLECTION (fallbacks kept for dev)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "AAC")
COLLECTION = os.getenv("COLLECTION", "animals")

# Initialize one shared AnimalShelter instance
shelter = AnimalShelter()

PROJECTION = {
    "_id": 1,
    "animal_type": 1,
    "breed": 1,
    "sex_upon_outcome": 1,
    "age_upon_outcome_in_weeks": 1,
}

DEFAULT_PAGE_SIZE = 25


def build_query(species: Optional[list], sex: Optional[list], age_range: Optional[list]) -> Dict[str, Any]:
    q = {}
    if species:
        q["animal_type"] = {"$in": species}
    if sex:
        q["sex_upon_outcome"] = {"$in": sex}
    if age_range and len(age_range) == 2:
        q["age_upon_outcome_in_weeks"] = {"$gte": int(age_range[0]), "$lte": int(age_range[1])}
    return whitelist_filters(q)


def fetch_page(filters: Dict[str, Any], last_id: Optional[str], page_size: int = DEFAULT_PAGE_SIZE) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    q = keyset_query(filters, last_id)
    # Use your CRUD.read; if it doesn’t accept projection/sort, we’ll add a helper below
    docs = list(shelter.collection.find(q, PROJECTION).sort([("_id", 1)]).limit(page_size))
    next_last_id = str(docs[-1]["_id"]) if docs else None
    # Format for UI (convert ObjectId)
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs, next_last_id

# ---------- Cached aggregations ----------
@lru128
def _top_breeds_cached(sig):
    filters, limit = sig  # unpack normalized signature
    pipeline = [
        {"$match": filters},
        {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    return list(shelter.collection.aggregate(pipeline))

def top_breeds(filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    sig = make_signature(filters, ("limit", limit))
    return _top_breeds_cached(sig)

@lru128
def _age_histogram_cached(sig):
    filters, step, max_weeks = sig
    # bucket by age in 'step' week increments (e.g., 26 = half-year)
    pipeline = [
        {"$match": filters},
        {"$bucket": {
            "groupBy": "$age_upon_outcome_in_weeks",
            "boundaries": list(range(0, int(max_weeks) + step, step)),
            "default": "≥{}".format(max_weeks),
            "output": {"count": {"$sum": 1}}
        }},
        {"$project": {"bucket": "$_id", "count": 1, "_id": 0}},
        {"$sort": {"bucket": 1}}
    ]
    return list(shelter.collection.aggregate(pipeline))

def age_histogram(filters: Dict[str, Any], step: int = 26, max_weeks: int = 520) -> List[Dict[str, Any]]:
    sig = make_signature(filters, ("step", step), ("max", max_weeks))
    return _age_histogram_cached(sig)

def invalidate_caches():
    # call this after any CRUD write that would affect aggregations
    _top_breeds_cached.cache_clear()
    _age_histogram_cached.cache_clear()

def top_breeds(filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    pipeline = [
        {"$match": filters},
        {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    return list(shelter.collection.aggregate(pipeline))