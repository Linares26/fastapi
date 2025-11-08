from operator import index
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Inicia el server: python -m uvicorn users:router --reload

#entidad user
class User(BaseModel):
    id: int
    name :str
    surname: str
    url: str
    age: int

users_lista = [User(id=1, name="Brais", surname="moure", url="https://moure.dev", age=35),
               User(id=2, name= "Moure", surname="dev", url="https://mouredev.com", age=35),
               User(id=3, name= "Haakon", surname="dahlberg", url="https://haakon.com", age=33)]

router = APIRouter(tags=["user"],
                   responses={404: {"message": "No encontrado"}})

## Rutas ###
@router.get("/usersjson")
async def usersjson():
    return [{"name":"Brais", "surname": "moure", "url": "https://moure.dev", "age": 35},
            {"name":"Moure", "surname": "dev", "url": "https://mouredev.com", "age": 35},
            {"name":"Haakon", "surname": "dahlberg", "url": "https://haakon.com", "age": 33}]

@router.get("/users")
async def users():
    return users_lista

###__path__
@router.get("/user/{id}")
async def user(id: int):
    return search_user(id)
    
###___query___    
@router.get("/user")
async def user(id: int):
    return search_user(id)

@router.post("/user", response_model=User, status_code=201)
async def user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=404, detail="El usuario ya existe")
    users_lista.append(user)
    return user
    
@router.put("/user")
async def user(user: User):
    found = False
    for index, saved_user in enumerate(users_lista):
        if saved_user.id == user.id:
            users_lista[index] = user
            found = True
    if not found:
        return {"error": "No se ha actualizado el usuario"}

    return user


@router.delete("/user/{id}")
async def user(id: int):
    found = False
    for index, saved_user in enumerate(users_lista):
        if saved_user.id == id:
            del users_lista[index]
            found = True
            return {"msg": "Usuario eliminado"}
    if not found:
        return {"error": "No se ha eliminado el usuario"}
            

###________funciones_______    

def search_user(id: int):
    users = list(filter(lambda user: user.id == id, users_lista))
    try:
        return list (users)[0]
    except:
        return None



