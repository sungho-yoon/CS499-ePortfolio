# CRUD.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()  # load .env file from project root

class AnimalShelter:
    # CRUD operations for the AAC (Austin Animal Center) database

    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "AAC")
        self.col_name = os.getenv("COLLECTION", "animals")

        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self.database = self.client[self.db_name]
            self._collection = self.database[self.col_name]
            self.client.server_info()  # test connection
            print(f"Connected to MongoDB at {self.uri}")
        except errors.ServerSelectionTimeoutError as err:
            raise ConnectionError(f"MongoDB connection failed: {err}")

    @property
    def collection(self):
        """Read-only property exposing the MongoDB collection."""
        return self._collection

    # ---------- CREATE ----------
    def create(self, data: dict) -> dict:
        """Insert a new document into the collection."""
        if not isinstance(data, dict):
            raise TypeError("Data must be provided as a dictionary")
        try:
            result = self._collection.insert_one(data)
            return {"inserted_id": str(result.inserted_id), "status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- READ ----------
    def read(self, query: dict = None, projection: dict = None, page: int = 1, page_size: int = 25) -> dict:
        """Read documents from the collection with pagination and projection."""
        query = query or {}
        skip = (page - 1) * page_size
        try:
            docs = list(
                self._collection.find(query, projection)
                .skip(skip)
                .limit(page_size)
            )
            total = self._collection.count_documents(query)
            for d in docs:
                d["_id"] = str(d["_id"])
            return {"count": len(docs), "total": total, "page": page, "data": docs}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- UPDATE ----------
    def update(self, filter_doc: dict, new_values: dict) -> dict:
        """Update existing documents based on filter criteria."""
        if not isinstance(filter_doc, dict) or not isinstance(new_values, dict):
            raise TypeError("filter_doc and new_values must be dictionaries")
        try:
            res = self._collection.update_many(filter_doc, {"$set": new_values})
            from app.services.animals import invalidate_caches
            invalidate_caches()  # clear cache after data change
            return {
                "matched": res.matched_count,
                "modified": res.modified_count,
                "acknowledged": res.acknowledged,
                "status": "success"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- DELETE ----------
    def delete(self, filter_doc: dict) -> dict:
        """Delete documents matching the filter."""
        if not isinstance(filter_doc, dict):
            raise TypeError("Filter must be a dictionary")
        try:
            res = self._collection.delete_many(filter_doc)
            from app.services.animals import invalidate_caches
            invalidate_caches()
            return {"deleted_count": res.deleted_count, "status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ---------- UTILITY ----------
    def ping(self) -> bool:
        """Verify connectivity to the database."""
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False