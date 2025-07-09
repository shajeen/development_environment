#!/usr/bin/env python3
"""
Docker Development Environment Manager - GUI Application
A graphical interface to manage Docker-based development environments
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import subprocess
import threading
import queue
import os
from pathlib import Path
from src.core.docker_manager import DockerEnvironmentManager
from src.gui.gui_dialogs import EditEnvironmentDialog, CloneEnvironmentDialog
from src.gui.container_image_info_dialog import ContainerImageInfoDialog

class DockerManagerGUI:
    """GUI for Docker Environment Manager"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Docker Development Environment Manager")
        self.root.geometry("900x700")
        
        # Initialize manager
        self.manager = DockerEnvironmentManager()
        
        # Create queue for thread communication
        self.output_queue = queue.Queue()
        
        # Status cache to improve performance
        self.status_cache = {}
        self.last_status_check = 0
        
        # Setup UI
        self.setup_ui()
        
        # Start output processor
        self.process_output()
        
        # Initial refresh - delayed to improve startup time
        self.root.after(100, self.refresh_status)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🐳 Docker Development Environment Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Environment selection
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Docker environments
        docker_frame = ttk.LabelFrame(left_frame, text="🐳 Docker Compose Environments", padding="10")
        docker_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        self.docker_listbox = tk.Listbox(docker_frame, height=4)
        self.docker_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.docker_listbox.bind('<<ListboxSelect>>', self.on_docker_select)
        
        # Scrollbar for docker listbox
        docker_scrollbar = ttk.Scrollbar(docker_frame, orient=tk.VERTICAL, command=self.docker_listbox.yview)
        docker_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.docker_listbox.configure(yscrollcommand=docker_scrollbar.set)
        
        docker_frame.columnconfigure(0, weight=1)
        docker_frame.rowconfigure(0, weight=1)
        
        # Vagrant environments
        vagrant_frame = ttk.LabelFrame(left_frame, text="🗺️ Vagrant Environments", padding="10")
        vagrant_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        self.vagrant_listbox = tk.Listbox(vagrant_frame, height=4)
        self.vagrant_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.vagrant_listbox.bind('<<ListboxSelect>>', self.on_vagrant_select)
        
        # Scrollbar for vagrant listbox
        vagrant_scrollbar = ttk.Scrollbar(vagrant_frame, orient=tk.VERTICAL, command=self.vagrant_listbox.yview)
        vagrant_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.vagrant_listbox.configure(yscrollcommand=vagrant_scrollbar.set)
        
        vagrant_frame.columnconfigure(0, weight=1)
        vagrant_frame.rowconfigure(0, weight=1)
        
        # Right panel - Controls and info
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        
        # Environment info
        info_frame = ttk.LabelFrame(right_frame, text="Environment Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Info labels
        self.info_labels = {}
        info_fields = ["Name", "Type", "Status", "Port", "Container", "Image", "Volume", "SSH Command", "Credentials", "Description"]
        for i, field in enumerate(info_fields):
            ttk.Label(info_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            self.info_labels[field] = ttk.Label(info_frame, text="N/A")
            self.info_labels[field].grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
            # Make description label wrap text
            if field == "Description":
                self.info_labels[field].config(wraplength=300)
        
        # Control buttons
        control_frame = ttk.LabelFrame(right_frame, text="Actions", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button configuration
        button_config = {"width": 12, "padding": 5}
        
        # Row 1 buttons
        button_frame1 = ttk.Frame(control_frame)
        button_frame1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.build_btn = ttk.Button(button_frame1, text="🔨 Build", command=self.build_environment, **button_config)
        self.build_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.start_btn = ttk.Button(button_frame1, text="🚀 Start", command=self.start_environment, **button_config)
        self.start_btn.grid(row=0, column=1, padx=5)
        
        self.stop_btn = ttk.Button(button_frame1, text="🛑 Stop", command=self.stop_environment, **button_config)
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        # Row 2 buttons
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.restart_btn = ttk.Button(button_frame2, text="🔄 Restart", command=self.restart_environment, **button_config)
        self.restart_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.clear_btn = ttk.Button(button_frame2, text="🧹 Clear", command=self.clear_environment, **button_config)
        self.clear_btn.grid(row=0, column=1, padx=5)
        
        self.ssh_btn = ttk.Button(button_frame2, text="🔌 SSH", command=self.ssh_connect, **button_config)
        self.ssh_btn.grid(row=0, column=2, padx=5)
        
        # Row 3 buttons - Edit and Clone
        button_frame3 = ttk.Frame(control_frame)
        button_frame3.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.edit_btn = ttk.Button(button_frame3, text="✏️ Edit", command=self.edit_environment, **button_config)
        self.edit_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.clone_btn = ttk.Button(button_frame3, text="📋 Clone", command=self.clone_environment, **button_config)
        self.clone_btn.grid(row=0, column=1, padx=5)
        
        self.info_btn = ttk.Button(button_frame3, text="ℹ️ Info", command=self.show_container_image_info, **button_config)
        self.info_btn.grid(row=0, column=2, padx=5)
        
        # Row 4 buttons - Delete
        button_frame4 = ttk.Frame(control_frame)
        button_frame4.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.delete_btn = ttk.Button(button_frame4, text="🗑️ Delete", command=self.delete_environment, **button_config)
        self.delete_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Options frame
        options_frame = ttk.LabelFrame(right_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.no_cache_var = tk.BooleanVar()
        self.no_cache_cb = ttk.Checkbutton(options_frame, text="No Cache (Build)", variable=self.no_cache_var)
        self.no_cache_cb.grid(row=0, column=0, sticky=tk.W)
        
        self.remove_volumes_var = tk.BooleanVar()
        self.remove_volumes_cb = ttk.Checkbutton(options_frame, text="Remove Volumes (Clear)", variable=self.remove_volumes_var)
        self.remove_volumes_cb.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        self.remove_images_var = tk.BooleanVar()
        self.remove_images_cb = ttk.Checkbutton(options_frame, text="Remove Images (Delete)", variable=self.remove_images_var)
        self.remove_images_cb.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.delete_volumes_var = tk.BooleanVar()
        self.delete_volumes_cb = ttk.Checkbutton(options_frame, text="Remove Volumes (Delete)", variable=self.delete_volumes_var)
        self.delete_volumes_cb.grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(right_frame, text="🔄 Refresh Status", command=self.manual_refresh)
        refresh_btn.grid(row=3, column=0, pady=5)
        
        # Output panel
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, state=tk.DISABLED)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear output button
        clear_output_btn = ttk.Button(output_frame, text="Clear Output", command=self.clear_output)
        clear_output_btn.grid(row=1, column=0, pady=(5, 0))
        
        # Initialize environment list
        self.populate_environment_list()
        
        # Initially disable buttons
        self.set_buttons_state(False)
    
    def populate_environment_list(self):
        """Populate the environment listboxes"""
        self.docker_listbox.delete(0, tk.END)
        self.vagrant_listbox.delete(0, tk.END)
        
        # Reload environments from file
        self.manager.load_environments()
        
        for key, env in self.manager.environments.items():
            env_type = env.get("type", "docker-compose")
            if env_type == "vagrant":
                self.vagrant_listbox.insert(tk.END, f"{key} - {env['name']}")
            else:
                self.docker_listbox.insert(tk.END, f"{key} - {env['name']}")
    
    def on_docker_select(self, event):
        """Handle Docker environment selection"""
        selection = self.docker_listbox.curselection()
        if selection:
            # Clear vagrant selection
            self.vagrant_listbox.selection_clear(0, tk.END)
            
            listbox_item = self.docker_listbox.get(selection[0])
            env_key = listbox_item.split(' - ')[0]
            self.selected_env = env_key
            # Update info in background thread to avoid blocking UI
            self.root.after(50, lambda: self.update_environment_info(env_key))
            self.set_buttons_state(True)
    
    def on_vagrant_select(self, event):
        """Handle Vagrant environment selection"""
        selection = self.vagrant_listbox.curselection()
        if selection:
            # Clear docker selection
            self.docker_listbox.selection_clear(0, tk.END)
            
            listbox_item = self.vagrant_listbox.get(selection[0])
            env_key = listbox_item.split(' - ')[0]
            self.selected_env = env_key
            # Update info in background thread to avoid blocking UI
            self.root.after(50, lambda: self.update_environment_info(env_key))
            self.set_buttons_state(True)
    
    def update_environment_info(self, env_key):
        """Update environment information display"""
        if env_key not in self.manager.environments:
            return
        
        env = self.manager.environments[env_key]
        env_type = env.get("type", "docker-compose")
        env_path = str(self.manager.base_path / env["path"]) if env_type == "vagrant" else None
        
        # Use cached status if available and recent (< 3 seconds)
        import time
        current_time = time.time()
        cache_key = f"{env_key}_{env_type}"
        
        if (cache_key in self.status_cache and 
            current_time - self.status_cache[cache_key]['timestamp'] < 3):
            status = self.status_cache[cache_key]['status']
        else:
            status = self.manager.get_container_status(env["container"], env_type, env_path)
            self.status_cache[cache_key] = {'status': status, 'timestamp': current_time}
        
        # Update info labels
        self.info_labels["Name"].config(text=env["name"])
        self.info_labels["Type"].config(text=f"🗺 Vagrant" if env_type == "vagrant" else "🐳 Docker Compose")
        self.info_labels["Status"].config(text=status)
        self.info_labels["Port"].config(text=str(env["port"]))
        self.info_labels["Container"].config(text=env["container"])
        self.info_labels["Image"].config(text=env["image"])
        self.info_labels["Volume"].config(text=env.get("volume", "N/A"))
        self.info_labels["Description"].config(text=env.get("description", "No description available"))
        
        # Update SSH command based on environment type
        if env_type == "vagrant":
            ssh_user = env.get("ssh_user", "root")
            ssh_cmd = f"ssh {ssh_user}@localhost -p {env['port']}"
            if env.get("ssh_key"):
                credentials = f"SSH Key: {env['ssh_key']}"
            else:
                credentials = "SSH Key required"
            
            # Add VNC info if available
            if env.get("vnc_port"):
                ssh_cmd += f" | VNC: 127.0.0.1:{env['vnc_port']}"
            
            # Add GPU info if available
            if env.get("gpu_support"):
                credentials += " | GPU: Enabled"
        else:
            ssh_cmd = f"ssh dev@localhost -p {env['port']}"
            credentials = "dev / devpass"
        
        self.info_labels["SSH Command"].config(text=ssh_cmd)
        self.info_labels["Credentials"].config(text=credentials)
        
        # Update status color
        if status == "running":
            self.info_labels["Status"].config(foreground="green")
        elif status == "stopped":
            self.info_labels["Status"].config(foreground="red")
        else:
            self.info_labels["Status"].config(foreground="orange")
        
        # Update type color
        if env_type == "vagrant":
            self.info_labels["Type"].config(foreground="blue")
        else:
            self.info_labels["Type"].config(foreground="darkgreen")
    
    def set_buttons_state(self, enabled):
        """Enable or disable control buttons"""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in [self.build_btn, self.start_btn, self.stop_btn, 
                   self.restart_btn, self.clear_btn, self.ssh_btn,
                   self.edit_btn, self.info_btn, self.delete_btn]:
            btn.config(state=state)
        
        # Clone button is always enabled
        self.clone_btn.config(state=tk.NORMAL)
    
    def append_output(self, text):
        """Append text to output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def clear_output(self):
        """Clear the output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def run_command_threaded(self, command_func, *args):
        """Run a command in a separate thread"""
        def worker():
            try:
                result = command_func(*args)
                # Clear cache and refresh
                self.status_cache.clear()
                self.output_queue.put(("refresh", None))
                return result
            except Exception as e:
                self.output_queue.put(("error", str(e)))
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
    
    def process_output(self):
        """Process output from background threads"""
        try:
            while True:
                msg_type, data = self.output_queue.get_nowait()
                if msg_type == "refresh":
                    self.refresh_status()
                elif msg_type == "error":
                    messagebox.showerror("Error", data)
                elif msg_type == "output":
                    self.append_output(data)
                elif msg_type == "populate":
                    self.populate_environment_list()
                elif msg_type == "clear_selection":
                    self.clear_selection()
        except queue.Empty:
            pass
        
        # Schedule next check - reduce frequency to improve performance
        self.root.after(500, self.process_output)
    
    def refresh_status(self):
        """Refresh the status of all environments"""
        # Clear status cache to force fresh status check
        self.status_cache.clear()
        if hasattr(self, 'selected_env'):
            self.update_environment_info(self.selected_env)
    
    def manual_refresh(self):
        """Manual refresh triggered by user"""
        self.append_output("🔄 Refreshing environment status...")
        self.refresh_status()
        self.append_output("✅ Status refreshed!")
    
    def clear_selection(self):
        """Clear the current environment selection"""
        self.docker_listbox.selection_clear(0, tk.END)
        self.vagrant_listbox.selection_clear(0, tk.END)
        if hasattr(self, 'selected_env'):
            delattr(self, 'selected_env')
        self.set_buttons_state(False)
        # Clear info labels
        for label in self.info_labels.values():
            label.config(text="N/A")
            label.config(foreground="black")
    
    def build_environment(self):
        """Build selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        self.append_output(f"Building {self.selected_env} environment...")
        
        def build_worker():
            success = self.manager.build_environment(self.selected_env, self.no_cache_var.get())
            status = "✅ Build completed successfully!" if success else "❌ Build failed!"
            self.output_queue.put(("output", status))
            # Clear cache and refresh
            self.status_cache.clear()
            self.output_queue.put(("refresh", None))
        
        thread = threading.Thread(target=build_worker)
        thread.daemon = True
        thread.start()
    
    def start_environment(self):
        """Start selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        self.append_output(f"Starting {self.selected_env} environment...")
        
        def start_worker():
            success = self.manager.start_environment(self.selected_env)
            if success:
                env = self.manager.environments[self.selected_env]
                env_type = env.get("type", "docker-compose")
                self.output_queue.put(("output", f"✅ {self.selected_env} started successfully!"))
                
                if env_type == "vagrant":
                    ssh_user = env.get("ssh_user", "root")
                    self.output_queue.put(("output", f"📡 SSH: ssh {ssh_user}@localhost -p {env['port']}"))
                    if env.get("ssh_key"):
                        self.output_queue.put(("output", f"🔑 SSH Key: {env['ssh_key']}"))
                    if env.get("vnc_port"):
                        self.output_queue.put(("output", f"🗺 VNC: Connect to 127.0.0.1:{env['vnc_port']}"))
                else:
                    self.output_queue.put(("output", f"📡 SSH: ssh dev@localhost -p {env['port']}"))
                    self.output_queue.put(("output", f"🔑 Credentials: dev / devpass"))
            else:
                self.output_queue.put(("output", f"❌ Failed to start {self.selected_env} environment!"))
            # Clear cache and refresh
            self.status_cache.clear()
            self.output_queue.put(("refresh", None))
        
        thread = threading.Thread(target=start_worker)
        thread.daemon = True
        thread.start()
    
    def stop_environment(self):
        """Stop selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        self.append_output(f"Stopping {self.selected_env} environment...")
        self.run_command_threaded(self.manager.stop_environment, self.selected_env)
    
    def restart_environment(self):
        """Restart selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        self.append_output(f"🔄 Restarting {self.selected_env} environment...")
        
        def restart_worker():
            # Stop the environment first
            self.append_output(f"🛑 Stopping {self.selected_env} environment...")
            stop_success = self.manager.stop_environment(self.selected_env)
            if stop_success:
                self.append_output(f"✅ {self.selected_env} stopped successfully!")
            
            # Start the environment
            self.append_output(f"🚀 Starting {self.selected_env} environment...")
            start_success = self.manager.start_environment(self.selected_env)
            if start_success:
                env = self.manager.environments[self.selected_env]
                env_type = env.get("type", "docker-compose")
                self.append_output(f"✅ {self.selected_env} started successfully!")
                
                if env_type == "vagrant":
                    ssh_user = env.get("ssh_user", "root")
                    self.append_output(f"📡 SSH: ssh {ssh_user}@localhost -p {env['port']}")
                    if env.get("ssh_key"):
                        self.append_output(f"🔑 SSH Key: {env['ssh_key']}")
                    if env.get("vnc_port"):
                        self.append_output(f"🗺 VNC: Connect to 127.0.0.1:{env['vnc_port']}")
                else:
                    self.append_output(f"📡 SSH: ssh dev@localhost -p {env['port']}")
                    self.append_output(f"🔑 Credentials: dev / devpass")
            else:
                self.append_output(f"❌ Failed to start {self.selected_env} environment!")
            
            # Clear cache and refresh
            self.status_cache.clear()
            self.output_queue.put(("refresh", None))
        
        thread = threading.Thread(target=restart_worker)
        thread.daemon = True
        thread.start()
    
    def clear_environment(self):
        """Clear selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to clear the {self.selected_env} environment?"):
            self.append_output(f"Clearing {self.selected_env} environment...")
            self.run_command_threaded(self.manager.clear_environment, self.selected_env, self.remove_volumes_var.get())
    
    def ssh_connect(self):
        """Connect to selected environment via SSH"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        env = self.manager.environments[self.selected_env]
        env_type = env.get("type", "docker-compose")
        env_path = str(self.manager.base_path / env["path"]) if env_type == "vagrant" else None
        status = self.manager.get_container_status(env["container"], env_type, env_path)
        
        if status != "running":
            messagebox.showerror("Error", f"Environment {self.selected_env} is not running!\nPlease start it first.")
            return
        
        # Open SSH connection in terminal
        if env_type == "vagrant":
            ssh_user = env.get("ssh_user", "root")
            ssh_command = f"ssh {ssh_user}@localhost -p {env['port']}"
        else:
            ssh_command = f"ssh dev@localhost -p {env['port']}"
        
        try:
            # Try different terminal commands based on OS
            if os.name == 'nt':  # Windows
                os.system(f"start cmd /k {ssh_command}")
            elif os.name == 'posix':  # Linux/Mac
                # Try different terminal emulators
                terminals = ['gnome-terminal', 'xterm', 'konsole', 'terminal']
                for term in terminals:
                    if subprocess.call(['which', term], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                        os.system(f"{term} -e {ssh_command}")
                        break
                else:
                    # Fallback to current terminal
                    self.append_output(f"Run this command in your terminal: {ssh_command}")
            
            self.append_output(f"🔌 SSH connection opened: {ssh_command}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open SSH connection: {str(e)}")
    
    def edit_environment(self):
        """Edit selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        # Create edit dialog
        edit_window = EditEnvironmentDialog(self.root, self.manager, self.selected_env)
        self.root.wait_window(edit_window.dialog)
        
        if edit_window.result:
            # Refresh the environment list and info
            self.populate_environment_list()
            self.update_environment_info(self.selected_env)
            self.append_output(f"✅ Environment '{self.selected_env}' updated successfully!")
    
    def clone_environment(self):
        """Clone selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        # Create clone dialog
        clone_window = CloneEnvironmentDialog(self.root, self.manager, self.selected_env)
        self.root.wait_window(clone_window.dialog)
        
        if clone_window.result:
            # Refresh the environment list
            self.populate_environment_list()
            self.append_output(f"✅ Environment '{clone_window.new_env_key}' cloned from '{self.selected_env}'!")
    
    def show_container_image_info(self):
        """Show container and image information"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        # Create info dialog
        info_window = ContainerImageInfoDialog(self.root, self.manager, self.selected_env)
        
    def delete_environment(self):
        """Delete selected environment"""
        if not hasattr(self, 'selected_env'):
            messagebox.showwarning("Warning", "Please select an environment first")
            return
        
        # Confirm deletion
        env_name = self.manager.environments[self.selected_env]["name"]
        if not messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete the '{env_name}' environment?\n\n"
                                   f"This will permanently remove the environment configuration."):
            return
        
        self.append_output(f"🗑️ Deleting {self.selected_env} environment...")
        
        def delete_worker():
            success = self.manager.delete_environment(
                self.selected_env, 
                self.delete_volumes_var.get(),
                self.remove_images_var.get()
            )
            if success:
                self.output_queue.put(("output", f"✅ Environment '{self.selected_env}' deleted successfully!"))
                self.output_queue.put(("populate", None))  # Refresh environment list
                self.output_queue.put(("clear_selection", None))  # Clear selection
            else:
                self.output_queue.put(("output", f"❌ Failed to delete environment '{self.selected_env}'"))
        
        thread = threading.Thread(target=delete_worker)
        thread.daemon = True
        thread.start()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = DockerManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()