from fastapi import FastAPI, HTTPException, Depends
from database import items_collection, clockin_collection, database
from models import ItemCreate, ItemUpdate, ClockInCreate, ClockInUpdate
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date
import logging
from typing import Optional
from fastapi import Query

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.get("/")
def read_root(): 
    return {"Hello": "World"}

# Create a new item
@app.post("/items", response_description="Create an Item")
async def create_item(item: ItemCreate):
    item_dict = item.dict()
    item_dict['expiry_date'] = item.expiry_date.strftime('%Y-%m-%d')
    item_dict['insert_date'] = datetime.utcnow() 
    result = await items_collection.insert_one(item_dict)

    inserted_item = await items_collection.find_one({"_id": result.inserted_id})
    inserted_item['_id'] = str(inserted_item['_id'])

    return {"item": inserted_item}



# Filter items
@app.get("/items/filter", response_description="Filter Items")
async def filter_items(
    email: Optional[str] = Query(None, description="Email to filter by"),
    expiry_date: Optional[str] = Query(None, description="Filter items expiring after this date (YYYY-MM-DD)"),
    insert_date: Optional[str] = Query(None, description="Filter items inserted after this date (YYYY-MM-DD)"),
    quantity_gte: Optional[int] = Query(None, description="Filter items with quantity greater than or equal to this value")
):
    try:
        filter_query = {}
        
        if email:
            filter_query["email"] = email
        
        if expiry_date:
            try:
                expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                filter_query["expiry_date"] = {"$gte": expiry_date_obj.strftime('%Y-%m-%d')}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid expiry date format. Use YYYY-MM-DD")
        
        if insert_date:
            try:
                insert_date_obj = datetime.strptime(insert_date, '%Y-%m-%d').date()
                filter_query["insert_date"] = {
                    "$gte": datetime.combine(insert_date_obj, datetime.min.time())
                }
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid insert date format. Use YYYY-MM-DD")
        
        if quantity_gte is not None:
            filter_query["quantity"] = {"$gte": quantity_gte}

        # Print the filter query for debugging
        print(f"Filter query: {filter_query}")
        
        items = []
        cursor = items_collection.find(filter_query)
        
        async for document in cursor:
            document['_id'] = str(document['_id'])
            items.append(document)
        
        return {"items": items, "count": len(items)}
    
    except Exception as e:
        print(f"Error in filter_items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Aggregation: Count items per email
@app.get("/items/aggregation", response_description="Aggregate Items by Email")
async def aggregate_items():
    pipeline = [
        {"$group": {"_id": "$email", "count": {"$sum": 1}}}
    ]
    result = await items_collection.aggregate(pipeline).to_list(100)
    return result

# Get item by ID
@app.get("/items/{id}", response_description="Get an Item by ID")
async def get_item(id: str):
    try:
        object_id = ObjectId(id)  # Try to convert the string to an ObjectId
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format. Must be a 24-character hex string.")
    
    item = await items_collection.find_one({"_id": object_id})
    if item:
        item['_id'] = str(item['_id'])  
        return item

    raise HTTPException(status_code=404, detail="Item not found")


    
# Update item by ID
@app.put("/items/{id}", response_description="Update an Item by ID")
async def update_item(id: str, item: ItemUpdate):
    try:
        item_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    existing_item = await items_collection.find_one({"_id": item_id})
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = {k: v for k, v in item.dict().items() if v is not None}
    if 'expiry_date' in updated_item:
        updated_item['expiry_date'] = updated_item['expiry_date'].strftime('%Y-%m-%d')

    result = await items_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_item})

    if result.modified_count == 1:
        updated_item_data = await items_collection.find_one({"_id": ObjectId(id)})
        if updated_item_data:
            updated_item_data['_id'] = str(updated_item_data['_id'])  
            return {"message": "Item updated successfully", "data": updated_item_data}
    raise HTTPException(status_code=404, detail="Item not found")

# Delete item by ID
@app.delete("/items/{id}", response_description="Delete an Item by ID")
async def delete_item(id: str):
    result = await items_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")



# Create a new clock-in record
@app.post("/clock-in", response_description="Create a Clock-In Record")
async def create_clock_in(clock_in: ClockInCreate):
    clock_in_dict = clock_in.dict()
    clock_in_dict['insert_datetime'] = datetime.utcnow()  # Auto-insert current datetime
    result = await clockin_collection.insert_one(clock_in_dict)

    inserted_item = await clockin_collection.find_one({"_id": result.inserted_id})
    inserted_item['_id'] = str(inserted_item['_id'])

    return {"clock": inserted_item}
    

# Filter clock-in records
@app.get("/clock-in/filter", response_description="Filter Clock-In Records")
async def filter_clock_in(email: Optional[str] = None, location: Optional[str] = None, insert_datetime: Optional[datetime] = None):
    query = {}
    if email:
        query['email'] = email
    if location:
        query['location'] = location
    if insert_datetime:
        query['insert_datetime'] = {"$gt": insert_datetime}

    records = await clockin_collection.find(query).to_list(100)
    
    # Convert ObjectId to string for each record
    for record in records:
        if '_id' in record:
            record['_id'] = str(record['_id'])
    
    return records


# Get clock-in record by ID
@app.get("/clock-in/{id}", response_description="Get Clock-In Record by ID")
async def get_clock_in(id: str):
    record = await clockin_collection.find_one({"_id": ObjectId(id)})
    if record:
        # Convert ObjectId to string for JSON serialization
        record['_id'] = str(record['_id'])
        return record
    raise HTTPException(status_code=404, detail="Record not found")


# Update clock-in record by ID
@app.put("/clock-in/{id}", response_description="Update a Clock-In Record by ID")
async def update_clock_in(id: str, clock_in: ClockInUpdate):
    updated_clock_in = {k: v for k, v in clock_in.dict().items() if v is not None}
    result = await clockin_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_clock_in})
    if result.modified_count == 1:
        return {"message": "Clock-In Record updated successfully"}
    raise HTTPException(status_code=404, detail="Record not found")



# Delete clock-in record by ID
@app.delete("/clock-in/{id}", response_description="Delete a Clock-In Record by ID")
async def delete_clock_in(id: str):
    result = await clockin_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Clock-In Record deleted successfully"}
    raise HTTPException(status_code=404, detail="Record not found")


# DB Connection
@app.get("/test-db", response_description="Test Database Connection")
async def test_db():
    try:
        # Try to fetch one document
        doc = await items_collection.find_one()
        if doc:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        return {
            "status": "connected",
            "database": "vodex",
            "collection": "items",
            "sample_doc": doc
        }
    except Exception as e:
        return {
            "status": "error",
            "details": str(e)
        }