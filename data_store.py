from typing import Dict, List, Any
from models import *
from datetime import datetime, date
import json

class InMemoryDataStore:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.courses: Dict[str, Course] = {}
        self.habits: Dict[str, Habit] = {}
        self.goals: Dict[str, Goal] = {}
        self.finance_entries: Dict[str, FinanceEntry] = {}
        self.devotion_entries: Dict[str, DevotionEntry] = {}
        self.projects: Dict[str, Project] = {}
        self.project_tasks: Dict[str, ProjectTask] = {}
        self.calendar_events: Dict[str, CalendarEvent] = {}
        
        # Initialize with some motivational quotes
        self.quotes = [
            "Education is the most powerful weapon which you can use to change the world. - Nelson Mandela",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "Trust in the Lord with all your heart and lean not on your own understanding. - Proverbs 3:5",
            "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you. - Jeremiah 29:11",
            "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go. - Joshua 1:9"
        ]
    
    # Task methods
    def add_task(self, task: Task) -> str:
        self.tasks[task.id] = task
        return task.id
    
    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    # Course methods
    def add_course(self, course: Course) -> str:
        self.courses[course.id] = course
        return course.id
    
    def get_course(self, course_id: str) -> Course:
        return self.courses.get(course_id)
    
    def get_all_courses(self) -> List[Course]:
        return list(self.courses.values())
    
    def update_course(self, course_id: str, **kwargs) -> bool:
        if course_id in self.courses:
            course = self.courses[course_id]
            for key, value in kwargs.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            return True
        return False
    
    def delete_course(self, course_id: str) -> bool:
        if course_id in self.courses:
            del self.courses[course_id]
            return True
        return False
    
    # Habit methods
    def add_habit(self, habit: Habit) -> str:
        self.habits[habit.id] = habit
        return habit.id
    
    def get_habit(self, habit_id: str) -> Habit:
        return self.habits.get(habit_id)
    
    def get_all_habits(self) -> List[Habit]:
        return list(self.habits.values())
    
    def update_habit(self, habit_id: str, **kwargs) -> bool:
        if habit_id in self.habits:
            habit = self.habits[habit_id]
            for key, value in kwargs.items():
                if hasattr(habit, key):
                    setattr(habit, key, value)
            return True
        return False
    
    def complete_habit(self, habit_id: str, completion_date: date = None) -> bool:
        if habit_id in self.habits:
            habit = self.habits[habit_id]
            if completion_date is None:
                completion_date = date.today()
            
            date_str = completion_date.isoformat()
            if date_str not in habit.completion_dates:
                habit.completion_dates.append(date_str)
                habit.last_completed = completion_date
                
                # Update streak
                if habit.last_completed == date.today():
                    habit.streak += 1
                    if habit.streak > habit.best_streak:
                        habit.best_streak = habit.streak
                        
            return True
        return False
    
    # Goal methods
    def add_goal(self, goal: Goal) -> str:
        self.goals[goal.id] = goal
        return goal.id
    
    def get_goal(self, goal_id: str) -> Goal:
        return self.goals.get(goal_id)
    
    def get_all_goals(self) -> List[Goal]:
        return list(self.goals.values())
    
    def update_goal(self, goal_id: str, **kwargs) -> bool:
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            for key, value in kwargs.items():
                if hasattr(goal, key):
                    setattr(goal, key, value)
            return True
        return False
    
    # Finance methods
    def add_finance_entry(self, entry: FinanceEntry) -> str:
        self.finance_entries[entry.id] = entry
        return entry.id
    
    def get_all_finance_entries(self) -> List[FinanceEntry]:
        return list(self.finance_entries.values())
    
    def get_finance_summary(self) -> Dict[str, float]:
        total_income = sum(entry.amount for entry in self.finance_entries.values() if entry.type == "income")
        total_expenses = sum(entry.amount for entry in self.finance_entries.values() if entry.type == "expense")
        balance = total_income - total_expenses
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance
        }
    
    # Devotion methods
    def add_devotion_entry(self, entry: DevotionEntry) -> str:
        self.devotion_entries[entry.id] = entry
        return entry.id
    
    def get_all_devotion_entries(self) -> List[DevotionEntry]:
        return sorted(list(self.devotion_entries.values()), key=lambda x: x.date, reverse=True)
    
    # Project methods
    def add_project(self, project: Project) -> str:
        self.projects[project.id] = project
        return project.id
    
    def get_all_projects(self) -> List[Project]:
        return list(self.projects.values())
    
    def add_project_task(self, task: ProjectTask) -> str:
        self.project_tasks[task.id] = task
        return task.id
    
    def get_project_tasks(self, project_id: str) -> List[ProjectTask]:
        return [task for task in self.project_tasks.values() if task.project_id == project_id]
    
    def update_project_task(self, task_id: str, **kwargs) -> bool:
        if task_id in self.project_tasks:
            task = self.project_tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            return True
        return False
    
    # Calendar methods
    def add_calendar_event(self, event: CalendarEvent) -> str:
        self.calendar_events[event.id] = event
        return event.id
    
    def get_calendar_events(self, start_date: date = None, end_date: date = None) -> List[CalendarEvent]:
        events = list(self.calendar_events.values())
        if start_date and end_date:
            events = [e for e in events if start_date <= e.start_date <= end_date]
        return sorted(events, key=lambda x: x.start_date)
    
    # Utility methods
    def get_random_quote(self) -> str:
        import random
        return random.choice(self.quotes)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        today = date.today()
        
        # Task stats
        pending_tasks = len([t for t in self.tasks.values() if t.status == "pending"])
        overdue_tasks = len([t for t in self.tasks.values() if t.due_date and t.due_date < today and t.status != "completed"])
        completed_today = len([t for t in self.tasks.values() if t.completed_at and t.completed_at.date() == today])
        
        # Habit stats
        habits_completed_today = len([h for h in self.habits.values() if h.last_completed == today])
        active_streaks = sum(h.streak for h in self.habits.values())
        
        # Goal stats
        active_goals = len([g for g in self.goals.values() if g.status == "active"])
        avg_progress = sum(g.progress for g in self.goals.values()) / len(self.goals) if self.goals else 0
        
        return {
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "completed_today": completed_today,
            "habits_completed_today": habits_completed_today,
            "active_streaks": active_streaks,
            "active_goals": active_goals,
            "avg_goal_progress": round(avg_progress, 1),
            "total_courses": len(self.courses),
            "total_projects": len(self.projects)
        }

# Global data store instance
data_store = InMemoryDataStore()
