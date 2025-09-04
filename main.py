from fastapi import FastAPI, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from database import get_db, init_db
from models import Product

app = FastAPI(title="GULA COLLECTION")

# Инициализация БД
init_db()

# Настройка шаблонов и статических файлов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Создаем папки если их нет
os.makedirs("static/uploads", exist_ok=True)

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products})

@app.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return templates.TemplateResponse("product.html", {"request": request, "product": product})

@app.get("/admin")
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse("admin.html", {"request": request, "products": products})

@app.post("/admin/add")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Сохранение изображения
    image_url = "/static/img/placeholder.jpg"
    if image and image.filename:
        # Создаем уникальное имя файла
        file_extension = Path(image.filename).suffix
        unique_filename = f"{os.urandom(8).hex()}{file_extension}"
        file_location = f"static/uploads/{unique_filename}"
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        image_url = f"/static/uploads/{unique_filename}"
    
    # Создание товара
    product = Product(
        name=name,
        description=description,
        price=price,
        image_url=image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/delete/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        # Удаляем изображение если оно не стандартное
        if product.image_url and "uploads" in product.image_url:
            image_path = f"static{product.image_url.split('/static')[-1]}"
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.delete(product)
        db.commit()
    
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/admin/edit/{product_id}")
async def edit_product_form(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return templates.TemplateResponse("admin_edit.html", {"request": request, "product": product})

@app.post("/admin/edit/{product_id}")
async def edit_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Обновляем данные
    product.name = name
    product.description = description
    product.price = price
    
    # Обновляем изображение если загружено новое
    if image and image.filename:
        # Удаляем старое изображение если оно не стандартное
        if product.image_url and "uploads" in product.image_url:
            old_image_path = f"static{product.image_url.split('/static')[-1]}"
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # Сохраняем новое изображение
        file_extension = Path(image.filename).suffix
        unique_filename = f"{os.urandom(8).hex()}{file_extension}"
        file_location = f"static/uploads/{unique_filename}"
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        product.image_url = f"/static/uploads/{unique_filename}"
    
    db.commit()
    
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)