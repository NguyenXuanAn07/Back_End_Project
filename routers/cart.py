#GIỎ HÀNG VÀ ĐẶT HÀNG
#cart.py xử lý 3 việc:
#1. Thêm sản phẩm vào giỏ
#2. Xem giỏ hàng
#3. Đặt hàng (checkout)

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import Session 
from jose import jwt, JWTError
from database import get_db
from models import User, Product, CartItem, Order, OrderItem
from schemas import CartItemCreate, OrderCreate
from fastapi.security import OAuth2PasswordBearer   #OAuth2PasswordBearer: công cụ lấy Token từ request, đưa cho def get_current_user kiểm tra
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")   #'tokenUrl="/auth/login"': chỉ định link đăng nhập để lấy token

#Lấy thông tin từ file .env
from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORRITHM")

#Tạo Router
router = APIRouter(prefix="/cart", tags=["cart"])

#Hàm kiểm tra token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #trong token sẽ có subject (chủ nhân của token), hàm này tách các phần ra
        email = payload.get("sub") #hàm này lấy được sub ra, tức email là chủ nhân của token
        if email is None:
            raise HTTPException(
                status_code=401,
                detail = "Token khong hop le"
                )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail= "Token khong hop le"
            )
    user = db.query(User).filter(User.email == user.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail = "Khong tim thay user!")
    return user

#API1-THÊM SẢN PHẨM VÀO GIỎ HÀNG
