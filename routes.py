from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from data_store import data_store
from models import *
from datetime import datetime, date, timedelta
import logging
import os

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
    stats = data_store.get_dashboard_stats()
    quote = data_store.get_random_quote()
    
    # Get recent items for dashboard widgets
    recent_tasks = sorted([t for t in data_store.get_all_tasks() if t.status != "completed"], 
                         key=lambda x: x.due_date or date.max)[:5]
    upcoming_events = data_store.get_calendar_events(date.today(), date.today() + timedelta(days=7))[:5]
    active_habits = data_store.get_all_habits()[:5]
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         quote=quote,
                         recent_tasks=recent_tasks,
                         upcoming_events=upcoming_events,
                         active_habits=active_habits)

@app.route('/tasks')
def tasks():
    """Task and assignment management"""
    all_tasks = data_store.get_all_tasks()
    courses = data_store.get_all_courses()
    
    # Filter tasks by status and category
    filter_status = request.args.get('status', 'all')
    filter_category = request.args.get('category', 'all')
    
    filtered_tasks = all_tasks
    if filter_status != 'all':
        filtered_tasks = [t for t in filtered_tasks if t.status == filter_status]
    if filter_category != 'all':
        filtered_tasks = [t for t in filtered_tasks if t.category == filter_category]
    
    # Sort by due date
    filtered_tasks.sort(key=lambda x: x.due_date or date.max)
    
    return render_template('tasks.html', 
                         tasks=filtered_tasks, 
                         courses=courses,
                         filter_status=filter_status,
                         filter_category=filter_category)

@app.route('/tasks/add', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        due_date = None
        if request.form.get('due_date'):
            due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        
        task = Task(
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            due_date=due_date,
            priority=request.form.get('priority', 'medium'),
            category=request.form.get('category', 'general'),
            course_id=request.form.get('course_id') if request.form.get('course_id') else None
        )
        
        data_store.add_task(task)
        flash('Task added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding task: {e}")
        flash('Error adding task. Please try again.', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed"""
    success = data_store.update_task(task_id, 
                                   status='completed', 
                                   completed_at=datetime.now())
    if success:
        flash('Task completed!', 'success')
    else:
        flash('Task not found.', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    success = data_store.delete_task(task_id)
    if success:
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found.', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/calendar')
def calendar():
    """Calendar and scheduling view"""
    # Get current month events
    today = date.today()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    events = data_store.get_calendar_events(start_of_month, end_of_month)
    
    return render_template('calendar.html', events=events, today=today)

@app.route('/calendar/add', methods=['POST'])
def add_calendar_event():
    """Add a new calendar event"""
    try:
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        
        event = CalendarEvent(
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            start_date=start_date,
            start_time=request.form.get('start_time', '09:00'),
            end_time=request.form.get('end_time', '10:00'),
            type=request.form.get('type', 'event'),
            reminder_minutes=int(request.form.get('reminder_minutes', 15))
        )
        
        data_store.add_calendar_event(event)
        flash('Event added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding event: {e}")
        flash('Error adding event. Please try again.', 'error')
    
    return redirect(url_for('calendar'))

@app.route('/courses')
def courses():
    """Course management"""
    all_courses = data_store.get_all_courses()
    return render_template('courses.html', courses=all_courses)

@app.route('/courses/add', methods=['POST'])
def add_course():
    """Add a new course"""
    try:
        course = Course(
            name=request.form.get('name'),
            code=request.form.get('code', ''),
            instructor=request.form.get('instructor', ''),
            credits=int(request.form.get('credits', 3)),
            schedule=request.form.get('schedule', ''),
            description=request.form.get('description', ''),
            color=request.form.get('color', '#007bff')
        )
        
        data_store.add_course(course)
        flash('Course added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding course: {e}")
        flash('Error adding course. Please try again.', 'error')
    
    return redirect(url_for('courses'))

@app.route('/habits')
def habits():
    """Habit tracking"""
    all_habits = data_store.get_all_habits()
    return render_template('habits.html', habits=all_habits, today=date.today())

@app.route('/habits/add', methods=['POST'])
def add_habit():
    """Add a new habit"""
    try:
        habit = Habit(
            name=request.form.get('name'),
            description=request.form.get('description', ''),
            target_frequency=request.form.get('target_frequency', 'daily')
        )
        
        data_store.add_habit(habit)
        flash('Habit added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding habit: {e}")
        flash('Error adding habit. Please try again.', 'error')
    
    return redirect(url_for('habits'))

@app.route('/habits/<habit_id>/complete', methods=['POST'])
def complete_habit(habit_id):
    """Mark a habit as completed for today"""
    success = data_store.complete_habit(habit_id)
    if success:
        flash('Habit completed for today!', 'success')
    else:
        flash('Habit not found.', 'error')
    
    return redirect(url_for('habits'))

@app.route('/goals')
def goals():
    """Goal setting and tracking"""
    all_goals = data_store.get_all_goals()
    return render_template('goals.html', goals=all_goals)

@app.route('/goals/add', methods=['POST'])
def add_goal():
    """Add a new goal"""
    try:
        target_date = None
        if request.form.get('target_date'):
            target_date = datetime.strptime(request.form.get('target_date'), '%Y-%m-%d').date()
        
        goal = Goal(
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            category=request.form.get('category', 'academic'),
            target_date=target_date,
            progress=int(request.form.get('progress', 0))
        )
        
        data_store.add_goal(goal)
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
        progress = max(0, min(100, progress))  # Ensure between 0-100
        
        success = data_store.update_goal(goal_id, progress=progress)
        if success:
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
    all_entries = data_store.get_all_finance_entries()
    summary = data_store.get_finance_summary()
    
    # Sort by date (most recent first)
    all_entries.sort(key=lambda x: x.date, reverse=True)
    
    return render_template('finances.html', entries=all_entries, summary=summary, today=date.today)

@app.route('/finances/add', methods=['POST'])
def add_finance_entry():
    """Add a new financial entry"""
    try:
        entry_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        
        entry = FinanceEntry(
            description=request.form.get('description'),
            amount=float(request.form.get('amount')),
            category=request.form.get('category', 'other'),
            type=request.form.get('type', 'expense'),
            date=entry_date
        )
        
        data_store.add_finance_entry(entry)
        flash('Financial entry added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding finance entry: {e}")
        flash('Error adding financial entry. Please try again.', 'error')
    
    return redirect(url_for('finances'))

@app.route('/devotion')
def devotion():
    """Bible study and devotion tracking"""
    all_entries = data_store.get_all_devotion_entries()
    return render_template('devotion.html', entries=all_entries, today=date.today)

@app.route('/devotion/add', methods=['POST'])
def add_devotion_entry():
    """Add a new devotion entry"""
    try:
        entry_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        
        entry = DevotionEntry(
            title=request.form.get('title'),
            scripture=request.form.get('scripture', ''),
            notes=request.form.get('notes', ''),
            reflection=request.form.get('reflection', ''),
            date=entry_date,
            duration_minutes=int(request.form.get('duration_minutes', 0))
        )
        
        data_store.add_devotion_entry(entry)
        flash('Devotion entry added successfully!', 'success')
    except Exception as e:
        logging.error(f"Error adding devotion entry: {e}")
        flash('Error adding devotion entry. Please try again.', 'error')
    
    return redirect(url_for('devotion'))

@app.route('/projects')
def projects():
    """Project management with Kanban boards"""
    all_projects = data_store.get_all_projects()
    
    # Get project with tasks for Kanban view
    selected_project_id = request.args.get('project_id')
    selected_project = None
    project_tasks = {"todo": [], "in_progress": [], "done": []}
    
    if selected_project_id:
        selected_project = next((p for p in all_projects if p.id == selected_project_id), None)
        if selected_project:
            tasks = data_store.get_project_tasks(selected_project_id)
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
            name=request.form.get('name'),
            description=request.form.get('description', ''),
            due_date=due_date,
            status=request.form.get('status', 'planning')
        )
        
        data_store.add_project(project)
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
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            project_id=project_id,
            priority=request.form.get('priority', 'medium'),
            status='todo'
        )
        
        data_store.add_project_task(task)
        flash('Task added to project!', 'success')
    except Exception as e:
        logging.error(f"Error adding project task: {e}")
        flash('Error adding task. Please try again.', 'error')
    
    return redirect(url_for('projects', project_id=project_id))

@app.route('/projects/tasks/<task_id>/move', methods=['POST'])
def move_project_task(task_id):
    """Move a project task to different status column"""
    try:
        new_status = request.form.get('status')
        if new_status in ['todo', 'in_progress', 'done']:
            data_store.update_project_task(task_id, status=new_status)
            flash('Task moved successfully!', 'success')
        else:
            flash('Invalid status.', 'error')
    except Exception as e:
        logging.error(f"Error moving task: {e}")
        flash('Error moving task. Please try again.', 'error')
    
    project_id = request.form.get('project_id')
    return redirect(url_for('projects', project_id=project_id))

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
    project = None
    for p in data_store.get_all_projects():
        if p.id == project_id:
            project = p
            break
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    members = data_store.get_project_members(project_id)
    pending_invitations = data_store.get_pending_invitations(project_id)
    
    return render_template('project_members.html', 
                         project=project, 
                         members=members,
                         pending_invitations=pending_invitations)

@app.route('/projects/<project_id>/members/remove', methods=['POST'])
def remove_project_member(project_id):
    """Remove a member from a project"""
    email = request.form.get('email')
    
    try:
        if data_store.remove_project_member(project_id, email):
            flash(f'Member {email} removed from project.', 'success')
        else:
            flash('Error removing member.', 'error')
    except Exception as e:
        logging.error(f"Error removing member: {e}")
        flash('Error removing member. Please try again.', 'error')
    
    return redirect(url_for('project_members', project_id=project_id))

@app.route('/invite/<invitation_id>/accept')
def accept_project_invitation(invitation_id):
    """Accept a project invitation"""
    try:
        if data_store.accept_invitation(invitation_id):
            flash('Invitation accepted! You are now a member of the project.', 'success')
        else:
            flash('Invalid or expired invitation.', 'error')
    except Exception as e:
        logging.error(f"Error accepting invitation: {e}")
        flash('Error processing invitation.', 'error')
    
    return redirect(url_for('projects'))

@app.route('/projects/<project_id>/activity')
def project_activity(project_id):
    """View project activity timeline"""
    project = None
    for p in data_store.get_all_projects():
        if p.id == project_id:
            project = p
            break
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    # Get recent activity (this would be expanded with actual activity tracking)
    activities = [
        {"user": "admin@example.com", "action": "created project", "timestamp": datetime.now()},
        {"user": "member@example.com", "action": "added new task", "timestamp": datetime.now()},
    ]
    
    return render_template('project_activity.html', 
                         project=project, 
                         activities=activities)

@app.route('/settings')
def settings():
    """Application settings and preferences"""
    return render_template('settings.html')

# API endpoints for AJAX functionality
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Get dashboard statistics as JSON"""
    return jsonify(data_store.get_dashboard_stats())

@app.route('/api/habits/chart_data')
def api_habits_chart_data():
    """Get habit completion data for charts"""
    habits = data_store.get_all_habits()
    chart_data = []
    
    for habit in habits:
        chart_data.append({
            'name': habit.name,
            'streak': habit.streak,
            'best_streak': habit.best_streak,
            'completion_rate': len(habit.completion_dates) / max(1, (date.today() - habit.created_at.date()).days) * 100
        })
    
    return jsonify(chart_data)

@app.route('/api/finances/chart_data')
def api_finances_chart_data():
    """Get financial data for charts"""
    entries = data_store.get_all_finance_entries()
    
    # Group by category
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500
