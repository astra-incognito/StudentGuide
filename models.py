from db_setup import db
from datetime import datetime, date

class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String, default="medium")
    status = db.Column(db.String, default="pending")
    category = db.Column(db.String, default="general")
    course_id = db.Column(db.String, db.ForeignKey('course.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Course(db.Model):
    __tablename__ = 'course'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String)
    instructor = db.Column(db.String)
    credits = db.Column(db.Integer, default=3)
    schedule = db.Column(db.String)
    description = db.Column(db.Text)
    color = db.Column(db.String, default="#007bff")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='course', lazy=True)

class Habit(db.Model):
    __tablename__ = 'habit'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    target_frequency = db.Column(db.String, default="daily")  # daily, weekly, monthly
    streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    last_completed = db.Column(db.Date)
    completion_dates = db.Column(db.ARRAY(db.String))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    __tablename__ = 'goal'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String, default="academic")  # academic, personal, spiritual, financial
    target_date = db.Column(db.Date)
    progress = db.Column(db.Integer, default=0)  # 0-100
    status = db.Column(db.String, default="active")  # active, completed, paused
    milestones = db.Column(db.ARRAY(db.String))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FinanceEntry(db.Model):
    __tablename__ = 'finance_entry'
    
    id = db.Column(db.String, primary_key=True)
    description = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, default=0.0)
    category = db.Column(db.String, default="other")  # income, food, transport, books, entertainment, other
    type = db.Column(db.String, default="expense")  # income, expense
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DevotionEntry(db.Model):
    __tablename__ = 'devotion_entry'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    scripture = db.Column(db.String)
    notes = db.Column(db.Text)
    reflection = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    duration_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'project'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String, default="planning")  # planning, active, completed, on_hold
    due_date = db.Column(db.Date)
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('ProjectTask', backref='project', lazy=True)

class ProjectTask(db.Model):
    __tablename__ = 'project_task'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String, default="todo")  # todo, in_progress, done
    project_id = db.Column(db.String, db.ForeignKey('project.id'))
    assigned_to = db.Column(db.String)
    priority = db.Column(db.String, default="medium")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_event'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, default=date.today)
    start_time = db.Column(db.String, default="09:00")
    end_time = db.Column(db.String, default="10:00")
    type = db.Column(db.String, default="event")  # event, class, assignment, personal
    reminder_minutes = db.Column(db.Integer, default=15)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectMember(db.Model):
    __tablename__ = 'project_member'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String)
    email = db.Column(db.String)
    name = db.Column(db.String)
    role = db.Column(db.String, default="member")  # owner, admin, member, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, default="active")  # active, inactive, pending

class ProjectInvitation(db.Model):
    __tablename__ = 'project_invitation'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String)
    email = db.Column(db.String)
    invited_by = db.Column(db.String)
    role = db.Column(db.String, default="member")
    message = db.Column(db.Text)
    status = db.Column(db.String, default="pending")  # pending, accepted, declined, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class TaskComment(db.Model):
    __tablename__ = 'task_comment'
    
    id = db.Column(db.String, primary_key=True)
    task_id = db.Column(db.String)
    author_email = db.Column(db.String)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectActivity(db.Model):
    __tablename__ = 'project_activity'
    
    id = db.Column(db.String, primary_key=True)
    project_id = db.Column(db.String)
    user_email = db.Column(db.String)
    action = db.Column(db.String)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(128))
    university = db.Column(db.String(128))
    major = db.Column(db.String(128))
    grad_year = db.Column(db.String(8))
    task_reminders = db.Column(db.Boolean, default=True)
    habit_reminders = db.Column(db.Boolean, default=True)
    devotion_reminders = db.Column(db.Boolean, default=True)
    calendar_notifications = db.Column(db.Boolean, default=True)
    reminder_time = db.Column(db.String(16), default='15')
    theme = db.Column(db.String(16), default='dark')
    accent_color = db.Column(db.String(8), default='#0d6efd')
    compact_mode = db.Column(db.Boolean, default=False)
    animations = db.Column(db.Boolean, default=True)
    gpa_scale = db.Column(db.String(8), default='4.0')
    default_task_category = db.Column(db.String(32), default='general')
    week_start = db.Column(db.String(8), default='sunday')
    show_gpa = db.Column(db.Boolean, default=True)
