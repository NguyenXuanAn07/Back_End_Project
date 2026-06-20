#Kết nối tới database bằng create_engine
#Tạo khuôn session bằng sessionmaker để mở/đóng phiên làm việc
#Tạo Base — bản mẫu gốc để các bảng kế thừa


from sqlalchemy import create_engine #create_engine là cầu nối
from sqlalchemy.ext.declarative import declarative_base #declarative_base giúp mô tả bảng database bằng code python
from sqlalchemy.orm import sessionmaker 
from dotenv import load_dotenv
import os #os là thư viện giúp python tương tác với hệ điều hành

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") #lấy địa chỉ database từ file .env lưu vào biến 'DATABASE_URL'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #ssmker tạo ra khuôn làm việc, autocommit không tự động lưu thay đổi vào DB, autoflush không tự đồng bộ trước mỗi truy vấn
Base = declarative_base() #tạo lớp nền để các bảng kế thừa, VD: class User(Base) -> tạo bảng Users

def get_db():
    db = SessionLocal() 
    try:
        yield db # yield đưa db cho ai cần dùng
    finally:
        db.close()
