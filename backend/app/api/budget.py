from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.models import Trip, Expense, User
from app.schemas.schemas import ExpenseCreate, ExpenseOut
from app.api.auth import get_current_user
from app.services.budget_service import calculate_budget_breakdown

router = APIRouter(prefix="/budget", tags=["Budget & Expenses"])

@router.get("/{trip_id}/summary")
def get_trip_budget_summary(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    expenses_data = [
        {"category": e.category, "amount": e.amount, "title": e.title}
        for e in trip.expenses
    ]
    
    summary = calculate_budget_breakdown(
        total_budget=trip.total_budget,
        travellers_count=trip.travellers_count,
        expenses=expenses_data,
        currency=trip.budget_currency
    )
    return summary

@router.post("/{trip_id}/expenses", response_model=ExpenseOut)
def add_trip_expense(
    trip_id: int,
    exp_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    expense = Expense(
        trip_id=trip_id,
        payer_id=current_user.id,
        payer_name=exp_in.payer_name or current_user.full_name,
        category=exp_in.category,
        title=exp_in.title,
        amount=exp_in.amount,
        currency=exp_in.currency or trip.budget_currency,
        split_type=exp_in.split_type
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.get("/{trip_id}/expenses", response_model=List[ExpenseOut])
def list_trip_expenses(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Expense).filter(Expense.trip_id == trip_id).order_by(Expense.created_at.desc()).all()

@router.delete("/expenses/{expense_id}")
def delete_trip_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exp = db.query(Expense).filter(Expense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return {"status": "deleted", "expense_id": expense_id}

