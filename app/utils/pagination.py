from typing import Optional, Tuple
from bson import ObjectId

def keyset_query(base_query: dict, last_id: Optional[str]):
    q = dict(base_query)
    if last_id:
        q["_id"] = {"$gt": ObjectId(last_id)}
    return q