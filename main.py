#main.py = người điều phối
# → Gọi database.py để kết nối DB
# → Gọi routers/auth.py để xử lý đăng nhập
# → Gọi routers/cart.py để xử lý giỏ hàng
# → Mở cửa đón request từ frontend

#NỐI AUTH SANG MAIN.PY
from routers import auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware #middleware kiểm tra/xử lý request, response trước khi đưa vào server
                                                   #nếu không có cors, FE không thể request cho BE vì hoạt động ở 2 địa chỉ khác nhau và sẽ báo lỗi
from database import engine, Base #engine cầu nối tới PgSQl, Base là bản mẫu gốc của các bảng
from models import User, Product, CartItem, Order, OrderItem #lấy từ model.py các bảng đã viết

app = FastAPI() #TẠO API CỦA MÌNH, từ đấy, mọi thứ đều thông qua app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      #cho phép mọi nguồn gọi vào
    allow_credentials=True,  #cho phép gửi kèm token/cookie
    allow_methods=["*"],     #cho phép mọi loại request (GET, POST, PUT, DELETE,...)
    allow_headers=["*"],     #cho phép mọi loại header
)

app.include_router(auth.router)  #gắn tất cả API trong auth vào server, giống như lắp 1 phòng vào 1 tòa nhà

#Tạo bảng tự động
Base.metadata.create_all(bind=engine) #base có các bảng users,...; metadata chứa toàn bộ thông tin đó
                                      #create_all nhìn vào model.py tạo các bảng chưa có trong database
                                      #bind=engine tạo bảng vào đúng database mình đã kết nối

@app.get("/")   # @:gắn thêm tính năng vào hàm bên dưới, app.get: lắng nghe request loại GET, "/": đường dẫn
def read_root():   # hàm này chạy khi có người truy cập vào "/"
    return {"message:" "Shop APi đang chạy!"}   #VD: khi có người truy cập vào link:...., sẽ trả về return để biết là server đang hoạt động bình thường