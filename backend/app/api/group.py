from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.session import get_db
from app.models.models import Trip, TripMember, GroupVote, User
from app.schemas.schemas import GroupInviteRequest, TripMemberOut, GroupVoteCreate, GroupVoteOut
from app.api.auth import get_current_user

router = APIRouter(prefix="/group", tags=["Group Travel"])

@router.post("/{trip_id}/invite", response_model=TripMemberOut)
def invite_group_member(
    trip_id: int,
    invite_in: GroupInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    trip.is_group = True
    
    new_member = TripMember(
        trip_id=trip.id,
        name=invite_in.name,
        email=invite_in.email,
        role=invite_in.role,
        budget_share=round(trip.total_budget / max(1, trip.travellers_count + 1), 2),
        status="accepted"
    )
    trip.travellers_count += 1
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.post("/join/{share_code}", response_model=TripMemberOut)
def join_trip_by_code(
    share_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.share_code == share_code.upper()).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Invalid trip invite link or code")
        
    existing = db.query(TripMember).filter(TripMember.trip_id == trip.id, TripMember.email == current_user.email).first()
    if existing:
        return existing
        
    trip.is_group = True
    trip.travellers_count += 1
    new_member = TripMember(
        trip_id=trip.id,
        user_id=current_user.id,
        name=current_user.full_name,
        email=current_user.email,
        role="member",
        budget_share=round(trip.total_budget / trip.travellers_count, 2),
        status="accepted"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.post("/{trip_id}/votes", response_model=GroupVoteOut)
def vote_on_item(
    trip_id: int,
    vote_in: GroupVoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vote = GroupVote(
        trip_id=trip_id,
        member_id=current_user.id,
        member_name=current_user.full_name,
        item_type=vote_in.item_type,
        item_name=vote_in.item_name,
        vote=vote_in.vote,
        comment=vote_in.comment
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote

@router.get("/{trip_id}/votes", response_model=List[GroupVoteOut])
def get_trip_votes(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(GroupVote).filter(GroupVote.trip_id == trip_id).order_by(GroupVote.created_at.desc()).all()

@router.get("/{trip_id}/settlements")
def calculate_group_settlements(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    members = trip.members
    expenses = trip.expenses
    if not members:
        return {"settlements": [], "total_group_spent": 0, "per_person_share": 0}
        
    total_spent = sum(e.amount for e in expenses)
    member_count = len(members)
    per_person = round(total_spent / max(1, member_count), 2)
    
    # Calculate each person's paid amount
    paid_map = {m.name: 0.0 for m in members}
    for e in expenses:
        payer = e.payer_name or "Me"
        if payer in paid_map:
            paid_map[payer] += e.amount
        else:
            paid_map[payer] = e.amount
            
    # Balances: positive means owed money, negative means owes money
    balances = {name: round(paid - per_person, 2) for name, paid in paid_map.items()}
    
    # Simple settlement resolution
    debtors = [(name, -bal) for name, bal in balances.items() if bal < -0.01]
    creditors = [(name, bal) for name, bal in balances.items() if bal > 0.01]
    
    settlements = []
    d_idx, c_idx = 0, 0
    debtors = [list(x) for x in debtors]
    creditors = [list(x) for x in creditors]
    
    while d_idx < len(debtors) and c_idx < len(creditors):
        d_name, d_amt = debtors[d_idx]
        c_name, c_amt = creditors[c_idx]
        settle_amt = round(min(d_amt, c_amt), 2)
        
        if settle_amt > 0:
            settlements.append({
                "from_member": d_name,
                "to_member": c_name,
                "amount": settle_amt,
                "currency": trip.budget_currency
            })
            
        debtors[d_idx][1] -= settle_amt
        creditors[c_idx][1] -= settle_amt
        
        if debtors[d_idx][1] <= 0.01:
            d_idx += 1
        if creditors[c_idx][1] <= 0.01:
            c_idx += 1
            
    return {
        "total_group_spent": total_spent,
        "per_person_share": per_person,
        "balances": balances,
        "settlements": settlements
    }

