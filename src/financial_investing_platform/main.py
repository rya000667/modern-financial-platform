from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME")
templates = Jinja2Templates(directory=str(__package__).replace('.', '/') + "/templates")

# In-memory data stores
users = {"admin": "password"}
stocks = []
options = []
risk_profiles = []


def get_user(request: Request):
    return request.session.get("user")


@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if users.get(username) == password:
        request.session["user"] = username
        return RedirectResponse("/stocks", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/stocks")
def get_stocks(request: Request):
    if not get_user(request):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("stocks.html", {"request": request, "stocks": stocks})


@app.get("/stocks/new")
def new_stock(request: Request):
    return templates.TemplateResponse("stock_form.html", {"request": request, "form_title": "Add Stock", "action": "/stocks", "stock": None})


@app.get("/stocks/{ticker}/edit")
def edit_stock(request: Request, ticker: str):
    stock = next((s for s in stocks if s["ticker"] == ticker), None)
    return templates.TemplateResponse("stock_form.html", {"request": request, "form_title": "Edit Stock", "action": f"/stocks/{ticker}", "stock": stock})


@app.post("/stocks")
def create_stock(ticker: str = Form(...), shares: int = Form(...), avg_price_paid: float = Form(...), cost_basis: float = Form(...), current_price: float = Form(...)):
    stocks.append({"ticker": ticker, "shares": shares, "avg_price_paid": avg_price_paid, "cost_basis": cost_basis, "current_price": current_price, "last_updated": "-", "is_active": True})
    return RedirectResponse("/stocks", status_code=303)


@app.post("/stocks/{ticker}")
def update_stock(request: Request, ticker: str, shares: int = Form(None), avg_price_paid: float = Form(None), cost_basis: float = Form(None), current_price: float = Form(None), delete: int = Form(0)):
    stock = next((s for s in stocks if s["ticker"] == ticker), None)
    if not stock:
        return RedirectResponse("/stocks", status_code=303)
    if delete:
        stock["is_active"] = False
    else:
        stock.update({"shares": shares, "avg_price_paid": avg_price_paid, "cost_basis": cost_basis, "current_price": current_price})
    return RedirectResponse("/stocks", status_code=303)


@app.get("/options")
def get_options(request: Request):
    if not get_user(request):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("options.html", {"request": request, "options": options})


@app.get("/options/new")
def new_option(request: Request):
    return templates.TemplateResponse("option_form.html", {"request": request, "form_title": "Add Option", "action": "/options", "option": None})


@app.get("/options/{opt_tkr}/edit")
def edit_option(request: Request, opt_tkr: str):
    opt = next((o for o in options if o["option_ticker"] == opt_tkr), None)
    return templates.TemplateResponse("option_form.html", {"request": request, "form_title": "Edit Option", "action": f"/options/{opt_tkr}", "option": opt})


@app.post("/options")
def create_option(option_ticker: str = Form(...), ticker: str = Form(...), quantity: int = Form(...), expiration_date: str = Form(...), avg_price: float = Form(...), cost_basis: float = Form(...)):
    options.append({"option_ticker": option_ticker, "ticker": ticker, "quantity": quantity, "expiration_date": expiration_date, "avg_price": avg_price, "cost_basis": cost_basis, "last_updated": "-", "is_active": True})
    return RedirectResponse("/options", status_code=303)


@app.post("/options/{opt_tkr}")
def update_option(opt_tkr: str, ticker: str = Form(None), quantity: int = Form(None), expiration_date: str = Form(None), avg_price: float = Form(None), cost_basis: float = Form(None), delete: int = Form(0)):
    opt = next((o for o in options if o["option_ticker"] == opt_tkr), None)
    if not opt:
        return RedirectResponse("/options", status_code=303)
    if delete:
        opt["is_active"] = False
    else:
        opt.update({"ticker": ticker, "quantity": quantity, "expiration_date": expiration_date, "avg_price": avg_price, "cost_basis": cost_basis})
    return RedirectResponse("/options", status_code=303)


@app.get("/risk")
def get_risk(request: Request):
    if not get_user(request):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("risk.html", {"request": request, "risk_profiles": risk_profiles})


@app.get("/risk/new")
def new_risk(request: Request):
    return templates.TemplateResponse("risk_form.html", {"request": request, "form_title": "Add Risk", "action": "/risk", "risk": None})


@app.get("/risk/{ticker}/edit")
def edit_risk(request: Request, ticker: str):
    rp = next((r for r in risk_profiles if r["ticker"] == ticker), None)
    return templates.TemplateResponse("risk_form.html", {"request": request, "form_title": "Edit Risk", "action": f"/risk/{ticker}", "risk": rp})


@app.post("/risk")
def create_risk(ticker: str = Form(...), min_prob_OTM: float = Form(...), max_prob_OTM: float = Form(...), min_rorc: float = Form(...)):
    risk_profiles.append({"ticker": ticker, "min_prob_OTM": min_prob_OTM, "max_prob_OTM": max_prob_OTM, "min_rorc": min_rorc, "last_updated": "-", "is_active": True})
    return RedirectResponse("/risk", status_code=303)


@app.post("/risk/{ticker}")
def update_risk(ticker: str, min_prob_OTM: float = Form(None), max_prob_OTM: float = Form(None), min_rorc: float = Form(None), delete: int = Form(0)):
    rp = next((r for r in risk_profiles if r["ticker"] == ticker), None)
    if not rp:
        return RedirectResponse("/risk", status_code=303)
    if delete:
        rp["is_active"] = False
    else:
        rp.update({"min_prob_OTM": min_prob_OTM, "max_prob_OTM": max_prob_OTM, "min_rorc": min_rorc})
    return RedirectResponse("/risk", status_code=303)


@app.websocket("/ws/options")
async def options_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json({"msg": "price", "count": len(options)})
            await ws.receive_text()
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    uvicorn.run("financial_investing_platform.main:app", host="0.0.0.0", port=8000, reload=True)
