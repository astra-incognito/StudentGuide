from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import *
from datetime import datetime, date, timedelta
import logging
import os
import uuid

def send_invitation_email(email, project_id, invitation_id, message=""):
    """Send project invitation email using SendGrid"""
    try:
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_key:
            return False
            
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Get project details
        project = None
        for p in data_store.get_all_projects():
            if p.id == project_id:
                project = p
                break
                
        if not project:
            return False
            
        # Create email content
        subject = f"You're invited to join '{project.name}' project"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0d6efd;">Project Invitation</h2>
            <p>You've been invited to collaborate on the project: <strong>{project.name}</strong></p>
            
            {f"<p><em>Message from the team:</em><br>{message}</p>" if message else ""}
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Project Details:</h3>
                <p><strong>Name:</strong> {project.name}</p>
                <p><strong>Description:</strong> {project.description}</p>
                <p><strong>Status:</strong> {project.status.title()}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{request.host_url}invite/{invitation_id}/accept" 
                   style="background: #0d6efd; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Accept Invitation
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                This invitation will expire in 7 days. If you have any questions, 
                please contact the project team.
            </p>
        </div>
        """
        
        sg = SendGridAPIClient(sendgrid_key)
        message = Mail(
            from_email=Email("noreply@studenthub.com"),
            to_emails=To(email),
            subject=subject,
            html_content=html_content
        )
        
        response = sg.send(message)
        return response.status_code == 202
        
    except Exception as e:
        logging.error(f"SendGrid error: {e}")
        return False

@app.route('/')
def dashboard():
    """Main dashboard with overview widgets"""
    # Dashboard stats (example: count queries)
    stats = {
        'pending_tasks': Task.query.filter_by(status='pending').count(),
        'overdue_tasks': Task.query.filter(Task.due_date < date.today(), Task.status != 'completed').count(),
        'completed_today': Task.query.filter(Task.completed_at != None, db.func.date(Task.completed_at) == date.today()).count(),
        'habits_completed_today': Habit.query.filter(Habit.last_completed == date.today()).count(),
        'active_streaks': db.session.query(db.func.sum(Habit.streak)).scalar() or 0,
        'active_goals': Goal.query.filter_by(status='active').count(),
        'avg_goal_progress': round(db.session.query(db.func.avg(Goal.progress)).scalar() or 0, 1),
        'total_courses': Course.query.count(),
        'total_projects': Project.query.count()
    }
    quote = "Education is the most powerful weapon which you can use to change the world. - Nelson Mandela"  # Placeholder
    recent_tasks = Task.query.filter(Task.status != "completed").order_by(Task.due_date.asc().nullslast()).limit(5).all()
    upcoming_events = CalendarEvent.query.filter(CalendarEvent.start_date >= date.today(), CalendarEvent.start_date <= date.today() + timedelta(days=7)).order_by(CalendarEvent.start_date.asc()).limit(5).all()
    active_habits = Habit.query.limit(5).all()
    return render_template('dashboard.html', 
                         stats=stats, 
                         quote=quote,
                         recent_tasks=recent_tasks,
                         upcoming_events=upcoming_events,
                         active_habits=active_habits)

@app.route('/tasks')
def tasks():
    """Task and assignment management"""
    all_tasks = Task.query.all()
    courses = Course.query.all()
    # Filter tasks by status and category
    filter_status = request.args.get('status', 'all')
    filter_category = request.args.get('category', 'all')
    filtered_tasks = all_tasks
    if filter_status != 'all':
        filtered_tasks = [t for t in filtered_tasks if t.status == filter_status]
    if filter_category != 'all':
        filtered_tasks = [t for t in filtered_tasks if t.category == filter_category]
    filtered_tasks.sort(key=lambda x: x.due_date or date.max)
    return render_template('tasks.html', 
                         tasks=filtered_tasks, 
                         courses=courses,
                         filter_status=filter_status,
                         filter_category=filter_category,
                         today=date.today())

@app.route('/tasks/add', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        due_date = None
        if request.form.get('due_date'):
            due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        task = Task(
            id=str(uuid.uuid4()),
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            due_date=due_date,
            priority=request.form.get('priority', 'medium'),
            category=request.form.get('category', 'general'),
            course_id=request.form.get('course_id') if request.form.get('course_id') else None
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding task: {e}")
        flash('Error adding task. Please try again.', 'error')
    return redirect(url_for('tasks'))

@app.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed"""
    task = Task.query.get(task_id)
    if task:
        task.status = 'completed'
        task.completed_at = datetime.now()
        db.session.commit()
        flash('Task marked as completed!', 'success')
    else:
        flash('Task not found.', 'error')
    return redirect(url_for('tasks'))

@app.route('/tasks/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found.', 'error')
    return redirect(url_for('tasks'))

@app.route('/tasks/<task_id>', methods=['GET', 'POST'])
def view_or_edit_task(task_id):
    """View and edit a single task"""
    task = Task.query.get_or_404(task_id)
    courses = Course.query.all()
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.category = request.form.get('category')
        task.priority = request.form.get('priority')
        due_date = request.form.get('due_date')
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
        course_id = request.form.get('course_id')
        task.course_id = course_id if course_id else None
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks'))
    return render_template('task_detail.html', task=task, courses=courses)

@app.route('/calendar')
def calendar():
    """Calendar and scheduling view with month navigation"""
    from calendar import monthrange
    today = date.today()
    month = request.args.get('month', default=today.month, type=int)
    year = request.args.get('year', default=today.year, type=int)
    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)
    events = CalendarEvent.query.filter(CalendarEvent.start_date >= start_of_month, CalendarEvent.start_date <= end_of_month).all()
    # Pass a 'today' object for the selected month/year
    today_for_view = date(year, month, today.day if year == today.year and month == today.month else 1)
    return render_template('calendar.html', events=events, today=today_for_view)

@app.route('/calendar/add', methods=['POST'])
def add_calendar_event():
    """Add a new calendar event"""
    try:
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        event = CalendarEvent(
            id=str(uuid.uuid4()),
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            start_date=start_date,
            start_time=request.form.get('start_time', '09:00'),
            end_time=request.form.get('end_time', '10:00'),
            type=request.form.get('type', 'event'),
            reminder_minutes=int(request.form.get('reminder_minutes', 15))
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added to calendar!', 'success')
    except Exception as e:
        logging.error(f"Error adding calendar event: {e}")
        flash('Error adding calendar event. Please try again.', 'error')
    return redirect(url_for('calendar'))

@app.route('/courses')
def courses():
    """Course management"""
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/courses/add', methods=['POST'])
def add_course():
    """Add a new course"""
    try:
        course = Course(
            id=str(uuid.uuid4()),
            name=request.form.get('name'),
            code=request.form.get('code', ''),
            instructor=request.form.get('instructor', ''),
            credits=int(request.form.get('credits', 3)),
            schedule=request.form.get('schedule', ''),
            description=request.form.get('description', ''),
            color=request.form.get('color', '#007bff')
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding course: {e}")
        flash('Error adding course. Please try again.', 'error')
    
    return redirect(url_for('courses'))

@app.route('/habits')
def habits():
    """Habit tracking"""
    all_habits = Habit.query.all()
    return render_template('habits.html', habits=all_habits, today=date.today(), timedelta=timedelta)

@app.route('/habits/add', methods=['POST'])
def add_habit():
    """Add a new habit"""
    try:
        habit = Habit(
            id=str(uuid.uuid4()),
            name=request.form.get('name'),
            description=request.form.get('description', ''),
            target_frequency=request.form.get('target_frequency', 'daily')
        )
        db.session.add(habit)
        db.session.commit()
        flash('Habit added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding habit: {e}")
        flash('Error adding habit. Please try again.', 'error')
    return redirect(url_for('habits'))

@app.route('/habits/<habit_id>/complete', methods=['POST'])
def complete_habit(habit_id):
    """Mark a habit as completed for today"""
    habit = Habit.query.get(habit_id)
    if habit:
        today_str = date.today().isoformat()
        if habit.completion_dates is None:
            habit.completion_dates = []
        if today_str not in habit.completion_dates:
            habit.completion_dates.append(today_str)
            habit.last_completed = date.today()
            habit.streak = (habit.streak or 0) + 1
            if habit.streak > (habit.best_streak or 0):
                habit.best_streak = habit.streak
            db.session.commit()
        flash('Habit completed for today!', 'success')
    else:
        flash('Habit not found.', 'error')
    return redirect(url_for('habits'))

@app.route('/goals')
def goals():
    """Goal setting and tracking"""
    all_goals = Goal.query.all()
    return render_template('goals.html', goals=all_goals)

@app.route('/goals/add', methods=['POST'])
def add_goal():
    """Add a new goal"""
    try:
        target_date = None
        if request.form.get('target_date'):
            target_date = datetime.strptime(request.form.get('target_date'), '%Y-%m-%d').date()
        goal = Goal(
            id=str(uuid.uuid4()),
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            category=request.form.get('category', 'academic'),
            target_date=target_date,
            progress=int(request.form.get('progress', 0))
        )
        db.session.add(goal)
        db.session.commit()
        flash('Goal added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding goal: {e}")
        flash('Error adding goal. Please try again.', 'error')
    return redirect(url_for('goals'))

@app.route('/goals/<goal_id>/update_progress', methods=['POST'])
def update_goal_progress(goal_id):
    """Update goal progress"""
    try:
        progress = int(request.form.get('progress', 0))
        progress = max(0, min(100, progress))
        goal = Goal.query.get(goal_id)
        if goal:
            goal.progress = progress
            db.session.commit()
            flash('Goal progress updated!', 'success')
        else:
            flash('Goal not found.', 'error')
    except Exception as e:
        logging.error(f"Error updating goal progress: {e}")
        flash('Error updating progress. Please try again.', 'error')
    return redirect(url_for('goals'))

@app.route('/finances')
def finances():
    """Financial tracking"""
    all_entries = FinanceEntry.query.order_by(FinanceEntry.date.desc()).all()
    # Calculate summary
    total_income = sum(e.amount for e in all_entries if getattr(e, 'type', None) == 'income')
    total_expenses = sum(e.amount for e in all_entries if getattr(e, 'type', None) == 'expense')
    balance = total_income - total_expenses
    summary = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance
    }
    return render_template('finances.html', entries=all_entries, summary=summary, today=date.today)  # Pass today as a function, not a value

@app.route('/finances/add', methods=['POST'])
def add_finance_entry():
    """Add a new financial entry"""
    try:
        entry_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        entry = FinanceEntry(
            id=str(uuid.uuid4()),
            description=request.form.get('description'),
            amount=float(request.form.get('amount')),
            category=request.form.get('category', 'other'),
            type=request.form.get('type', 'expense'),
            date=entry_date
        )
        db.session.add(entry)
        db.session.commit()
        flash('Financial entry added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding finance entry: {e}")
        flash('Error adding financial entry. Please try again.', 'error')
    return redirect(url_for('finances'))

@app.route('/devotion')
def devotion():
    """Bible study and devotion tracking"""
    all_entries = DevotionEntry.query.order_by(DevotionEntry.date.desc()).all()
    return render_template('devotion.html', entries=all_entries, today=date.today)

@app.route('/devotion/add', methods=['POST'])
def add_devotion_entry():
    """Add a new devotion entry"""
    try:
        entry_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        entry = DevotionEntry(
            id=str(uuid.uuid4()),
            title=request.form.get('title'),
            scripture=request.form.get('scripture', ''),
            notes=request.form.get('notes', ''),
            reflection=request.form.get('reflection', ''),
            date=entry_date,
            duration_minutes=int(request.form.get('duration_minutes', 0))
        )
        db.session.add(entry)
        db.session.commit()
        flash('Devotion entry added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding devotion entry: {e}")
        flash('Error adding devotion entry. Please try again.', 'error')
    return redirect(url_for('devotion'))

@app.route('/projects')
def projects():
    """Project management with Kanban boards"""
    all_projects = Project.query.all()
    selected_project_id = request.args.get('project_id')
    selected_project = None
    project_tasks = {"todo": [], "in_progress": [], "done": []}
    if selected_project_id:
        selected_project = Project.query.get(selected_project_id)
        if selected_project:
            tasks = ProjectTask.query.filter_by(project_id=selected_project_id).all()
            for task in tasks:
                project_tasks[task.status].append(task)
    return render_template('projects.html',
                         projects=all_projects,
                         selected_project=selected_project,
                         project_tasks=project_tasks)

@app.route('/projects/add', methods=['POST'])
def add_project():
    """Add a new project"""
    try:
        due_date = None
        if request.form.get('due_date'):
            due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        project = Project(
            id=str(uuid.uuid4()),
            name=request.form.get('name'),
            description=request.form.get('description', ''),
            due_date=due_date,
            status=request.form.get('status', 'planning')
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding project: {e}")
        flash('Error adding project. Please try again.', 'error')
    return redirect(url_for('projects'))

@app.route('/projects/<project_id>/tasks/add', methods=['POST'])
def add_project_task(project_id):
    """Add a task to a project"""
    try:
        task = ProjectTask(
            id=str(uuid.uuid4()),
            title=request.form.get('task_title'),
            description=request.form.get('task_description', ''),
            status=request.form.get('status', 'todo'),
            project_id=project_id,
            assigned_to=request.form.get('assigned_to', ''),
            priority=request.form.get('priority', 'medium')
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added to project!', 'success')
    except Exception as e:
        logging.error(f"Error adding project task: {e}")
        flash('Error adding project task. Please try again.', 'error')
    return redirect(url_for('projects', project_id=project_id))

@app.route('/projects/tasks/<task_id>/move', methods=['POST'])
def move_project_task(task_id):
    """Move a project task to different status column"""
    task = ProjectTask.query.get(task_id)
    if task:
        task.status = request.form.get('status', task.status)
        db.session.commit()
        flash('Task moved successfully!', 'success')
    else:
        flash('Task not found.', 'error')
    return redirect(url_for('projects', project_id=request.form.get('project_id')))

@app.route('/projects/<project_id>/invite', methods=['POST'])
def invite_project_member(project_id):
    """Invite a member to join a project via email"""
    email = request.form.get('email')
    message = request.form.get('message', '')
    invited_by = request.form.get('invited_by', 'Project Admin')
    
    try:
        # Create invitation
        invitation_id = data_store.create_invitation(project_id, email, invited_by)
        
        # Send email invitation (if SendGrid is configured)
        if send_invitation_email(email, project_id, invitation_id, message):
            flash(f'Invitation sent to {email} successfully!', 'success')
        else:
            flash(f'Invitation created for {email}. Email delivery requires SendGrid configuration.', 'warning')
            
    except Exception as e:
        logging.error(f"Error sending invitation: {e}")
        flash('Error sending invitation. Please try again.', 'error')
    
    return redirect(url_for('projects', project_id=project_id))

@app.route('/projects/<project_id>/members')
def project_members(project_id):
    """View and manage project members"""
    project = Project.query.get(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    # Placeholder: You should implement a ProjectMember model and query members from the database
    members = []
    pending_invitations = []
    return render_template('project_members.html', 
                         project=project, 
                         members=members,
                         pending_invitations=pending_invitations)

@app.route('/projects/<project_id>/activity')
def project_activity(project_id):
    """View project activity timeline"""
    project = Project.query.get(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    # Placeholder: You should implement a ProjectActivity model and query activities from the database
    activities = []
    return render_template('project_activity.html', 
                         project=project, 
                         activities=activities, 
                         today=date.today)  # Pass today as a function for template

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    from models import Settings
    user_id = 1  # For demo, use a static user id. Replace with real user id in production.
    settings = Settings.query.get(user_id)
    if request.method == 'POST':
        settings.student_name = request.form.get('studentName')
        settings.university = request.form.get('university')
        settings.major = request.form.get('major')
        settings.grad_year = request.form.get('gradYear')
        settings.task_reminders = 'taskReminders' in request.form
        settings.habit_reminders = 'habitReminders' in request.form
        settings.devotion_reminders = 'devotionReminders' in request.form
        settings.calendar_notifications = 'calendarNotifications' in request.form
        settings.reminder_time = request.form.get('reminderTime')
        settings.theme = request.form.get('theme')
        settings.accent_color = request.form.get('accentColor')
        settings.compact_mode = 'compactMode' in request.form
        settings.animations = 'animations' in request.form
        settings.gpa_scale = request.form.get('gpaScale')
        settings.default_task_category = request.form.get('defaultTaskCategory')
        settings.week_start = request.form.get('weekStart')
        settings.show_gpa = 'showGpa' in request.form
        db.session.commit()
        flash('Settings updated!', 'success')
        return redirect(url_for('settings'))
    if not settings:
        settings = Settings(id=user_id)
        db.session.add(settings)
        db.session.commit()
    return render_template('settings.html', settings=settings)

# API endpoints for AJAX functionality
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Get dashboard statistics as JSON"""
    stats = {
        'pending_tasks': Task.query.filter_by(status='pending').count(),
        'overdue_tasks': Task.query.filter(Task.due_date < date.today(), Task.status != 'completed').count(),
        'completed_today': Task.query.filter(Task.completed_at != None, db.func.date(Task.completed_at) == date.today()).count(),
        'habits_completed_today': Habit.query.filter(Habit.last_completed == date.today()).count(),
        'active_streaks': db.session.query(db.func.sum(Habit.streak)).scalar() or 0,
        'active_goals': Goal.query.filter_by(status='active').count(),
        'avg_goal_progress': round(db.session.query(db.func.avg(Goal.progress)).scalar() or 0, 1),
        'total_courses': Course.query.count(),
        'total_projects': Project.query.count()
    }
    return jsonify(stats)

@app.route('/api/habits/chart_data')
def api_habits_chart_data():
    """Get habit completion data for charts"""
    habits = Habit.query.all()
    chart_data = []
    for habit in habits:
        days = max(1, (date.today() - habit.created_at.date()).days)
        completion_rate = len(habit.completion_dates or []) / days * 100
        chart_data.append({
            'name': habit.name,
            'streak': habit.streak,
            'best_streak': habit.best_streak,
            'completion_rate': completion_rate
        })
    return jsonify(chart_data)

@app.route('/api/finances/chart_data')
def api_finances_chart_data():
    """Get financial data for charts"""
    entries = FinanceEntry.query.all()
    categories = {}
    for entry in entries:
        if entry.type == 'expense':
            if entry.category not in categories:
                categories[entry.category] = 0
            categories[entry.category] += entry.amount
    chart_data = {
        'labels': list(categories.keys()),
        'data': list(categories.values())
    }
    return jsonify(chart_data)

@app.route('/notifications')
def notifications():
    # For demo, use static user_id '1'. Replace with session user in production.
    user_id = '1'
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark_read/<notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    return ('', 204)

@app.route('/notifications/create_demo', methods=['POST'])
def create_demo_notification():
    user_id = '1'
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        message='This is a demo notification!',
        type='info'
    )
    db.session.add(notif)
    db.session.commit()
    return ('', 204)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500

@app.route('/tasks/<task_id>/edit', methods=['POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.title = request.form.get('title')
    task.description = request.form.get('description')
    task.category = request.form.get('category')
    task.priority = request.form.get('priority')
    due_date = request.form.get('due_date')
    task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
    course_id = request.form.get('course_id')
    task.course_id = course_id if course_id else None
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('tasks'))

from models import StudyGroup, StudyGroupMember

@app.route('/groups')
def groups():
    user_id = '1'  # Replace with session user in production
    groups = StudyGroup.query.all()
    my_groups = StudyGroupMember.query.filter_by(user_id=user_id).all()
    return render_template('groups.html', groups=groups, my_groups=my_groups)

@app.route('/groups/create', methods=['POST'])
def create_group():
    user_id = '1'
    name = request.form.get('name')
    description = request.form.get('description')
    group = StudyGroup(id=str(uuid.uuid4()), name=name, description=description)
    db.session.add(group)
    db.session.commit()
    member = StudyGroupMember(id=str(uuid.uuid4()), group_id=group.id, user_id=user_id)
    db.session.add(member)
    db.session.commit()
    return redirect(url_for('groups'))

@app.route('/groups/join/<group_id>', methods=['POST'])
def join_group(group_id):
    user_id = '1'
    if not StudyGroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        member = StudyGroupMember(id=str(uuid.uuid4()), group_id=group_id, user_id=user_id)
        db.session.add(member)
        db.session.commit()
    return redirect(url_for('groups'))

@app.route('/groups/<group_id>')
def group_detail(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    members = StudyGroupMember.query.filter_by(group_id=group_id).all()
    return render_template('group_detail.html', group=group, members=members)

from models import PomodoroSession, UserPreference

@app.route('/focus', methods=['GET', 'POST'])
def focus():
    user_id = '1'
    if request.method == 'POST':
        import uuid
        from datetime import datetime
        start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        duration = int((end_time - start_time).total_seconds() // 60)
        session = PomodoroSession(id=str(uuid.uuid4()), user_id=user_id, start_time=start_time, end_time=end_time, duration_minutes=duration, task_id=request.form.get('task_id'))
        db.session.add(session)
        db.session.commit()
        flash('Focus session saved!', 'success')
        return redirect(url_for('focus'))
    sessions = PomodoroSession.query.filter_by(user_id=user_id).order_by(PomodoroSession.start_time.desc()).all()
    tasks = Task.query.all()
    return render_template('focus.html', sessions=sessions, tasks=tasks)

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    user_id = '1'
    pref = UserPreference.query.filter_by(user_id=user_id).first()
    if not pref:
        import uuid
        pref = UserPreference(id=str(uuid.uuid4()), user_id=user_id)
        db.session.add(pref)
        db.session.commit()
    if request.method == 'POST':
        pref.theme = request.form.get('theme')
        pref.accent_color = request.form.get('accent_color')
        pref.dark_mode = 'dark_mode' in request.form
        pref.pwa_enabled = 'pwa_enabled' in request.form
        db.session.commit()
        flash('Preferences updated!', 'success')
        return redirect(url_for('preferences'))
    return render_template('preferences.html', pref=pref)
