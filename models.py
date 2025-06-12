from datetime import datetime, date
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    due_date: Optional[date] = None
    priority: str = "medium"  # low, medium, high, urgent
    status: str = "pending"  # pending, in_progress, completed
    category: str = "general"
    course_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class Course:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    code: str = ""
    instructor: str = ""
    credits: int = 3
    schedule: str = ""
    description: str = ""
    color: str = "#007bff"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Habit:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    target_frequency: str = "daily"  # daily, weekly, monthly
    streak: int = 0
    best_streak: int = 0
    last_completed: Optional[date] = None
    completion_dates: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Goal:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    category: str = "academic"  # academic, personal, spiritual, financial
    target_date: Optional[date] = None
    progress: int = 0  # 0-100
    status: str = "active"  # active, completed, paused
    milestones: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class FinanceEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    amount: float = 0.0
    category: str = "other"  # income, food, transport, books, entertainment, other
    type: str = "expense"  # income, expense
    date: date = field(default_factory=date.today)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DevotionEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    scripture: str = ""
    notes: str = ""
    reflection: str = ""
    date: date = field(default_factory=date.today)
    duration_minutes: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Project:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    status: str = "planning"  # planning, active, completed, on_hold
    due_date: Optional[date] = None
    progress: int = 0
    tasks: List[str] = field(default_factory=list)  # Task IDs
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProjectTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: str = "todo"  # todo, in_progress, done
    project_id: str = ""
    assigned_to: str = ""
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CalendarEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    start_date: date = field(default_factory=date.today)
    start_time: str = "09:00"
    end_time: str = "10:00"
    type: str = "event"  # event, class, assignment, personal
    reminder_minutes: int = 15
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProjectMember:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    email: str = ""
    name: str = ""
    role: str = "member"  # owner, admin, member, viewer
    joined_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, inactive, pending

@dataclass
class ProjectInvitation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    email: str = ""
    invited_by: str = ""
    role: str = "member"
    message: str = ""
    status: str = "pending"  # pending, accepted, declined, expired
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class TaskComment:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    author_email: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProjectActivity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    user_email: str = ""
    action: str = ""  # created_task, completed_task, added_member, etc.
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
