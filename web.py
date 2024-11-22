from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Main import process_message, state

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get_response")
async def get_response(user_input: str = Form(...)):
    if user_input.lower() == "goodbye":
        return JSONResponse(content={"response": "Goodbye!"})

    result = process_message(user_input, state)

    bot_message = result["messages"][0]["content"]
 
    return JSONResponse(content={"response": bot_message})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
