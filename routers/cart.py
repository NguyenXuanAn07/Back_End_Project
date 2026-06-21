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
from schemas import CartItemCreate, OrderCreate, CartItemUpdate 

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
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail = "Giỏ hàng trống!")
    total = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail = f"Sản phẩm ID {item.product_id} không còn tồn tại!")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail = f"Sản phẩm {product.name} không đủ hàng!")
        total += product.price * item.quantity
    new_order = Order(
        user_id = current_user.id,
        total_amount = total,
        shipping_address = order.shipping_address,
        status = "pending"
    )
    db.add(new_order)
    db.flush()
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        order_item = OrderItem(
            order_id = new_order.id,
            product_id = item.product_id,
            quantity = item.quantity,
            price_at_order = product.price
        )
        db.add(order_item)
        product.stock -= item.quantity
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    db.refresh(new_order)
    return {"message": "Đặt hàng thành công!", "order_id": new_order.id, "total": float(total)}


#API4-CẬP NHẬT SỐ LƯỢNG TRONG GIỎ
@router.put("/{product_id}", status_code=status.HTTP_200_OK)
def update_cart_item(product_id: int, item: CartItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail= "Sản phẩm không có trong giỏ hàng!")
    
    cart_item.quantity = item.quantity
    db.commit()
    return {"message":"Đã cập nhật số lượng"}

#API5-XÓA SẢN PHẨM KHỎI GIỎ
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_cart_item(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=401, detail="Sản phẩm không tồn tại trong giỏ hàng!")
    db.delete(cart_item)
    db.commit()
    return {"message":"Đã xóa sản phẩm khỏi giỏ hàng!"}

#API LẤY TẤT CẢ ĐƠN HÀNG (dùng cho trang admin)
@router.get("/admin/orders")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    result = []
    for order in orders:      #Với mỗi đơn, tìm user đặt hàng
        user = db.query(User).filter(User.id == order.user_id).first()
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        products_text = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            products_text.append(f"{product.name} x{item.quantity}")

        result.append({
            "id": order.id,
            "customer": user.email,
            "email": user.email,
            "phone": user.phone,
            "address": order.shipping_address,
            "product": ", ".join(products_text),
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.isoformat()
        })
    return result