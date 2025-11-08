from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
## en la terminal de la pc python -c "import secrets; print(secrets.token_hex(32))
SECRET = "6ffc4b52dae6abbb6eb819da0ccac18d06f130834732f2aa22711f69372bbeac"

router = APIRouter(prefix="/jwtauth", 
                   tags=["jwt_auth_users"],
                   responses={404: {"message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

# --- Generación Dinámica del Hash ---
# Esto genera un hash nuevo y válido usando la configuración local de tu Passlib.


class User(BaseModel):
    username: str
    full_name :str
    email: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "johndoe": {"username":"johndoe", 
                "full_name":"John Doe", 
                "email":"jonhdoe@gmail.com", 
                "disabled":False,
                "password":"$2a$12$rQdmif6LYdil2egykPwoDuOUvUr5PzpWDetqxrGku0qmYGinLSoP6"
            },
    "alice": {"username":"alice", 
                "full_name":"Alice Wonderson", 
                "email":"alicewon@gmail.com", 
                "disabled":True,
                "password":"$2a$12$/f4.aGICgEsbEE9AC1Xlz.hSXtNnBvPbjnWRbAGvKwIReGLYun5h."
    }
}
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="credenciales de autenticación inválidas",
                headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception
    except JWTError:
        raise exception
    return search_user(username)
    
async def current_user(user: User = Depends(auth_user)):    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Usuario inactivo")
    
    return user
    
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):

    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    user = search_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseÃ±a no es correcta")

    access_token = {"sub": user.username,
                    "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user