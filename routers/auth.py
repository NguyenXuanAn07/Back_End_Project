#File routers/auth.File routers/auth.py — Đăng ký & Đăng nhập
#auth.py xử lý 2 việc:
#1. Đăng ký  → nhận thông tin → lưu vào database
#2. Đăng nhập → kiểm tra thông tin → cấp Token

#import từ FastAPI
from fastapi import APIRouter,  Depends, HTTPException, status #apirouters: tạo nhóm api riêng, depend: khai báo phụ thuộc (cần db)
                                                               #HTTPEXCEPTION: báo lỗi cho fe, status: các mã http chuẩn
from sqlalchemy.orm import Session #session là kiểu dữ liệu của phiên làm việc với database
from datetime import datetime, timedelta
from jose import JWTError, jwt #jwt: công cụ tạo và đọc token, jwterror: lỗi xảy ra khi token không hợp lệ
from passlib.context import CryptContext #cryptcontext: công cụ mã hóa và kiểm trả password           
from database import get_db #đef dang_ky(db = Depends(get_db))        
from models import User #1. Tìm user trong database: db.query(User).filter(User.email == email)
                        #2. Tạo user mới: new_user = User(Email=..., password_hash=....,...)
from schemas import UserCreate, UserOut, Token #Mang các def từ file khác sang đây để khi tạo lệnh file này có thể hiểu được

#Cấu hình mã hóa password
pwd_context = CryptContext(schemes=["bcrypt"], deprecapted="auto") #CrypContext tạo công cụ mã hóa
                                                                   #schemes=["bcrypt"]: "bcypt" là thuật toán mã hóa phổ biến nhất
                                                                   #deprecapted="auto": nếu sau này 'bcrypt' có phiên bản mới hơn thì sẽ tự động xử lí phiên bản cũ

#LẤY THÔNG TIN TỪ FILE .env
from dotenv import load_dotenv   #dotenv giúp python đọc file .env
import os   #os là thư viện giúp python tương tác với hệ điều hành
load_dotenv()   #đây là lúc thực sự đọc vào file .env

SECRET_KEY =os.getenv("SECRET_KET")   #lấy chìa khóa bí mật để ký token
ALGORITHM = os.getenv("ALGORITHM")   #lấy thuật toán tạo token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))   #lấy thời gian hết hạn token

#Tạo router
router = APIRouter(prefix="/auth", tags=["auth"]) #APIRouter: tạo nhóm API cho riêng ath
                                                  #prefix="/auth": tất cả các APi trong file này đều bắt đầu bằng '/auth', VD; /auth/login,..
                                                  #tags=["auth"]: nhóm API này hiển thị trong dóc với tên 'auth'

#Hàm mã hóa password
def hash_password(password: str) ->str:   #nhận vào 1 password dạng chuỗi, -> str: trả về 1 chuỗi(chuỗi hash)
    return pwd_context.hash(password)    #dùng pwd_context để mã hóa (dùng "máy xay")
                                         #VD: hash_password("123456") -> "hdshfhiu43812Z^&"

#Hàm kiểm tra password
def verify_password(plain_password: str, hashed_password: str) -> bool:   #plain: pass vừa nhập, hashed: đã lưu trong db
    return pwd_context.verify(plain_password, hashed_password)   #so sánh 2 pass, bool trả về true/false

#Hàm tạo token
def create_access_token(data: dict) -> str:   #'data: dict' : thông tin muốn nhét vào token
    to_encode = data.copy()   #sao chép data, không làm thay đổi bản gốc
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #tính tgian hêt hạn
    to_encode.update({"exp": expire})   #thêm tgia hết hạn vào token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   #jwt đóng gói tất cả thành 1 token

#API đăng ký
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED) 
   #@router.post: API này nhận request loại POST, "/register": đường dẫn
   #response_model=UserOut: dữ liệu trả về theo khuôn UserOut (không có password)
   #status_code=201: trả về mã 201=tạo mới thành công
def register(user: UserCreate, db: Session = Depends(get_db)):   #"user: UserCreate": nhận dữ liệu từ FE, "db: session": phiên làm việc vopwis db
                                                                 #"depends":FastAPI tự động mở session cho mình

