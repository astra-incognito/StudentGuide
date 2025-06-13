from db_setup import db
from datetime import datetime

# 1. Notifications
class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String, default='info')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_for = db.Column(db.DateTime)

# 2. Study Groups
class StudyGroup(db.Model):
    __tablename__ = 'study_group'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudyGroupMember(db.Model):
    __tablename__ = 'study_group_member'
    id = db.Column(db.String, primary_key=True)
    group_id = db.Column(db.String, db.ForeignKey('study_group.id'))
    user_id = db.Column(db.String, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

# 3. File Attachments
class FileAttachment(db.Model):
    __tablename__ = 'file_attachment'
    id = db.Column(db.String, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    uploaded_by = db.Column(db.String, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.String, db.ForeignKey('task.id'))
    event_id = db.Column(db.String, db.ForeignKey('calendar_event.id'))
    course_id = db.Column(db.String, db.ForeignKey('course.id'))

# 4. Notes
class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.String, db.ForeignKey('course.id'))
    project_id = db.Column(db.String, db.ForeignKey('project.id'))

# 5. Pomodoro Sessions
class PomodoroSession(db.Model):
    __tablename__ = 'pomodoro_session'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    task_id = db.Column(db.String, db.ForeignKey('task.id'))

# 6. Goal Badges
class Badge(db.Model):
    __tablename__ = 'badge'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

# 7. Calendar Sync Tokens
class CalendarSyncToken(db.Model):
    __tablename__ = 'calendar_sync_token'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    provider = db.Column(db.String, nullable=False)  # google, outlook, apple
    token = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 8. User Preferences (for theme, dark mode, etc.)
class UserPreference(db.Model):
    __tablename__ = 'user_preference'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    theme = db.Column(db.String, default='light')
    accent_color = db.Column(db.String, default='#007bff')
    dark_mode = db.Column(db.Boolean, default=False)
    pwa_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
