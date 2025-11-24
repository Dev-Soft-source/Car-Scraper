from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database.config import get_db
from models.models import User, UserSettings
from utils.auth import verify_password, get_password_hash, create_access_token
from utils.dependencies import get_current_user

router = APIRouter(prefix='/auth', tags=['Authentication'])

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    email: str

@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    print("Register: ", user_data)
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default settings
    settings = UserSettings(user_id=new_user.id)
    db.add(settings)
    db.commit()
    
    return {'message': 'User registered successfully', 'email': new_user.email}

@router.post('/login', response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    # Create access token
    access_token = create_access_token(data={'sub': user.email})
    
    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'email': user.email
    }

@router.get('/me')
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        'id': current_user.id,
        'email': current_user.email,
        'created_at': current_user.created_at
    }
