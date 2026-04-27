"""
routers/users.py  – supabase-py version
"""
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from database.db import get_supabase
from schemas.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserOut])
def list_users(sb: Client = Depends(get_supabase)):
    res = sb.table("users").select("*").execute()
    return res.data or []


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, sb: Client = Depends(get_supabase)):
    res = sb.table("users").select("*").eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(404, "User not found")
    return res.data[0]


@router.post("/", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, sb: Client = Depends(get_supabase)):
    # Check duplicate email
    dup = sb.table("users").select("id").eq("email", body.email).execute()
    if dup.data:
        raise HTTPException(409, f"Email '{body.email}' already registered")
    row = body.model_dump()
    # Use provided ID (from Supabase auth) or generate a new one
    row["id"] = row["id"] or str(uuid.uuid4())
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    res = sb.table("users").insert(row).execute()
    return res.data[0]



@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, body: UserCreate, sb: Client = Depends(get_supabase)):
    row = body.model_dump()
    res = sb.table("users").update(row).eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(404, "User not found")
    return res.data[0]
