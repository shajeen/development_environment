#!/usr/bin/env python3
"""
GUI Dialog Classes for Docker Environment Manager
Contains edit and clone dialog implementations
"""

import tkinter as tk
from tkinter import ttk, messagebox

class EditEnvironmentDialog:
    """Dialog for editing environment configuration"""
    
    def __init__(self, parent, manager, env_key):
        self.manager = manager
        self.env_key = env_key
        self.env = manager.environments[env_key]
        self.result = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Environment: {env_key}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text=f"✏️ Edit Environment: {self.env_key}", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create entry fields
        self.entries = {}
        fields = [("name", "Display Name"), ("path", "Directory Path"), 
                 ("port", "SSH Port"), ("container", "Container Name"),
                 ("image", "Image Name"), ("volume", "Volume Name")]
        
        for i, (field, label) in enumerate(fields):
            ttk.Label(main_frame, text=f"{label}:").grid(row=i+1, column=0, sticky=tk.W, pady=5)
            
            entry = ttk.Entry(main_frame, width=40)
            entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
            entry.insert(0, str(self.env[field]))
            
            self.entries[field] = entry
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=(20, 0))
        
        save_btn = ttk.Button(button_frame, text="💾 Save", command=self.save_changes)
        save_btn.grid(row=0, column=0, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="❌ Cancel", command=self.cancel)
        cancel_btn.grid(row=0, column=1)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def save_changes(self):
        """Save the changes"""
        try:
            # Validate port
            port_value = self.entries["port"].get()
            try:
                port_int = int(port_value)
                if port_int < 1 or port_int > 65535:
                    raise ValueError("Port must be between 1 and 65535")
                
                # Check for port conflicts with other environments
                for other_key, other_env in self.manager.environments.items():
                    if other_key != self.env_key and other_env["port"] == port_int:
                        messagebox.showerror("Error", f"Port {port_int} is already used by environment '{other_key}'!")
                        return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid port: {e}")
                return
            
            # Validate path
            path_value = self.entries["path"].get().strip()
            if path_value:
                from pathlib import Path
                path_obj = self.manager.base_path / path_value
                if not path_obj.exists():
                    result = messagebox.askyesno("Path Warning", 
                        f"Path {path_obj} does not exist!\n\nContinue anyway?")
                    if not result:
                        return
            
            # Update environment
            for field, entry in self.entries.items():
                value = entry.get().strip()
                if not value:
                    messagebox.showerror("Error", f"{field.capitalize()} cannot be empty")
                    return
                
                if field == "port":
                    value = int(value)
                
                self.env[field] = value
            
            # Save to file
            self.manager.save_environments()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
    
    def cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()


class CloneEnvironmentDialog:
    """Dialog for cloning environment configuration"""
    
    def __init__(self, parent, manager, source_env):
        self.manager = manager
        self.source_env = source_env
        self.result = False
        self.new_env_key = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Clone Environment: {source_env}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text=f"📋 Clone Environment: {self.source_env}", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Source info
        source_frame = ttk.LabelFrame(main_frame, text="Source Environment", padding="10")
        source_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        source_env = self.manager.environments[self.source_env]
        ttk.Label(source_frame, text=f"Name: {source_env['name']}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(source_frame, text=f"Port: {source_env['port']}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(source_frame, text=f"Path: {source_env['path']}").grid(row=2, column=0, sticky=tk.W)
        
        # New environment settings
        new_frame = ttk.LabelFrame(main_frame, text="New Environment Settings", padding="10")
        new_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # New environment unique identifier
        ttk.Label(new_frame, text="Unique Identifier:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.key_entry = ttk.Entry(new_frame, width=30)
        self.key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # New environment name
        ttk.Label(new_frame, text="Display Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(new_frame, width=30)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.name_entry.insert(0, f"{source_env['name']} (Clone)")
        
        # New port
        ttk.Label(new_frame, text="SSH Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(new_frame, width=30)
        self.port_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Auto-suggest next available port
        used_ports = [env["port"] for env in self.manager.environments.values()]
        suggested_port = max(used_ports) + 1
        self.port_entry.insert(0, str(suggested_port))
        
        # Add helpful instruction
        instruction_frame = ttk.Frame(main_frame)
        instruction_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        instruction_label = ttk.Label(instruction_frame, 
                                     text="💡 Unique Identifier: Short name (e.g., 'my-python-dev'). Fill details and click 'Clone Environment'.",
                                     font=("Arial", 9),
                                     foreground="blue")
        instruction_label.grid(row=0, column=0, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 10), sticky=(tk.W, tk.E))
        
        # Make buttons more prominent
        self.clone_btn = ttk.Button(button_frame, text="✅ Clone Environment", command=self.clone_environment)
        self.clone_btn.grid(row=0, column=0, padx=(0, 10), pady=10, sticky=(tk.W, tk.E))
        
        cancel_btn = ttk.Button(button_frame, text="❌ Cancel", command=self.cancel)
        cancel_btn.grid(row=0, column=1, padx=(10, 0), pady=10, sticky=(tk.W, tk.E))
        
        # Configure button frame weights
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        new_frame.columnconfigure(1, weight=1)
        source_frame.columnconfigure(0, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.clone_environment())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Set focus to the unique identifier entry field
        self.key_entry.focus_set()
    
    def clone_environment(self):
        """Clone the environment"""
        try:
            # Get values
            new_key = self.key_entry.get().strip()
            new_name = self.name_entry.get().strip()
            new_port = self.port_entry.get().strip()
            
            # Validate inputs
            if not new_key:
                messagebox.showerror("Error", "Unique identifier cannot be empty")
                return
            
            if not new_name:
                messagebox.showerror("Error", "Display name cannot be empty")
                return
            
            if new_key in self.manager.environments:
                messagebox.showerror("Error", f"Unique identifier '{new_key}' already exists")
                return
            
            # Validate port
            try:
                port_int = int(new_port)
                if port_int < 1 or port_int > 65535:
                    raise ValueError("Port must be between 1 and 65535")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid port: {e}")
                return
            
            # Check if port is already used
            used_ports = [env["port"] for env in self.manager.environments.values()]
            if port_int in used_ports:
                messagebox.showerror("Error", f"Port {port_int} is already in use")
                return
            
            # Show progress (disable button during cloning)
            self.clone_btn.config(text="⏳ Cloning...", state="disabled")
            self.dialog.update()
            
            # Clone the environment
            success = self.manager.clone_environment(self.source_env, new_key, new_name, port_int)
            
            if success:
                # Show success message
                messagebox.showinfo("Success", f"Environment '{new_key}' has been successfully cloned from '{self.source_env}'!\n\nYou can now find it in the environment list.")
                self.result = True
                self.new_env_key = new_key
                self.dialog.destroy()
            else:
                # Re-enable button on failure
                self.clone_btn.config(text="✅ Clone Environment", state="normal")
                messagebox.showerror("Clone Failed", f"Failed to clone environment '{self.source_env}' to '{new_key}'.\n\nPossible causes:\n• Directory already exists\n• Permission issues\n• Invalid configuration\n\nPlease check the environment configuration and try again.")
            
        except Exception as e:
            # Re-enable button on exception
            self.clone_btn.config(text="✅ Clone Environment", state="normal")
            
            messagebox.showerror("Clone Error", f"An error occurred while cloning the environment:\n\n{str(e)}\n\nPlease try again or check the logs for more details.")
    
    def cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()