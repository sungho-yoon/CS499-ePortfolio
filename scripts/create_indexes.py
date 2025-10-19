import os
from dotenv import load_dotenv
from pymongo import MongoClient

def main():
    load_dotenv()
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "AAC")
    col_name = os.getenv("COLLECTION", "animals")

    client = MongoClient(uri)
    col = client[db_name][col_name]

    # Always have a stable sort key
    col.create_index([("_id", 1)])
    # Compound index aligned with filters
    col.create_index([
        ("animal_type", 1),
        ("sex_upon_outcome", 1),
        ("age_upon_outcome_in_weeks", 1),
        ("breed", 1),
    ])

    print("Indexes created ✓")

if __name__ == "__main__":
    main()