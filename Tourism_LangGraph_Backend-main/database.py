import pymongo
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

try:
    client = MongoClient("mongodb://localhost:27017")
    db = client["TripPlannerDB"]
    vendors_collection = db["vendors"]
    print("Successfully connected to MongoDB")
except pymongo.errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB:{e}")
    exit()


def add_vendors(vendor_data: dict) -> str:
    vendor_data["registration_date"] = datetime.now()
    vendor_data["last_updated"] = datetime.now()

    result = vendors_collection.insert_one(vendor_data)
    print(f"Added new vendor with ID: {result.inserted_id}")
    return str(result.inserted_id)


def find_vendor_by_id(vendor_id: str) -> dict:
    try:
        return vendors_collection.find_one({"_id": ObjectId(vendor_id)})
    except Exception as e:
        print(f"Error finding vendor: {e}")
        return None


def find_vendor_by_type(vendor_type: str) -> list:
    vendors = vendors_collection.find({"vendor_type": vendor_type})
    return list(vendors)


def find_all_vendors() -> list:
    vendors = vendors_collection.find({})
    return list(vendors)


def find_vendors_by_city_and_type(vendor_type: str, city: str) -> list:
    """
    Finds all vendors of a specific type in a specific city, regardless of status.
    """
    query = {
        "vendor_type": vendor_type,
        # Case-insensitive match for the city
        "city": {"$regex": f"^{city.strip()}$", "$options": "i"},
    }
    vendors = vendors_collection.find(query)
    return list(vendors)