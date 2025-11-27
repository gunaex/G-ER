from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import MasterMachine, User, MachineStatus
from schemas import MachineCreate, MachineResponse, MachineBase
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/machines",
    tags=["Machine Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[MachineResponse])
def read_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieve all machines.
    """
    machines = db.query(MasterMachine).offset(skip).limit(limit).all()
    return machines

@router.post("/", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(machine: MachineCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Create a new machine.
    """
    db_machine = db.query(MasterMachine).filter(MasterMachine.machine_code == machine.machine_code).first()
    if db_machine:
        raise HTTPException(status_code=400, detail="Machine code already registered")
    
    new_machine = MasterMachine(**machine.dict())
    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)
    return new_machine

@router.get("/{machine_id}", response_model=MachineResponse)
def read_machine(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Get a specific machine by ID.
    """
    machine = db.query(MasterMachine).filter(MasterMachine.id == machine_id).first()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.put("/{machine_id}", response_model=MachineResponse)
def update_machine(machine_id: int, machine_update: MachineCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Update a machine.
    """
    db_machine = db.query(MasterMachine).filter(MasterMachine.id == machine_id).first()
    if db_machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    for key, value in machine_update.dict().items():
        setattr(db_machine, key, value)
    
    db.commit()
    db.refresh(db_machine)
    return db_machine

@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(machine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Delete a machine (soft delete or hard delete depending on policy, here hard delete for simplicity or check dependencies).
    """
    db_machine = db.query(MasterMachine).filter(MasterMachine.id == machine_id).first()
    if db_machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    db.delete(db_machine)
    db.commit()
    return None
