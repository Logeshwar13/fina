"""
routers/budgets.py  – CRUD for user budgets (Supabase)
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from supabase import Client
from database.db import get_supabase
from schemas.schemas import BudgetCreate, BudgetOut

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("/", response_model=List[BudgetOut])
def list_budgets(user_id: str = Query(...), sb: Client = Depends(get_supabase)):
    res = sb.table("budgets").select("*").eq("user_id", user_id).execute()
    return res.data or []


@router.post("/", response_model=BudgetOut, status_code=201)
def create_budget(body: BudgetCreate, sb: Client = Depends(get_supabase)):
    row = body.model_dump()
    row["id"] = str(uuid.uuid4())
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    res = sb.table("budgets").insert(row).execute()
    if not res.data:
        raise HTTPException(500, "Failed to create budget")
    return res.data[0]


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(budget_id: str, body: BudgetCreate, sb: Client = Depends(get_supabase)):
    row = body.model_dump()
    res = sb.table("budgets").update(row).eq("id", budget_id).execute()
    if not res.data:
        raise HTTPException(404, "Budget not found")
    return res.data[0]


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: str, sb: Client = Depends(get_supabase)):
    sb.table("budgets").delete().eq("id", budget_id).execute()
