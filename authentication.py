from fastapi import HTTPException
from typing import Optional, Any, Dict
from bcrypt import hashpw, gensalt, checkpw
from sqlmodel import select, Session
from jwt import encode, decode
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from backend.models.users import User, subscription

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


async def isSubscriptionActive(session: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """Check if a user has an active subscription."""
    statement = select(subscription).where(subscription.user_id == user_id)
    user_subscription = session.exec(statement).first()
    
    if not user_subscription:
        return None
    
    current_date = datetime.now().date()
    start_date = datetime.strptime(user_subscription.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(user_subscription.end_date, "%Y-%m-%d").date()
    
    return {
        "is_active": start_date <= current_date <= end_date,
        "plan_id": user_subscription.plan_id,
        "start_date": user_subscription.start_date,
        "end_date": user_subscription.end_date
    }


async def isUserExists(session: Session, username: str) -> bool:
    """Check if a user exists in the database by username."""
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user is not None


async def getUserByUsername(session: Session, username: str) -> User | None:
    """Retrieve a user from the database by username."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


async def login(session: Session, username: str, password: str):
    """Authenticate a user with username and password."""

    print(f"Attempting login for username: {username} and password: {password}")
    user = await getUserByUsername(session, username)
    print(f"User found: {user}")
    
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "no user found"})
    

    
    # Verify password against stored hash
    if checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):

        subscription = await isSubscriptionActive(session, user.id)

  
        token = encode(
            {
                "user_id": user.id, 
                "exp": datetime.now() + timedelta(minutes=30), 
                "subscription_active": subscription.get("is_active", False)
             },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        refresth_token = encode(
            {"user_id": user.id, 
             "exp": datetime.now() + timedelta(days=30), 
             "subscription_active": subscription.get("is_active", False)},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,

        )
        response = {
            "success": True,
            "message": "Login successful",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email},

            "subscription": subscription if subscription else None,
            "token": token,
            "refresh_token": refresth_token
        }
        return response
    
    raise HTTPException(status_code=401, detail={"success": False, "message": "Invalid credentials"})


async def register(session: Session, username: str, password: str, email: str):
    """Register a new user with username, password, and email."""
    # Check if username already exists
    if await isUserExists(session, username):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username already exists"})
    
    # Hash the password
    password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    
    # Create and save the new user
    user = User(username=username, email=email, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"success": True, "message": "Registration successful", "user_id": user.id}

def verify_token(token: str):
    """Verify a JWT token and return the user ID if valid."""
    try:
        payload = decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        isExpired = payload.get("exp") < datetime.now().timestamp()
        if isExpired:
            raise HTTPException(status_code=401, detail={"success": False, "message": "Token has expired"})

        return payload.get("user_id")
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def refresh_token(refresh_token: str):
        """Refresh JWT token - implementation depends on how you handle refresh tokens."""
        isValid = verify_token(refresh_token)
        if not isValid:
            raise HTTPException(status_code=401, detail={"success": False, "message": "Invalid refresh token"})
        
        token = encode(
            {"user_id": isValid, "exp": datetime.now() + timedelta(minutes=30)},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        return {"token": token, "refresh_token": refresh_token}


def subscribe(session: Session, user_id: int, plan_id: int, start_date: str, end_date: str):
    """Subscribe a user to a plan."""
    """ Payment processing logic would go here (e.g., integrating with Stripe or PayPal) """

    print(f"Subscribing user {user_id} to plan {plan_id} from {start_date} to {end_date}")

    new_subscription = subscription(user_id=user_id, plan_id=plan_id, start_date=start_date, end_date=end_date)
    session.add(new_subscription)
    session.commit()
    session.refresh(new_subscription)
    return {"success": True, "message": "Subscription successful", "subscription": new_subscription}


