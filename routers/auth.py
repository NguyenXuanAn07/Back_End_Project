#File routers/auth.File routers/auth.py — Đăng ký & Đăng nhập
#auth.py xử lý 2 việc:
#1. Đăng ký  → nhận thông tin → lưu vào database
#2. Đăng nhập → kiểm tra thông tin → cấp Token

#import từ FastAPI
from fastapi import APIRouter,  Depends, HTTPException, status #apirouters: tạo nhóm api riêng, depend: khai báo phụ thuộc (cần db)
                                                               #HTTPEXCEPTION: báo lỗi cho fe, status: các mã http chuẩn
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt #jwt: công cụ tạo và đọc token, jwterror: lỗi xảy ra khi token không hợp lệ
from passlib.context import CryptContext #cryptcontext: công cụ mã hóa và kiểm trả password           
from database import get_db #đef dang_ky(db = Depends(get_db))        
from models import User
from schemas import UserCreate, UserOut, Token #Mang các def từ file khác sang đây để khi tạo lệnh file này có thể hiểu được

#Cấu hình mã hóa password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #CrypContext tạo công cụ mã hóa
                                                                   #schemes=["bcrypt"]: "bcypt" là thuật toán mã hóa phổ biến nhất
                                                                   #deprecapted="auto": nếu sau này 'bcrypt' có phiên bản mới hơn thì sẽ tự động xử lí phiên bản cũ

#LẤY THÔNG TIN TỪ FILE .env
from dotenv import load_dotenv 
import os   
load_dotenv() 

SECRET_KEY =os.getenv("SECRET_KEY")  
ALGORITHM = os.getenv("ALGORITHM")  
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#Tạo router
router = APIRouter(prefix="/auth", tags=["auth"]) #APIRouter: tạo nhóm API cho riêng ath
                                                  #prefix="/auth": tất cả các APi trong file này đều bắt đầu bằng '/auth', VD; /auth/login,..
                                                  #tags=["auth"]: nhóm API này hiển thị trong dóc với tên 'auth'

#Hàm mã hóa password
def hash_password(password: str) ->str: 
    return pwd_context.hash(password)  

#Hàm kiểm tra password
def verify_password(plain_password: str, hashed_password: str) -> bool:   #plain: pass vừa nhập, hashed: đã lưu trong db
    return pwd_context.verify(plain_password, hashed_password)   #so sánh 2 pass, bool trả về true/false

#Hàm tạo token
def create_access_token(data: dict) -> str:   #'data: dict' : thông tin muốn nhét vào token
    to_encode = data.copy()   #sao chép data, không làm thay đổi bản gốc
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #tính tgian hêt hạn
    to_encode.update({"exp": expire})   #thêm tgia hết hạn vào token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   #jwt đóng gói tất cả thành 1 token

#API ĐĂNG KÝ
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED) 
def register(user: UserCreate, db: Session = Depends(get_db)): 
    print(f"Email: {user.email}")                                                                
    existing_user = db.query(User).filter(User.email == user.email).first() #"db.query(User)": hỏi db cho xem bảng User, "filter(User.mail == user.mail)": lọc ra mail trùng khớp, ".first()": đưa ra kết quả đầu tiên (none nếu không có)
    if existing_user:   #Nếu tìm thấy user
        raise HTTPException(   
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "Email was avaiable!"   
        )
    #Mã hóa password
    hashed = hash_password(user.password)

    #Tạo user mới
    new_user = User(
        email = user.email,
        password_hash = hashed,
        full_name = user.full_name,
        phone = user.phone,
        address = user.address
    )
    #Lưu thông tin user mới vào db
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    #Trả về thông tin user: UserOut
    return new_user

#API ĐĂNG NHẬP
@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Email is not avaiable!"
        )
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Wrong password!"
        )
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}