# vodex-evaluation

This project implements CRUD (Create, Read, Update, Delete) APIs for managing Items and User Clock-In Records using FastAPI and MongoDB. It also includes filtering and aggregation features.

## Prerequisites

- Python (version 3.x recommended)
- MangoDB (You can use MongoDB Atlas or a local instance)
- pipenv (for virtual environment management)

## Setup Instructions

### 1. Clone the repository

First, you need to clone the repository to your local machine. You can do this using the following command:

```bash
git clone https://github.com/girishc24/vodex-evaluation.git
cd vodex-evaluation
```
### 2. Create a virtual environment

Create a virtual environment to install the project dependencies. This helps in maintaining project-specific dependencies and avoiding conflicts with other projects.

- For Linux/Mac:
```
python -m venv venv
source venv/bin/activate
```
- For Windows:
```
python -m venv venv
venv\Scripts\activate
```
### 3. Install dependencies

With the virtual environment activated, install the required dependencies using the requirements.txt file:
```
pip install -r requirements.txt
```
### 4. Set up MongoDB

You can either set up a local MongoDB instance or use MongoDB Atlas (cloud-hosted MongoDB).

Ensure the connection string is correct in the application. You can configure it in a .env file like this:

```
# .env file
MONGO_DETAILS=mongodb+srv://<username>:<password>@cluster0.mongodb.net/mydatabase?retryWrites=true&w=majority
```
### 5. Configure Environment Variables

Create a .env file in the project root with the following variables:

```
MONGO_DETAILS=<your-mongodb-uri>
```

### 6. Run the Application

To start the FastAPI server locally, run:
```
uvicorn main:app --reload
```
The application will be accessible at: http://127.0.0.1:8000/

## API Documentation

FastAPI provides automatic interactive API documentation.

- Swagger UI: Visit http://127.0.0.1:8000/docs to explore the API documentation and test the endpoints interactively.
- Redoc: Visit http://127.0.0.1:8000/redoc for alternative documentation.

## API Endpoints Documentation

Items API

1. Create a New Item
- Endpoint: POST /items
- Description: Create a new item.
- Request Body:
```
{
  "name": "John Doe",
  "email": "johndoe@gmail.com",
  "item_name": "Laptop",
  "quantity": 5,
  "expiry_date": "2024-12-31"
}
```
### Response:
- Status: 201 Created
- Body :
```
{
  "item": {
    "_id": "6709ebc3931f68477ce8096d",
    "name": "John Doe",
    "email": "johndoe@example.com",
    "item_name": "Laptop",
    "quantity": 5,
    "expiry_date": "2024-12-31",
    "insert_date": "2024-10-12T03:23:47.340000"
  }
}
```
2. Get an Item by ID
- Endpoint: GET /items/{id}
- Description: Retrieve an item by its ID.
- Response:
  - Status: 200 OK
  - Body:
```
    {
    "id": "64f9b7c8f1b2b541f87ef912",
    "name": "John Doe",
    "email": "johndoe@example.com",
    "item_name": "Laptop",
    "quantity": 5,
    "expiry_date": "2024-12-31",
    "insert_date": "2024-10-11T12:45:30.000Z"
    }
```

- Error Response:
- Status: 404 Not Found
- Body:

```
{
  "detail": "Item not found"
}
```