#!/usr/bin/env python3
import os
import stat
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

class BinlyManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Binly (~/.local/bin)")
        self.root.geometry("1100x750")

        self.BIN_DIR = os.path.expanduser("~/.local/bin")
        os.makedirs(self.BIN_DIR, exist_ok=True)

        # Nomes específicos para ignorar na listagem
        self.IGNORED_NAMES = ["binly", "binly.py"]
        
        self.current_file = None 
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.pack(fill="both", expand=True)

        # --- LEFT SIDE: LIST AND CONTROLS ---
        self.left_frame = tk.Frame(self.paned, padx=10, pady=10)
        self.paned.add(self.left_frame, width=320)

        tk.Label(self.left_frame, text="Registered Commands", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.ent_search = tk.Entry(self.left_frame)
        self.ent_search.pack(fill="x", pady=5)
        self.ent_search.insert(0, "Search...")
        self.ent_search.bind("<FocusIn>", lambda e: self.ent_search.delete(0, tk.END))
        self.ent_search.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.lb_commands = tk.Listbox(self.left_frame, font=("Monospace", 10))
        self.lb_commands.pack(fill="both", expand=True, pady=5)
        self.lb_commands.bind("<<ListboxSelect>>", self.load_for_editing)

        # Quick Action Buttons
        tk.Button(self.left_frame, text="➕ New Command (Auto/Manual)", bg="#cce5ff", font=("Arial", 9, "bold"),
                  command=self.open_creation_wizard).pack(fill="x", pady=5)
        
        self.btn_activate = tk.Button(self.left_frame, text="✅ Activate (chmod +x)", bg="#d4edda", 
                                      command=lambda: self.set_executable(True), state=tk.DISABLED)
        self.btn_activate.pack(fill="x", pady=2)

        self.btn_deactivate = tk.Button(self.left_frame, text="🚫 Deactivate (remove x)", bg="#f8d7da", 
                                        command=lambda: self.set_executable(False), state=tk.DISABLED)
        self.btn_deactivate.pack(fill="x", pady=2)
        
        tk.Button(self.left_frame, text="🗑️ Remove Selected", 
                  command=self.remove_command).pack(fill="x", pady=(10, 2))
        
        tk.Button(self.left_frame, text="🔄 Refresh List", 
                  command=self.refresh_list).pack(fill="x", pady=2)

        # --- RIGHT SIDE: EDITOR ---
        self.right_frame = tk.Frame(self.paned, padx=10, pady=10)
        self.paned.add(self.right_frame)

        header_frame = tk.Frame(self.right_frame)
        header_frame.pack(fill="x")

        self.lbl_status = tk.Label(header_frame, text="No file selected", fg="gray", font=("Arial", 9, "bold"))
        self.lbl_status.pack(side="left")

        self.btn_save = tk.Button(header_frame, text="💾 SAVE CHANGES", bg="#28a745", fg="white", 
                                  font=("Arial", 9, "bold"), state=tk.DISABLED, command=self.save_current_content)
        self.btn_save.pack(side="right")

        self.txt_content = tk.Text(self.right_frame, font=("Monospace", 11), undo=True, wrap="none")
        self.txt_content.pack(fill="both", expand=True, pady=5)

    def refresh_list(self):
        search_term = self.ent_search.get().lower()
        if search_term == "search...": search_term = ""
        
        self.lb_commands.delete(0, tk.END)
        for name in sorted(os.listdir(self.BIN_DIR)):
            # Ignora especificamente o nome do binário binly
            if name in self.IGNORED_NAMES:
                continue
                
            if os.path.isfile(os.path.join(self.BIN_DIR, name)):
                if search_term in name.lower():
                    self.lb_commands.insert(tk.END, name)

    def load_for_editing(self, event=None):
        sel = self.lb_commands.curselection()
        if not sel: return
        
        name = self.lb_commands.get(sel[0])
        full_path = os.path.join(self.BIN_DIR, name)
        
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            self.current_file = name
            self.txt_content.delete("1.0", tk.END)
            self.txt_content.insert(tk.END, content)
            
            self.update_ui_state(full_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")

    def update_ui_state(self, path):
        """Updates buttons and labels based on file state"""
        is_exec = os.access(path, os.X_OK)
        status_text = f"File: {self.current_file} | Executable: {'YES' if is_exec else 'NO'}"
        color = "#155724" if is_exec else "#721c24"
        
        self.lbl_status.config(text=status_text, fg=color)
        self.btn_save.config(state=tk.NORMAL)
        self.btn_activate.config(state=tk.NORMAL)
        self.btn_deactivate.config(state=tk.NORMAL)

    def set_executable(self, make_exec):
        if not self.current_file: return
        full_path = os.path.join(self.BIN_DIR, self.current_file)
        try:
            st = os.stat(full_path).st_mode
            if make_exec:
                os.chmod(full_path, st | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            else:
                os.chmod(full_path, st & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            self.update_ui_state(full_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_current_content(self):
        if not self.current_file: return
        full_path = os.path.join(self.BIN_DIR, self.current_file)
        try:
            content = self.txt_content.get("1.0", tk.END + "-1c")
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Success", f"Content of '{self.current_file}' updated!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_command(self):
        if not self.current_file: return
        if messagebox.askyesno("Confirm", f"Delete '{self.current_file}'?"):
            os.remove(os.path.join(self.BIN_DIR, self.current_file))
            self.current_file = None
            self.txt_content.delete("1.0", tk.END)
            self.lbl_status.config(text="Select a command", fg="gray")
            self.btn_save.config(state=tk.DISABLED)
            self.btn_activate.config(state=tk.DISABLED)
            self.btn_deactivate.config(state=tk.DISABLED)
            self.refresh_list()

    def open_creation_wizard(self):
        win = tk.Toplevel(self.root)
        win.title("Create New Command")
        win.geometry("600x480")
        win.grab_set()

        tabs = ttk.Notebook(win)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # AUTO TAB
        tab_auto = tk.Frame(tabs, padx=10, pady=10)
        tabs.add(tab_auto, text="Automatic")
        tk.Label(tab_auto, text="Command name:").pack(anchor="w")
        ent_name_auto = tk.Entry(tab_auto)
        ent_name_auto.pack(fill="x", pady=5)
        
        tk.Label(tab_auto, text="Target File:").pack(anchor="w")
        pf = tk.Frame(tab_auto); pf.pack(fill="x")
        ent_path = tk.Entry(pf); ent_path.pack(side="left", fill="x", expand=True)
        
        def browse():
            p = filedialog.askopenfilename()
            if p:
                ent_path.delete(0, tk.END); ent_path.insert(0, p)
                if not ent_name_auto.get():
                    ent_name_auto.insert(0, os.path.splitext(os.path.basename(p))[0].lower())
        tk.Button(pf, text="...", command=browse).pack(side="right")

        def save_auto():
            name = ent_name_auto.get().strip()
            path = ent_path.get().strip()
            if not name or not path: 
                return
            content = f'#!/bin/bash\n"{path}" "$@"'
            self.write_new_file(name, content, win)
            
        tk.Button(tab_auto, text="Create Command", bg="#28a745", fg="white", command=save_auto).pack(pady=20)

        # MANUAL TAB
        tab_manual = tk.Frame(tabs, padx=10, pady=10)
        tabs.add(tab_manual, text="Manual")
        tk.Label(tab_manual, text="Name:").pack(anchor="w")
        ent_name_man = tk.Entry(tab_manual); ent_name_man.pack(fill="x", pady=5)
        txt_man = tk.Text(tab_manual, height=10, font=("Monospace", 10))
        txt_man.insert("1.0", "#!/bin/bash\n\n"); txt_man.pack(fill="both", expand=True)
        
        def save_manual():
            name = ent_name_man.get().strip()
            if name: 
                self.write_new_file(name, txt_man.get("1.0", tk.END + "-1c"), win)
                
        tk.Button(tab_manual, text="Create Manually", bg="#007bff", fg="white", command=save_manual).pack(pady=10)

    def write_new_file(self, name, content, window):
        full_path = os.path.join(self.BIN_DIR, name)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.chmod(full_path, os.stat(full_path).st_mode | stat.S_IXUSR)
            window.destroy()
            self.refresh_list()
            messagebox.showinfo("Success", f"Command '{name}' created!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not write file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "clam" in style.theme_names(): style.theme_use("clam")
    app = BinlyManager(root)
    root.mainloop()