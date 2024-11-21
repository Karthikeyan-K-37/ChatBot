from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Main import process_message, state

# Create the FastAPI instance
app = FastAPI()

# Jinja2 Templates directory setup
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Render the index.html page
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get_response")
async def get_response(user_input: str = Form(...)):
    # If user says "goodbye", return the farewell message
    if user_input.lower() == "goodbye":
        return JSONResponse(content={"response": "Goodbye!"})

    # Process the user's input using logic from Main.py
    result = process_message(user_input, state)
    
    # Get the bot's response from the result
    bot_message = result["messages"][0]["content"]
    
    # Return the response as JSON
    return JSONResponse(content={"response": bot_message})

# Run the FastAPI application if the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
