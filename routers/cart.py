#GIỎ HÀNG VÀ ĐẶT HÀNG
#cart.py xử lý 3 việc:
#1. Thêm sản phẩm vào giỏ
#2. Xem giỏ hàng
#3. Đặt hàng (checkout)

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session 
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
ALGORITHM = os.getenv("ALGORITHM")

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
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail = "Khong tim thay user!")
    return user

#API1-THÊM SẢN PHẨM VÀO GIỎ HÀNG
@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=401, detail = "Product is not available!")
    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail = "Product is not enough!")
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item.product_id
    ).first()
    if existing:
        existing.quantity += item.quantity
    else:
        new_item = CartItem(
            user_id = current_user.id,
            product_id = item.product_id,
            quantity = item.quantity

        )
        db.add(new_item)
    db.commit()
    return {"message": "Đã thêm vào giỏ hàng"}

#API2-XEM GIỎ HÀNG
@router.get("/", status_code=status.HTTP_200_OK)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    result = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        result.append({
            "cart_item_id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "subtotal": product.price * item.quantity
        })
    return result

#API3-ĐẶT HÀNG(CHECKOUT)
@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()   #Lấy giỏ hàng của user để check
    if not cart_items:   #hàm báo giỏ trống
        raise HTTPException(status_code=400, detail = "Giỏ hàng trống!")
    total = 0
    for item in cart_items:   #Hàm tính tổng tiền
        product = db.query(Product).filter(Product.id == item.product_id).first()   #lấy danh sách products
        total += product.price * item.quantity   #tổng tiền
    new_order = Order(     #Tạo đơn hàng mới
        user_id = current_user.id,
        total_amount = total,
        shipping_address = order.shipping_address,
        status = "pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for item in cart_items:   #hàm lưu chi tiết của sản phẩm -> Trừ tồn kho
        product = db.query(Product).filter(Product.id == item.product_id).first()
        order_item = OrderItem(
            order_id = new_order.id,
            product_id = item.product_id,
            quantity = item.quantity,
            price_at_order = product.price
        )
        db.add(order_item)    #thêm vào db để trừ tồn kho của từng item trong order_item
        product.stock -= item.quantity   #Trừ tồn kho của từng item
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()    #Lọc user_id của giỏ hàng = user_id gần đây, rồi xóa giỏ hàng 
    db.commit()
    return {"message": "Đặt hàng thành công!", "order_id": new_order.id, "total": total}   #trả về thông tin đơn hàng
