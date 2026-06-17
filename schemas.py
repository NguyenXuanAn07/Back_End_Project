#VALIDATION
#File này có nhiệm vụ kiểm tra đầu vào dữ liệu, VD: email có đúng định dạng không,.....

from pydantic import BaseModel #pydantic là thư viện giúp kiểm tra dữ liệu tự động, BaseModel là bản mẫu gốc — giống như Base trong models.py nhưng dùng cho schemas
from typing import Optional #typing là thư viện giúp khái báo dữu liệu rõ ràng hơn, opyional là "có hoặc không", VD: sdt không yêu cầu nhập dữ liệu

#Sign up
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

#Login
class UserLogin(BaseModel):
    email: str
    password: str

#server trả về, dùng để hiển thị thông tin tài khoản
class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    #Pydantic cần được "bật" thêm tính năng để đọc dữ liệu từ SQLAlchemy models.
    class Config:
        from_attributes = True #"tôi cho phép đọc từ models"

#Thẻ token-thẻ ra vào khi đăng nhập
class Token(BaseModel):
    access_token: str
    token_type: str

#Schema này dùng khi user thêm sản phẩm vào giỏ hàng
class CartItemCreate(BaseModel):
    product_id: int  #thêm id sản phẩm vào giỏ hàng
    quantity: int = 1  #nếu không gán số lượng thì default là 1

#Schema này dùng khi user đặt hàng (checkout)
class OrderCreate(BaseModel):
    shipping_address: str

#Cập nhật số lượng
class CartItemUpdate(BaseModel):
    quantity: int