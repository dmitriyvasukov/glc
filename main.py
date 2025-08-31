from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")






@app.get("/", response_class=HTMLResponse)
  
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request" : request})



