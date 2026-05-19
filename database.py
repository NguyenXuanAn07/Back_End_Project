#Kết nối tới database bằng create_engine
#Tạo khuôn session bằng sessionmaker để mở/đóng phiên làm việc
#Tạo Base — bản mẫu gốc để các bảng kế thừa


from sqlalchemy import create_engine #sqlalchemy thư viện giúp py nói chuyện vs psql, create_engine là cầu nối
from sqlalchemy.ext.declarative import declarative_base #declarative_base giúp mô tả bảng database bằng code python
from sqlalchemy.orm import sessionmaker #sessionmaker tạo ra các phiên làm việc với database
from dotenv import load_dotenv #dotenv giúp python đọc file .env
import os #os là thư viện giúp python tương tác với hệ điều hành

load_dotenv() #đây là lúc thực sự đọc vào file .env

DATABASE_URL = os.getenv("DATABASE_URL") #lấy địa chỉ database từ file .env lưu vào biến 'DATABASE_URL'

engine = create_engine(DATABASE_URL) #nối từ python đến postgresql
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #ssmker tạo ra khuôn làm việc, autocommit không tự động lưu thay đổi vào DB, autoflush không tự đồng bộ trước mỗi truy vấn
Base = declarative_base() #tạo lớp nền để các bảng kế thừa, VD: class User(Base) -> tạo bảng Users

def get_db():
    db = SessionLocal() #mở một phiên làm việc với database
    try:
        yield db # yield đưa db cho ai cần dùng
    finally:
        db.close() #đóng database lại cho dù kết quả thế nào ở bước cuối cùng
