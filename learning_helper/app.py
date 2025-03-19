from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test", response_class=HTMLResponse)
async def test_get(request: Request):
    return templates.TemplateResponse("test.html", {"request": request, "message": "GET 方法调用成功!"})


@app.post("/test", response_class=HTMLResponse)
async def test_post(request: Request):
    form = await request.form()
    input_text = form.get("input_text")
    return templates.TemplateResponse("test.html", {"request": request, "message": f"POST 请求的输入内容: {input_text}"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9012)