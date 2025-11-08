from operator import index
from fastapi import APIRouter, HTTPException, status
from db.models.user import User
from db.client import db_client
from db.schemas.user import user_schema, users_schema
from bson import ObjectId



# Inicia el server: python -m uvicorn users:router --reload
router = APIRouter(prefix="/userdb",
                   tags=["user"],
                   responses={404: {"message": "No encontrado"}})

users_lista = []

## Rutas ###

@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

@router.get("/{id}")  # Path
async def user(id: str):
    return search_user("_id", ObjectId(id))


@router.get("/")  # Query
async def user(id: str):
    return search_user("_id", ObjectId(id))

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def user(user: User):
    if type(search_user("email", user.email)) == User:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")
    
    user_dict = dict(user)
    del user_dict["id"]
    id = db_client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": id}))
    return User(**new_user)
    
@router.put("/", response_model=User)
async def user(user: User):
    try:
        user_dict = dict(user)
        del user_dict["id"]
        db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}

    return search_user("_id", ObjectId(user.id))


@router.delete("/{id}")
async def user(id: str, status_code=status.HTTP_204_NO_CONTENT):
    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}
            

###________funciones_______    

def search_user(field: str, key):
    
    try:
        user = db_client.users.find_one({field: key})
        new_user =  User(**user_schema(user))
        return new_user
    except:
        return {"Error": "No se ha encontrado el usuario"}
    




