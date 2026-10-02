import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from .auth import authenticate_user, create_access_token, get_session_user, hash_password, require_session_user
from .config import ALLOWED_IMAGE_TYPES, BASE_DIR, MAX_UPLOAD_MB
from .database import get_db
from .models import Recommendation, User
from .recommendation_service import home_recommendations, jewelry_recommendations, party_recommendations

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def context(request: Request, db: Session, **extra):
    data = {"request": request, "user": get_session_user(request, db)}
    data.update(extra)
    return data


def save_recommendation(db: Session, user: User, category: str, inputs: dict, result: dict) -> Recommendation:
    record = Recommendation(
        user_id=user.id,
        category=category,
        input_json=json.dumps(inputs, ensure_ascii=False),
        result_json=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="home.html", context=context(request, db))


@router.get("/testimonials", response_class=HTMLResponse)
def testimonials(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="testimonials.html", context=context(request, db))


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="register.html", context=context(request, db))


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.lower().strip()
    if len(password) < 8:
        return templates.TemplateResponse(request=request, name="register.html", context=context(request, db, error="Password must be at least 8 characters."), status_code=400)
    if db.scalar(select(User).where(User.email == email)):
        return templates.TemplateResponse(request=request, name="register.html", context=context(request, db, error="An account with this email already exists."), status_code=400)
    user = User(name=name.strip(), email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="login.html", context=context(request, db))


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(request=request, name="login.html", context=context(request, db, error="Invalid email or password."), status_code=401)
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/token")
def token(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@router.get("/session-info")
def session_info(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    return {"authenticated": bool(user), "user": {"id": user.id, "name": user.name, "email": user.email} if user else None}


@router.get("/session-data")
def session_data(request: Request, db: Session = Depends(get_db)):
    user = require_session_user(request, db)
    count = len(user.recommendations)
    return {"user_id": user.id, "name": user.name, "recommendation_count": count}


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    recent = db.scalars(select(Recommendation).where(Recommendation.user_id == user.id).order_by(desc(Recommendation.created_at)).limit(5)).all()
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context(request, db, recent=recent))


@router.get("/planner/home", response_class=HTMLResponse)
def home_planner(request: Request, db: Session = Depends(get_db)):
    if not get_session_user(request, db):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="home_planner.html", context=context(request, db))


@router.get("/planner/party", response_class=HTMLResponse)
def party_planner(request: Request, db: Session = Depends(get_db)):
    if not get_session_user(request, db):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="party_planner.html", context=context(request, db))


@router.get("/planner/jewelry", response_class=HTMLResponse)
def jewelry_planner(request: Request, db: Session = Depends(get_db)):
    if not get_session_user(request, db):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request=request, name="jewelry_planner.html", context=context(request, db))


@router.post("/generate-home", response_class=HTMLResponse)
def generate_home(
    request: Request,
    budget: float = Form(..., gt=0),
    rooms: str = Form(...),
    style: str = Form("modern"),
    needs: str = Form(...),
    db: Session = Depends(get_db),
):
    user = require_session_user(request, db)
    result = home_recommendations(budget, rooms, style, needs)
    record = save_recommendation(db, user, "Home", {"budget": budget, "rooms": rooms, "style": style, "needs": needs}, result.model_dump())
    return templates.TemplateResponse(request=request, name="recommendations.html", context=context(request, db, result=result, record=record, category="Home"))


@router.post("/generate-party", response_class=HTMLResponse)
def generate_party(
    request: Request,
    budget: float = Form(..., gt=0),
    guests: int = Form(..., gt=0, le=5000),
    event_type: str = Form(...),
    venue: str = Form("any"),
    city: str = Form(""),
    db: Session = Depends(get_db),
):
    user = require_session_user(request, db)
    result = party_recommendations(budget, guests, event_type, venue, city)
    record = save_recommendation(db, user, "Party", {"budget": budget, "guests": guests, "event_type": event_type, "venue": venue, "city": city}, result.model_dump())
    return templates.TemplateResponse(request=request, name="recommendations.html", context=context(request, db, result=result, record=record, category="Party"))


@router.post("/generate-jewelry", response_class=HTMLResponse)
async def generate_jewelry(
    request: Request,
    budget: float = Form(..., gt=0),
    occasion: str = Form(...),
    style: str = Form(...),
    metal: str = Form("any"),
    outfit_notes: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    user = require_session_user(request, db)
    image_bytes = None
    mime_type = None
    if outfit_image and outfit_image.filename:
        mime_type = outfit_image.content_type or ""
        if mime_type not in ALLOWED_IMAGE_TYPES:
            return templates.TemplateResponse(request=request, name="jewelry_planner.html", context=context(request, db, error="Upload a JPG, PNG, or WEBP image."), status_code=400)
        image_bytes = await outfit_image.read()
        if len(image_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
            return templates.TemplateResponse(request=request, name="jewelry_planner.html", context=context(request, db, error=f"Image must be {MAX_UPLOAD_MB} MB or smaller."), status_code=400)
    result = jewelry_recommendations(budget, occasion, style, metal, outfit_notes, image_bytes, mime_type)
    record = save_recommendation(db, user, "Jewelry", {"budget": budget, "occasion": occasion, "style": style, "metal": metal, "outfit_notes": outfit_notes, "image_supplied": bool(image_bytes)}, result.model_dump())
    return templates.TemplateResponse(request=request, name="recommendations.html", context=context(request, db, result=result, record=record, category="Jewelry"))


@router.get("/history", response_class=HTMLResponse)
def history(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    records = db.scalars(select(Recommendation).where(Recommendation.user_id == user.id).order_by(desc(Recommendation.created_at))).all()
    return templates.TemplateResponse(request=request, name="history.html", context=context(request, db, records=records))


@router.get("/recommendations-details/{record_id}", response_class=HTMLResponse)
def recommendation_details(record_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    record = db.get(Recommendation, record_id)
    if not record or record.user_id != user.id:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    result = json.loads(record.result_json)
    return templates.TemplateResponse(request=request, name="recommendation_details.html", context=context(request, db, record=record, result=result))
