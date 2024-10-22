from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import secrets

app = FastAPI()

# Jinja2 templates location
templates = Jinja2Templates(directory="templates")

# Define a valid token (this is for demonstration; you may want to store tokens in a database)
VALID_TOKEN = "1234567890abcdef"


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(token: str = Form(...)):
    if len(token) == 16 and secrets.compare_digest(token, VALID_TOKEN):
        # Redirect to a new page if the token is valid
        return RedirectResponse(f"/welcome/{token}", status_code=302)
    else:
        # Return to login page with an error message if invalid
        return templates.TemplateResponse(
            "login.html", {"error": "Invalid token", "request": {}}
        )


@app.get("/welcome/{token}", response_class=HTMLResponse)
async def welcome_page(request: Request, token: str):
    print(token)
    if token == VALID_TOKEN:
        return templates.TemplateResponse("welcome.html", {"request": request})
    else:
        return RedirectResponse("/", status_code=302)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
