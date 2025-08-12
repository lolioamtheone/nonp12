import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity App")
        self.root.geometry("1000x600")
        self.data_file = "tasks.json"
        self.tasks = self.load_tasks()
        
        # Default opacity (1.0 = fully opaque, 0.0 = fully transparent)
        self.opacity = 1.0
        self.root.attributes("-alpha", self.opacity)
        
        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Custom fonts
        self.title_font = Font(family="Helvetica", size=12, weight="bold")
        self.task_font = Font(family="Helvetica", size=10)
        
        # Main task frame (left side)
        self.task_frame = ttk.LabelFrame(self.root, text="Task Management", padding=10)
        self.task_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.task_frame.grid_columnconfigure(0, weight=1)
        self.task_frame.grid_rowconfigure(1, weight=1)
        
        # Task list frame (right side)
        self.side_frame = ttk.LabelFrame(self.root, text="Smart Task View", padding=10)
        self.side_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.side_frame.grid_columnconfigure(0, weight=1)
        self.side_frame.grid_rowconfigure(0, weight=1)
        
        # Menu bar
        self.create_menu_bar()
        
        # Task entry widgets
        self.create_task_entry_widgets()
        
        # Task list
        self.create_task_list()
        
        # Smart view list
        self.create_smart_view()
        
        # Stats label
        self.stats_label = ttk.Label(self.task_frame, text="")
        self.stats_label.grid(row=3, column=0, sticky="w", pady=5)
        
        # Opacity control (added to the bottom right)
        self.create_opacity_control()
        
        self.update_stats()
        self.update_smart_view()
    
    def create_menu_bar(self):
        """Create the menu bar with opacity controls"""
        menubar = tk.Menu(self.root)
        
        # View menu with opacity presets
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Full Opacity (100%)", command=lambda: self.set_opacity(1.0))
        view_menu.add_command(label="High Opacity (80%)", command=lambda: self.set_opacity(0.8))
        view_menu.add_command(label="Medium Opacity (60%)", command=lambda: self.set_opacity(0.6))
        view_menu.add_command(label="Low Opacity (40%)", command=lambda: self.set_opacity(0.4))
        view_menu.add_separator()
        view_menu.add_command(label="Custom Opacity...", command=self.show_custom_opacity_dialog)
        menubar.add_cascade(label="View", menu=view_menu)
        
        self.root.config(menu=menubar)
    
    def create_opacity_control(self):
        """Create opacity slider control in the UI"""
        opacity_frame = ttk.Frame(self.side_frame)
        opacity_frame.grid(row=2, column=0, sticky="se", pady=5)
        
        ttk.Label(opacity_frame, text="Opacity:").pack(side="left", padx=5)
        
        self.opacity_slider = ttk.Scale(
            opacity_frame, 
            from_=0.2, 
            to=1.0, 
            value=self.opacity,
            command=self.on_opacity_change
        )
        self.opacity_slider.pack(side="left", padx=5)
        
        self.opacity_label = ttk.Label(opacity_frame, text=f"{int(self.opacity*100)}%")
        self.opacity_label.pack(side="left", padx=5)
    
    def on_opacity_change(self, value):
        """Handle opacity slider changes"""
        try:
            self.opacity = float(value)
            self.root.attributes("-alpha", self.opacity)
            self.opacity_label.config(text=f"{int(self.opacity*100)}%")
        except Exception as e:
            print(f"Error changing opacity: {e}")
    
    def set_opacity(self, value):
        """Set opacity to a specific value"""
        try:
            self.opacity = float(value)
            self.root.attributes("-alpha", self.opacity)
            self.opacity_slider.set(value)
            self.opacity_label.config(text=f"{int(self.opacity*100)}%")
        except Exception as e:
            print(f"Error setting opacity: {e}")
    
    def show_custom_opacity_dialog(self):
        """Show dialog for custom opacity input"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Custom Opacity")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter opacity (20-100%):").pack(padx=10, pady=5)
        
        entry = ttk.Entry(dialog)
        entry.pack(padx=10, pady=5)
        entry.insert(0, str(int(self.opacity*100)))
        
        def apply_opacity():
            try:
                value = int(entry.get())
                if 20 <= value <= 100:
                    self.set_opacity(value/100)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Please enter a value between 20 and 100")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Apply", command=apply_opacity).pack(side="left", padx=5)
    
    def create_task_entry_widgets(self):
        """Create widgets for adding new tasks"""
        entry_frame = ttk.Frame(self.task_frame)
        entry_frame.grid(row=0, column=0, sticky="ew", pady=5)
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Task description
        ttk.Label(entry_frame, text="Description:").grid(row=0, column=0, sticky="w")
        self.desc_entry = ttk.Entry(entry_frame)
        self.desc_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Priority
        ttk.Label(entry_frame, text="Priority:").grid(row=1, column=0, sticky="w")
        self.priority_var = tk.StringVar(value="medium")
        priority_frame = ttk.Frame(entry_frame)
        priority_frame.grid(row=1, column=1, sticky="w", padx=5)
        ttk.Radiobutton(priority_frame, text="High", variable=self.priority_var, value="high").pack(side="left")
        ttk.Radiobutton(priority_frame, text="Medium", variable=self.priority_var, value="medium").pack(side="left")
        ttk.Radiobutton(priority_frame, text="Low", variable=self.priority_var, value="low").pack(side="left")
        
        # Due date
        ttk.Label(entry_frame, text="Due Date:").grid(row=2, column=0, sticky="w")
        self.due_entry = ttk.Entry(entry_frame)
        self.due_entry.grid(row=2, column=1, sticky="ew", padx=5)
        self.due_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Add button
        add_btn = ttk.Button(entry_frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=3, column=1, sticky="e", pady=5)
    
    def create_task_list(self):
        """Create the task list with Treeview"""
        list_frame = ttk.Frame(self.task_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(list_frame, columns=("id", "description", "priority", "due_date", "created_at", "completed"), show="headings")
        
        # Define columns
        self.tree.heading("id", text="ID")
        self.tree.heading("description", text="Description")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("due_date", text="Due Date")
        self.tree.heading("created_at", text="Created")
        self.tree.heading("completed", text="Completed")
        
        # Column widths
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("description", width=200)
        self.tree.column("priority", width=80, anchor="center")
        self.tree.column("due_date", width=100, anchor="center")
        self.tree.column("created_at", width=120, anchor="center")
        self.tree.column("completed", width=80, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Action buttons
        btn_frame = ttk.Frame(self.task_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        ttk.Button(btn_frame, text="Complete", command=self.complete_task).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_task).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Clear Completed", command=self.clear_completed).pack(side="right", padx=2)
        
        # Bind double click to edit
        self.tree.bind("<Double-1>", self.edit_task)
    
    def create_smart_view(self):
        """Create the smart view panel"""
        self.smart_tree = ttk.Treeview(self.side_frame, columns=("description", "priority", "due_date"), show="headings")
        
        # Define columns
        self.smart_tree.heading("description", text="Description")
        self.smart_tree.heading("priority", text="Priority")
        self.smart_tree.heading("due_date", text="Due Date")
        
        # Column widths
        self.smart_tree.column("description", width=200)
        self.smart_tree.column("priority", width=80, anchor="center")
        self.smart_tree.column("due_date", width=100, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.side_frame, orient="vertical", command=self.smart_tree.yview)
        self.smart_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.smart_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Stats frame
        stats_frame = ttk.Frame(self.side_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.smart_stats_label = ttk.Label(stats_frame, text="", font=self.title_font)
        self.smart_stats_label.pack(side="left")
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                tasks = json.load(f)
                # Convert string dates to datetime objects for sorting
                for task in tasks:
                    if 'created_at' in task:
                        try:
                            task['created_at_dt'] = datetime.strptime(task['created_at'], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            task['created_at_dt'] = datetime.now()
                    if 'due_date' in task and task['due_date']:
                        try:
                            task['due_date_dt'] = datetime.strptime(task['due_date'], "%Y-%m-%d")
                        except ValueError:
                            task['due_date'] = ""
                return tasks
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        # Remove datetime objects before saving
        save_tasks = []
        for task in self.tasks:
            save_task = task.copy()
            if 'created_at_dt' in save_task:
                del save_task['created_at_dt']
            if 'due_date_dt' in save_task:
                del save_task['due_date_dt']
            save_tasks.append(save_task)
        
        with open(self.data_file, 'w') as f:
            json.dump(save_tasks, f, indent=2)
    
    def add_task(self):
        """Add a new task"""
        description = self.desc_entry.get().strip()
        if not description:
            messagebox.showerror("Error", "Task description cannot be empty")
            return
        
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "priority": self.priority_var.get(),
            "due_date": self.due_entry.get().strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_at_dt": datetime.now(),
            "completed": False
        }
        
        if task["due_date"]:
            try:
                task["due_date_dt"] = datetime.strptime(task["due_date"], "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        
        self.tasks.append(task)
        self.save_tasks()
        self.update_task_list()
        self.update_smart_view()
        self.update_stats()
        
        # Clear entry fields
        self.desc_entry.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.due_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def complete_task(self):
        """Mark selected task as completed"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to complete")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_tasks()
                self.update_task_list()
                self.update_smart_view()
                self.update_stats()
                break
    
    def delete_task(self):
        """Delete selected task"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()
        self.update_task_list()
        self.update_smart_view()
        self.update_stats()
    
    def clear_completed(self):
        """Remove all completed tasks"""
        initial_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task["completed"]]
        removed = initial_count - len(self.tasks)
        self.save_tasks()
        self.update_task_list()
        self.update_smart_view()
        self.update_stats()
        messagebox.showinfo("Info", f"Removed {removed} completed tasks")
    
    def edit_task(self, event):
        """Edit task on double click"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        
        # Find the task
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Task")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Task description
        ttk.Label(edit_dialog, text="Description:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        desc_entry = ttk.Entry(edit_dialog)
        desc_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        desc_entry.insert(0, task["description"])
        
        # Priority
        ttk.Label(edit_dialog, text="Priority:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        priority_var = tk.StringVar(value=task["priority"])
        priority_frame = ttk.Frame(edit_dialog)
        priority_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(priority_frame, text="High", variable=priority_var, value="high").pack(side="left")
        ttk.Radiobutton(priority_frame, text="Medium", variable=priority_var, value="medium").pack(side="left")
        ttk.Radiobutton(priority_frame, text="Low", variable=priority_var, value="low").pack(side="left")
        
        # Due date
        ttk.Label(edit_dialog, text="Due Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        due_entry = ttk.Entry(edit_dialog)
        due_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        due_entry.insert(0, task["due_date"] if task["due_date"] else "")
        
        # Save button
        def save_changes():
            task["description"] = desc_entry.get().strip()
            task["priority"] = priority_var.get()
            
            new_due_date = due_entry.get().strip()
            if new_due_date:
                try:
                    task["due_date_dt"] = datetime.strptime(new_due_date, "%Y-%m-%d")
                    task["due_date"] = new_due_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                    return
            else:
                task["due_date"] = ""
                if "due_date_dt" in task:
                    del task["due_date_dt"]
            
            self.save_tasks()
            self.update_task_list()
            self.update_smart_view()
            edit_dialog.destroy()
        
        ttk.Button(edit_dialog, text="Save", command=save_changes).grid(row=3, column=1, sticky="e", padx=5, pady=5)
    
    def update_task_list(self):
        """Update the main task list"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add tasks to the treeview
        for task in self.tasks:
            completed = "Yes" if task["completed"] else "No"
            self.tree.insert("", "end", values=(
                task["id"],
                task["description"],
                task["priority"].capitalize(),
                task["due_date"] if task["due_date"] else "-",
                task["created_at"],
                completed
            ))
    
    def update_smart_view(self):
        """Update the smart view with weighted sorting"""
        # Clear current items
        for item in self.smart_tree.get_children():
            self.smart_tree.delete(item)
        
        # Filter out completed tasks
        pending_tasks = [task for task in self.tasks if not task["completed"]]
        
        if not pending_tasks:
            self.smart_stats_label.config(text="No pending tasks")
            return
        
        # Calculate weights for sorting
        today = datetime.now().date()
        
        for task in pending_tasks:
            # Priority weight (50%)
            if task["priority"] == "high":
                priority_weight = 3
            elif task["priority"] == "medium":
                priority_weight = 2
            else:
                priority_weight = 1
            
            # Due date weight (25%)
            if "due_date_dt" in task:
                days_until_due = (task["due_date_dt"].date() - today).days
                if days_until_due < 0:  # Overdue
                    due_weight = 3
                elif days_until_due == 0:  # Due today
                    due_weight = 2
                else:  # Future due date
                    due_weight = 1
            else:
                due_weight = 0  # No due date
            
            # Creation time weight (25%) - newer tasks get higher priority
            created_today = task["created_at_dt"].date() == today
            creation_weight = 1 if created_today else 0
            
            # Combined score
            task["sort_score"] = (
                0.5 * priority_weight + 
                0.25 * due_weight + 
                0.25 * creation_weight
            )
        
        # Sort by the calculated score (descending)
        pending_tasks.sort(key=lambda x: x["sort_score"], reverse=True)
        
        # Add to smart view
        for task in pending_tasks:
            self.smart_tree.insert("", "end", values=(
                task["description"],
                task["priority"].capitalize(),
                task["due_date"] if task["due_date"] else "-"
            ))
        
        # Update stats
        total_pending = len(pending_tasks)
        overdue = sum(1 for t in pending_tasks if "due_date_dt" in t and t["due_date_dt"].date() < today)
        due_today = sum(1 for t in pending_tasks if "due_date_dt" in t and t["due_date_dt"].date() == today)
        
        stats_text = f"Pending: {total_pending} | Overdue: {overdue} | Due today: {due_today}"
        self.smart_stats_label.config(text=stats_text)
    
    def update_stats(self):
        """Update the statistics display"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["completed"])
        pending = total - completed
        
        if total > 0:
            completion_rate = (completed / total) * 100
            stats_text = f"Total: {total} | Completed: {completed} | Pending: {pending} | Completion: {completion_rate:.1f}%"
        else:
            stats_text = "No tasks yet"
        
        self.stats_label.config(text=stats_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()