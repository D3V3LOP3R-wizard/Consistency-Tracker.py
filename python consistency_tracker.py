import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import defaultdict
import calendar

class ConsistencyTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Consistency Tracker - Daily Progress Hub")
        self.root.geometry("1200x700")
        
        # Data storage
        self.data_file = "consistency_data.json"
        self.categories = []
        self.logs = []
        self.load_data()
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.refresh_display()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.bg_color = '#f0f2f6'
        self.primary_color = '#667eea'
        self.secondary_color = '#764ba2'
        self.success_color = '#48bb78'
        self.warning_color = '#f56565'
        self.text_color = '#2d3748'
        
        self.root.configure(bg=self.bg_color)
        
    def create_widgets(self):
        """Create all UI elements"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Stats cards
        self.create_stats_cards(main_container)
        
        # Main content area with notebook (tabs)
        self.create_notebook(main_container)
        
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="📊 Consistency Tracker", 
            font=('Helvetica', 24, 'bold'),
            foreground=self.primary_color
        )
        title_label.pack(side=tk.LEFT)
        
        # Save Progress Button
        save_btn = ttk.Button(
            header_frame,
            text="💾 Save Progress",
            command=self.manual_save,
            style='Accent.TButton'
        )
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        # Date
        self.date_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=('Helvetica', 12),
            foreground=self.text_color
        )
        self.date_label.pack(side=tk.RIGHT, pady=10)
        
    def create_stats_cards(self, parent):
        """Create statistics cards"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configure grid
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Stats data
        self.stats_vars = {
            'current_streak': tk.StringVar(value="0"),
            'longest_streak': tk.StringVar(value="0"),
            'completion_rate': tk.StringVar(value="0%"),
            'total_logs': tk.StringVar(value="0")
        }
        
        stats_config = [
            ("Current Streak", "current_streak", "🔥"),
            ("Longest Streak", "longest_streak", "🏆"),
            ("Completion Rate", "completion_rate", "📈"),
            ("Total Logs", "total_logs", "📝")
        ]
        
        for i, (title, var_key, emoji) in enumerate(stats_config):
            self.create_stat_card(stats_frame, title, self.stats_vars[var_key], emoji, i)
            
    def create_stat_card(self, parent, title, value_var, emoji, column):
        """Create individual stat card"""
        card = ttk.Frame(parent, relief='solid', borderwidth=1)
        card.grid(row=0, column=column, padx=5, pady=5, sticky='nsew')
        
        # Title
        ttk.Label(
            card,
            text=f"{emoji} {title}",
            font=('Helvetica', 10),
            foreground=self.text_color
        ).pack(pady=(10, 5))
        
        # Value
        ttk.Label(
            card,
            textvariable=value_var,
            font=('Helvetica', 20, 'bold'),
            foreground=self.primary_color
        ).pack(pady=(0, 10))
        
    def create_notebook(self, parent):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_categories_tab()
        self.create_calendar_tab()
        self.create_analytics_tab()
        
    def create_dashboard_tab(self):
        """Create dashboard tab with today's progress"""
        dashboard = ttk.Frame(self.notebook)
        self.notebook.add(dashboard, text="📋 Dashboard")
        
        # Split into left and right panels
        left_panel = ttk.Frame(dashboard)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(dashboard)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Today's progress
        self.create_today_progress(left_panel)
        
        # Weekly overview
        self.create_weekly_overview(right_panel)
        
    def create_today_progress(self, parent):
        """Create today's progress section"""
        today_frame = ttk.LabelFrame(parent, text="Today's Progress", padding=10)
        today_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrollable content
        canvas = tk.Canvas(today_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(today_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store reference for updating
        self.today_frame = scrollable_frame
        
    def create_weekly_overview(self, parent):
        """Create weekly overview section"""
        weekly_frame = ttk.LabelFrame(parent, text="This Week", padding=10)
        weekly_frame.pack(fill=tk.BOTH, expand=True)
        
        # Week grid
        self.week_grid = ttk.Frame(weekly_frame)
        self.week_grid.pack(fill=tk.BOTH, expand=True)
        
        # Day labels
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = ttk.Label(self.week_grid, text=day, font=('Helvetica', 9))
            label.grid(row=0, column=i, padx=5, pady=5)
            
        # Week circles (will be updated)
        self.week_circles = []
        for i in range(7):
            circle_frame = ttk.Frame(self.week_grid, width=40, height=40)
            circle_frame.grid(row=1, column=i, padx=5, pady=5)
            circle_frame.grid_propagate(False)
            
            circle_label = ttk.Label(circle_frame, text="", font=('Helvetica', 10))
            circle_label.pack(expand=True, fill=tk.BOTH)
            
            self.week_circles.append(circle_label)
            
    def create_categories_tab(self):
        """Create categories management tab"""
        categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(categories_frame, text="🎯 Categories")
        
        # Top bar with add button
        top_bar = ttk.Frame(categories_frame)
        top_bar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            top_bar,
            text="➕ Add Category",
            command=self.add_category_dialog,
            style='Accent.TButton'
        ).pack(side=tk.LEFT)
        
        # Categories list
        self.categories_list = ttk.Frame(categories_frame)
        self.categories_list.pack(fill=tk.BOTH, expand=True)
        
    def create_calendar_tab(self):
        """Create monthly calendar tab"""
        calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendar_frame, text="📅 Calendar")
        
        # Month navigation
        nav_frame = ttk.Frame(calendar_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(nav_frame, text="◀", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        self.month_label = ttk.Label(nav_frame, text="", font=('Helvetica', 12, 'bold'))
        self.month_label.pack(side=tk.LEFT, padx=20)
        ttk.Button(nav_frame, text="▶", command=self.next_month).pack(side=tk.LEFT, padx=5)
        
        # Calendar grid
        self.calendar_grid = ttk.Frame(calendar_frame)
        self.calendar_grid.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Current month/year
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
    def create_analytics_tab(self):
        """Create analytics tab with charts"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.fig.patch.set_facecolor(self.bg_color)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, analytics_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.categories = data.get('categories', [])
                    self.logs = data.get('logs', [])
            except:
                self.categories = []
                self.logs = []
                
    def save_data(self):
        """Save data to JSON file"""
        data = {
            'categories': self.categories,
            'logs': self.logs
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def refresh_display(self):
        """Refresh all displays"""
        self.update_stats()
        self.update_today_progress()
        self.update_weekly_overview()
        self.update_categories_list()
        self.update_calendar()
        self.update_analytics()
        
    def update_stats(self):
        """Update statistics cards"""
        # Calculate current streak
        current_streak = self.calculate_current_streak()
        self.stats_vars['current_streak'].set(str(current_streak))
        
        # Calculate longest streak
        longest_streak = self.calculate_longest_streak()
        self.stats_vars['longest_streak'].set(str(longest_streak))
        
        # Calculate monthly completion rate
        completion_rate = self.calculate_monthly_completion()
        self.stats_vars['completion_rate'].set(f"{completion_rate}%")
        
        # Total logs
        self.stats_vars['total_logs'].set(str(len(self.logs)))
        
    def calculate_current_streak(self):
        """Calculate current consistency streak"""
        if not self.categories:
            return 0
            
        streak = 0
        check_date = datetime.now().date()
        
        while True:
            day_logs = [log for log in self.logs 
                       if datetime.strptime(log['date'], '%Y-%m-%d').date() == check_date]
            
            # Check if all categories were logged on this day
            categories_logged = set(log['category_id'] for log in day_logs)
            if len(categories_logged) < len(self.categories):
                break
                
            streak += 1
            check_date -= timedelta(days=1)
            
        return streak
        
    def calculate_longest_streak(self):
        """Calculate longest streak ever"""
        if not self.logs:
            return 0
            
        # Group logs by date
        logs_by_date = defaultdict(set)
        for log in self.logs:
            logs_by_date[log['date']].add(log['category_id'])
            
        dates = sorted(logs_by_date.keys())
        if not dates:
            return 0
            
        longest = 1
        current = 1
        
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i-1], '%Y-%m-%d').date()
            curr_date = datetime.strptime(dates[i], '%Y-%m-%d').date()
            
            if (curr_date - prev_date).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
                
        return longest
        
    def calculate_monthly_completion(self):
        """Calculate completion rate for current month"""
        today = datetime.now()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        
        if not self.categories:
            return 0
            
        completed_days = 0
        for day in range(1, days_in_month + 1):
            check_date = date(today.year, today.month, day)
            day_logs = [log for log in self.logs 
                       if datetime.strptime(log['date'], '%Y-%m-%d').date() == check_date]
            
            categories_logged = set(log['category_id'] for log in day_logs)
            if len(categories_logged) == len(self.categories):
                completed_days += 1
                
        return int((completed_days / days_in_month) * 100) if days_in_month > 0 else 0
        
    def update_today_progress(self):
        """Update today's progress display"""
        # Clear existing widgets
        for widget in self.today_frame.winfo_children():
            widget.destroy()
            
        if not self.categories:
            ttk.Label(
                self.today_frame,
                text="No categories yet. Add some categories to start tracking!",
                foreground=self.text_color
            ).pack(pady=20)
            return
            
        today = datetime.now().date().isoformat()
        
        for category in self.categories:
            # Get today's logs for this category
            category_logs = [log for log in self.logs 
                           if log['category_id'] == category['id'] and log['date'] == today]
            
            total_minutes = sum(log['minutes'] for log in category_logs)
            goal = category['goal']
            progress = min((total_minutes / goal) * 100, 100) if goal > 0 else 0
            
            # Category frame
            cat_frame = ttk.Frame(self.today_frame)
            cat_frame.pack(fill=tk.X, pady=5)
            
            # Category info
            info_frame = ttk.Frame(cat_frame)
            info_frame.pack(fill=tk.X)
            
            ttk.Label(
                info_frame,
                text=category['name'],
                font=('Helvetica', 11, 'bold'),
                foreground=category['color']
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                info_frame,
                text=f"{total_minutes}/{goal} min",
                font=('Helvetica', 10)
            ).pack(side=tk.LEFT, padx=10)
            
            ttk.Button(
                info_frame,
                text="Log Progress",
                command=lambda c=category: self.log_progress_dialog(c)
            ).pack(side=tk.RIGHT)
            
            # Progress bar
            progress_frame = ttk.Frame(cat_frame, height=10)
            progress_frame.pack(fill=tk.X, pady=(5, 0))
            
            # Create custom progress bar
            canvas = tk.Canvas(progress_frame, height=10, highlightthickness=0)
            canvas.pack(fill=tk.X)
            
            # Draw background
            canvas.create_rectangle(0, 0, 1000, 10, fill='#e2e8f0', outline='')
            
            # Draw progress
            if progress > 0:
                canvas.create_rectangle(0, 0, 10 * progress, 10, 
                                      fill=category['color'], outline='')
                
    def update_weekly_overview(self):
        """Update weekly overview display"""
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        for i in range(7):
            check_date = start_of_week + timedelta(days=i)
            date_str = check_date.isoformat()
            
            # Get logs for this day
            day_logs = [log for log in self.logs if log['date'] == date_str]
            categories_logged = set(log['category_id'] for log in day_logs)
            
            # Calculate completion
            if not self.categories:
                completion = 0
            else:
                completion = len(categories_logged) / len(self.categories)
                
            # Update circle
            circle = self.week_circles[i]
            
            if completion == 1:
                circle.configure(text="✓", background=self.success_color)
            elif completion > 0:
                circle.configure(text="~", background=self.warning_color)
            else:
                circle.configure(text="○", background='#e2e8f0')
                
            # Add date number
            circle.configure(text=f"{check_date.day}\n{circle.cget('text')}")
            
    def update_categories_list(self):
        """Update categories list display"""
        # Clear existing widgets
        for widget in self.categories_list.winfo_children():
            widget.destroy()
            
        if not self.categories:
            ttk.Label(
                self.categories_list,
                text="No categories yet. Click 'Add Category' to get started!",
                foreground=self.text_color
            ).pack(pady=20)
            return
            
        for category in self.categories:
            self.create_category_card(category)
            
    def create_category_card(self, category):
        """Create a category card"""
        card = ttk.Frame(self.categories_list, relief='solid', borderwidth=1)
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Category info
        info_frame = ttk.Frame(card)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            info_frame,
            text=category['name'],
            font=('Helvetica', 12, 'bold'),
            foreground=category['color']
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            info_frame,
            text=f"Goal: {category['goal']} min/day",
            font=('Helvetica', 10)
        ).pack(side=tk.LEFT, padx=20)
        
        # Calculate streak for this category
        streak = self.calculate_category_streak(category['id'])
        ttk.Label(
            info_frame,
            text=f"🔥 {streak} day streak",
            font=('Helvetica', 10)
        ).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="Log",
            command=lambda: self.log_progress_dialog(category),
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Edit",
            command=lambda: self.edit_category_dialog(category),
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Delete",
            command=lambda: self.delete_category(category['id']),
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
    def calculate_category_streak(self, category_id):
        """Calculate streak for a specific category"""
        # Get all logs for this category, sorted by date
        category_logs = [log for log in self.logs if log['category_id'] == category_id]
        dates = sorted(set(log['date'] for log in category_logs))
        
        if not dates:
            return 0
            
        # Calculate current streak
        streak = 0
        check_date = datetime.now().date()
        
        while True:
            date_str = check_date.isoformat()
            if date_str in dates:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
                
        return streak
        
    def update_calendar(self):
        """Update calendar display"""
        # Clear grid
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
            
        # Update month label
        self.month_label.config(
            text=datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        )
        
        # Get days in month
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        first_day = datetime(self.current_year, self.current_month, 1).weekday()
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(
                self.calendar_grid,
                text=day,
                font=('Helvetica', 9, 'bold')
            ).grid(row=0, column=i, padx=2, pady=2)
            
        # Create calendar cells
        row = 1
        col = first_day
        
        for day in range(1, days_in_month + 1):
            date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
            
            # Create cell
            cell = ttk.Frame(
                self.calendar_grid,
                relief='solid',
                borderwidth=1,
                width=80,
                height=60
            )
            cell.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
            cell.grid_propagate(False)
            
            # Get completion for this day
            day_logs = [log for log in self.logs if log['date'] == date_str]
            categories_logged = set(log['category_id'] for log in day_logs)
            
            if self.categories:
                completion = len(categories_logged) / len(self.categories)
            else:
                completion = 0
                
            # Set background color based on completion
            if completion == 1:
                bg_color = self.success_color
            elif completion > 0:
                bg_color = self.warning_color
            else:
                bg_color = '#f7fafc'
                
            # Day number
            ttk.Label(
                cell,
                text=str(day),
                font=('Helvetica', 10, 'bold'),
                background=bg_color
            ).pack(anchor='nw', padx=2, pady=2)
            
            # Completion bar
            if completion > 0:
                bar_frame = ttk.Frame(cell, height=4)
                bar_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
                
                canvas = tk.Canvas(bar_frame, height=4, highlightthickness=0, bg=bg_color)
                canvas.pack(fill=tk.X)
                canvas.create_rectangle(0, 0, 76 * completion, 4, 
                                      fill=self.primary_color, outline='')
                                      
            col += 1
            if col > 6:
                col = 0
                row += 1
                
    def update_analytics(self):
        """Update analytics charts"""
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        
        if not self.categories or not self.logs:
            self.ax1.text(0.5, 0.5, 'No data available', 
                         ha='center', va='center', transform=self.ax1.transAxes)
            self.ax2.text(0.5, 0.5, 'No data available', 
                         ha='center', va='center', transform=self.ax2.transAxes)
        else:
            # Category distribution pie chart
            category_totals = defaultdict(int)
            for log in self.logs:
                category_totals[log['category_id']] += log['minutes']
                
            if category_totals:
                sizes = list(category_totals.values())
                labels = []
                for cat_id in category_totals.keys():
                    category = next((c for c in self.categories if c['id'] == cat_id), None)
                    labels.append(category['name'] if category else 'Unknown')
                    
                colors = [next((c['color'] for c in self.categories if c['id'] == cat_id), '#667eea') 
                         for cat_id in category_totals.keys()]
                         
                self.ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
                self.ax1.set_title('Time Distribution by Category')
                
            # Weekly progress line chart
            last_7_days = []
            dates = []
            for i in range(6, -1, -1):
                date = datetime.now().date() - timedelta(days=i)
                dates.append(date.strftime('%a'))
                
                day_logs = [log for log in self.logs if log['date'] == date.isoformat()]
                total_minutes = sum(log['minutes'] for log in day_logs)
                last_7_days.append(total_minutes)
                
            self.ax2.plot(dates, last_7_days, marker='o', color=self.primary_color)
            self.ax2.set_title('Daily Total Minutes (Last 7 Days)')
            self.ax2.set_xlabel('Day')
            self.ax2.set_ylabel('Minutes')
            self.ax2.grid(True, alpha=0.3)
            
        # Refresh canvas
        self.fig.tight_layout()
        self.canvas.draw()
        
    def add_category_dialog(self):
        """Dialog to add a new category"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Category")
        dialog.geometry("300x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text="Category Name:").pack(pady=(10, 5))
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Daily Goal (minutes):").pack(pady=5)
        goal_entry = ttk.Entry(dialog, width=30)
        goal_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Color:").pack(pady=5)
        colors = ['#667eea', '#48bb78', '#f56565', '#ed8936', '#9f7aea']
        color_var = tk.StringVar(value=colors[0])
        
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        for color in colors:
            rb = ttk.Radiobutton(
                color_frame,
                variable=color_var,
                value=color,
                text=''
            )
            rb.pack(side=tk.LEFT, padx=2)
            
            # Color indicator
            indicator = tk.Canvas(color_frame, width=20, height=20, bg=color, highlightthickness=0)
            indicator.pack(side=tk.LEFT, padx=2)
            
        def save():
            name = name_entry.get().strip()
            goal = goal_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a category name")
                return
                
            try:
                goal = int(goal)
                if goal <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Please enter a valid positive number for goal")
                return
                
            # Create new category
            new_category = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'name': name,
                'goal': goal,
                'color': color_var.get()
            }
            
            self.categories.append(new_category)
            self.save_data()
            self.refresh_display()
            
            dialog.destroy()
            
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def edit_category_dialog(self, category):
        """Dialog to edit a category"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Category")
        dialog.geometry("300x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields with current values
        ttk.Label(dialog, text="Category Name:").pack(pady=(10, 5))
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.insert(0, category['name'])
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Daily Goal (minutes):").pack(pady=5)
        goal_entry = ttk.Entry(dialog, width=30)
        goal_entry.insert(0, str(category['goal']))
        goal_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Color:").pack(pady=5)
        colors = ['#667eea', '#48bb78', '#f56565', '#ed8936', '#9f7aea']
        color_var = tk.StringVar(value=category['color'])
        
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        for color in colors:
            rb = ttk.Radiobutton(
                color_frame,
                variable=color_var,
                value=color,
                text=''
            )
            rb.pack(side=tk.LEFT, padx=2)
            
            indicator = tk.Canvas(color_frame, width=20, height=20, bg=color, highlightthickness=0)
            indicator.pack(side=tk.LEFT, padx=2)
            
        def save():
            name = name_entry.get().strip()
            goal = goal_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a category name")
                return
                
            try:
                goal = int(goal)
                if goal <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Please enter a valid positive number for goal")
                return
                
            # Update category
            category['name'] = name
            category['goal'] = goal
            category['color'] = color_var.get()
            
            self.save_data()
            self.refresh_display()
            
            dialog.destroy()
            
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def log_progress_dialog(self, category):
        """Dialog to log progress for a category"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Log Progress - {category['name']}")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Form fields
        ttk.Label(dialog, text="Minutes spent:").pack(pady=(10, 5))
        minutes_entry = ttk.Entry(dialog, width=30)
        minutes_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Date:").pack(pady=5)
        date_entry = ttk.Entry(dialog, width=30)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Notes (optional):").pack(pady=5)
        notes_entry = ttk.Entry(dialog, width=30)
        notes_entry.pack(pady=5)
        
        def save():
            minutes = minutes_entry.get().strip()
            date_str = date_entry.get().strip()
            notes = notes_entry.get().strip()
            
            if not minutes:
                messagebox.showerror("Error", "Please enter minutes spent")
                return
                
            try:
                minutes = int(minutes)
                if minutes <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Please enter a valid positive number for minutes")
                return
                
            # Validate date
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD)")
                return
                
            # Create new log
            new_log = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'category_id': category['id'],
                'minutes': minutes,
                'date': date_str,
                'notes': notes
            }
            
            self.logs.append(new_log)
            self.save_data()
            self.refresh_display()
            
            dialog.destroy()
            
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def delete_category(self, category_id):
        """Delete a category and its logs"""
        if messagebox.askyesno("Confirm Delete", 
                               "Are you sure you want to delete this category? All related logs will also be deleted."):
            # Remove category
            self.categories = [c for c in self.categories if c['id'] != category_id]
            
            # Remove related logs
            self.logs = [log for log in self.logs if log['category_id'] != category_id]
            
            self.save_data()
            self.refresh_display()
            
    def prev_month(self):
        """Go to previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()
        
    def next_month(self):
        """Go to next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()

    def manual_save(self):
        """Manually save progress and show confirmation"""
        self.save_data()
        messagebox.showinfo("Progress Saved", "Your progress has been saved successfully!")

def main():
    root = tk.Tk()
    app = ConsistencyTracker(root)
    
    # Set window icon (optional)
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
        
    root.mainloop()

if __name__ == "__main__":
    main()  