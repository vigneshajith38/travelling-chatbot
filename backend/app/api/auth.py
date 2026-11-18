from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, UserPreference
from app.schemas.schemas import UserCreate, UserLogin, UserOut, Token, UserPreferenceSchema
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # If no token, check for default demo user or return demo user
    if not token:
        user = db.query(User).filter(User.email == "wanderer@wanderwise.com").first()
        if not user:
            # Create demo user automatically
            user = User(
                email="wanderer@wanderwise.com",
                hashed_password=get_password_hash("travel123"),
                full_name="Aarav Sharma",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            pref = UserPreference(
                user_id=user.id,
                preferred_styles=["mountains", "scenic", "peaceful", "coffee"],
                budget_level="moderate",
                travel_pace="balanced",
                preferred_currency="INR"
            )
            db.add(pref)
            db.commit()
        return user
        
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
    hashed = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed,
        full_name=user_in.full_name,
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Add preferences
    prefs = user_in.preferences or UserPreferenceSchema()
    user_pref = UserPreference(
        user_id=new_user.id,
        preferred_styles=prefs.preferred_styles,
        budget_level=prefs.budget_level,
        travel_pace=prefs.travel_pace,
        dietary_preferences=prefs.dietary_preferences,
        preferred_currency=prefs.preferred_currency
    )
    db.add(user_pref)
    db.commit()
    
    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/preferences", response_model=UserPreferenceSchema)
def update_preferences(pref_in: UserPreferenceSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)
        
    pref.preferred_styles = pref_in.preferred_styles
    pref.budget_level = pref_in.budget_level
    pref.travel_pace = pref_in.travel_pace
    pref.dietary_preferences = pref_in.dietary_preferences
    pref.preferred_currency = pref_in.preferred_currency
    db.commit()
    return pref_in

