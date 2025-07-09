#!/usr/bin/env python3
"""
DevEnvOps Container and Image Information Dialog
Shows detailed information about containers and images for DevEnvOps
"""

import tkinter as tk
from tkinter import ttk
import threading

class ContainerImageInfoDialog:
    """Dialog to show container and image information"""
    
    def __init__(self, parent, manager, env_key):
        self.manager = manager
        self.env_key = env_key
        self.env = manager.environments[env_key]
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Container & Image Info - {self.env['name']}")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
        self.load_info()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"📋 {self.env['name']} - Container & Image Info", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Container info frame
        container_frame = ttk.LabelFrame(main_frame, text="🐳 Container Information", padding="10")
        container_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        container_frame.columnconfigure(1, weight=1)
        
        # Container info labels
        self.container_labels = {}
        container_fields = ["Name", "Status", "Image", "Created", "Ports"]
        for i, field in enumerate(container_fields):
            ttk.Label(container_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.container_labels[field] = ttk.Label(container_frame, text="Loading...")
            self.container_labels[field].grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Image info frame
        image_frame = ttk.LabelFrame(main_frame, text="🖼️ Image Information", padding="10")
        image_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        # Image info labels
        self.image_labels = {}
        image_fields = ["Name", "ID", "Size", "Created", "Exists"]
        for i, field in enumerate(image_fields):
            ttk.Label(image_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.image_labels[field] = ttk.Label(image_frame, text="Loading...")
            self.image_labels[field].grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(20, 0))
        
        # Refresh button
        self.refresh_btn = ttk.Button(button_frame, text="🔄 Refresh", command=self.load_info)
        self.refresh_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(button_frame, text="Close", command=self.dialog.destroy)
        close_btn.grid(row=0, column=1)
        
        # Bind escape key to close
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def load_info(self):
        """Load container and image information"""
        def load_worker():
            try:
                # Get container info
                container_info = self.manager.get_container_info(self.env["container"])
                
                # Get image info
                image_info = self.manager.get_image_info(self.env["image"])
                
                # Update UI in main thread
                self.dialog.after(0, lambda: self.update_container_info(container_info))
                self.dialog.after(0, lambda: self.update_image_info(image_info))
                
            except Exception as e:
                # Show error in main thread
                self.dialog.after(0, lambda: self.show_error(str(e)))
        
        # Run in background thread
        thread = threading.Thread(target=load_worker)
        thread.daemon = True
        thread.start()
    
    def update_container_info(self, info):
        """Update container information display"""
        self.container_labels["Name"].config(text=self.env["container"])
        self.container_labels["Status"].config(text=info["status"])
        self.container_labels["Image"].config(text=info["image"])
        self.container_labels["Created"].config(text=info["created"])
        self.container_labels["Ports"].config(text=info["ports"])
        
        # Update status color
        if info["status"] == "running":
            self.container_labels["Status"].config(foreground="green")
        elif info["status"] == "stopped":
            self.container_labels["Status"].config(foreground="red")
        else:
            self.container_labels["Status"].config(foreground="orange")
    
    def update_image_info(self, info):
        """Update image information display"""
        self.image_labels["Name"].config(text=self.env["image"])
        self.image_labels["ID"].config(text=info["id"])
        self.image_labels["Size"].config(text=info["size"])
        self.image_labels["Created"].config(text=info["created"])
        self.image_labels["Exists"].config(text="Yes" if info["exists"] else "No")
        
        # Update exists color
        if info["exists"]:
            self.image_labels["Exists"].config(foreground="green")
        else:
            self.image_labels["Exists"].config(foreground="red")
    
    def show_error(self, error_msg):
        """Show error message"""
        for labels in [self.container_labels, self.image_labels]:
            for label in labels.values():
                label.config(text=f"Error: {error_msg}")
