from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Professor(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    username: str = Field(index = True, unique = True)
    password: str  # Plain text for stability
    classes: List["ClassRoom"] = Relationship(back_populates = "professor")


class ClassRoom(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    name: str  # e.g. "Class_A_ComSci"
    batch: str  # e.g. "2024"
    professor_id: int = Field(foreign_key = "professor.id")
    
    professor: Professor = Relationship(back_populates = "classes")
    students: List["Student"] = Relationship(back_populates = "classroom")
    
    # FIXED: Renamed from 'attendance' to 'attendance_records' to match the link below
    attendance_records: List["Attendance"] = Relationship(back_populates = "classroom")


class Student(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    roll_number: str
    name: str
    classroom_id: int = Field(foreign_key = "classroom.id")
    folder_path: str
    
    classroom: ClassRoom = Relationship(back_populates = "students")
    attendance_records: List["Attendance"] = Relationship(back_populates = "student")


class Attendance(SQLModel, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    date: str
    time: str
    method: str  # "Selfie" or "ClassPhoto"
    status: str
    
    student_id: int = Field(foreign_key = "student.id")
    classroom_id: int = Field(foreign_key = "classroom.id")
    
    # These 'back_populates' strings must match the variable names in the other classes exactly
    student: Student = Relationship(back_populates = "attendance_records")
    classroom: ClassRoom = Relationship(back_populates = "attendance_records")