import customtkinter as ctk
import subprocess
import os
import threading
import re

class VibeEdit(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VibeEdit - CRust IDE (vibe(O)s)")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Dark")
        
        self.workspace_dir = "/tmp/vibe-workspace"
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Top Toolbar
        self.toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.toolbar.pack(side="top", fill="x")
        
        ctk.CTkLabel(self.toolbar, text="vibe(O)s", font=("Inter", 16, "bold"), text_color="#a371f7").pack(side="left", padx=20)
        
        self.btn_run = ctk.CTkButton(self.toolbar, text="▶ Build & Run Project", width=150, fg_color="#2ea043", hover_color="#238636", command=self.run_code)
        self.btn_run.pack(side="right", padx=20, pady=10)

        self.btn_find = ctk.CTkButton(self.toolbar, text="🔍 Find & Replace", width=120, command=self.open_find_replace)
        self.btn_find.pack(side="right", padx=10, pady=10)
        
        # Main Layout (Sidebar + Editor)
        self.main_paned = ctk.CTkFrame(self, fg_color="transparent")
        self.main_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sidebar (File Tree Mockup)
        self.sidebar = ctk.CTkFrame(self.main_paned, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="EXPLORER", font=("Inter", 12, "bold")).pack(anchor="w", padx=10, pady=10)
        ctk.CTkButton(self.sidebar, text="📄 main.cr", fg_color="transparent", anchor="w", command=lambda: self.tabview.set("main.cr")).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(self.sidebar, text="📄 math.cr", fg_color="transparent", anchor="w", command=lambda: self.tabview.set("math.cr")).pack(fill="x", padx=5, pady=2)
        
        # Right Side (Editor + Terminal)
        self.right_frame = ctk.CTkFrame(self.main_paned, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self.right_frame)
        self.tabview.pack(fill="both", expand=True)
        
        self.tab_main = self.tabview.add("main.cr")
        self.tab_math = self.tabview.add("math.cr")
        
        # Editor: main.cr
        self.text_main = ctk.CTkTextbox(self.tab_main, font=("JetBrains Mono", 14), wrap="none")
        self.text_main.pack(fill="both", expand=True)
        self.text_main.bind("<KeyRelease>", lambda e: self.highlight_syntax(self.text_main))
        
        code_main = """// vibe(O)s CRust Project
// Made by Gemini 3.1 Pro (so far) | Prompted by ray0ffire/minerofthesoal

import "math.cr";

struct User {
    string name;
    int age;
    bool is_admin;
}

fn main() -> int {
    let os_name = "vibe(O)s";
    
    // Using our imported math module
    let result = multiply(10, 4);
    
    // Using our new Struct feature
    User admin;
    admin.name = "ray0ffire";
    admin.age = 99;
    admin.is_admin = true;
    
    println!("Welcome to " + os_name + "!");
    println!("User: " + admin.name + " | Admin: " + to_string(admin.is_admin));
    println!("10 * 4 = " + to_string(result));
    
    return 0;
}
"""
        self.text_main.insert("1.0", code_main)
        
        # Editor: math.cr
        self.text_math = ctk.CTkTextbox(self.tab_math, font=("JetBrains Mono", 14), wrap="none")
        self.text_math.pack(fill="both", expand=True)
        self.text_math.bind("<KeyRelease>", lambda e: self.highlight_syntax(self.text_math))
        
        code_math = """// math.cr - A custom module

fn multiply(a: int, b: int) -> int {
    return a * b;
}

fn divide(a: float, b: float) -> float {
    return a / b;
}
"""
        self.text_math.insert("1.0", code_math)
        
        self.setup_tags(self.text_main)
        self.setup_tags(self.text_math)
        self.highlight_syntax(self.text_main)
        self.highlight_syntax(self.text_math)
        
        # Terminal / Output Area
        self.terminal_frame = ctk.CTkFrame(self.right_frame, height=250)
        self.terminal_frame.pack(side="bottom", fill="x", pady=(10, 0))
        self.terminal_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.terminal_frame, text="Terminal Output", font=("Inter", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.terminal = ctk.CTkTextbox(self.terminal_frame, font=("JetBrains Mono", 12), fg_color="#0d1117", text_color="#e6edf3")
        self.terminal.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def setup_tags(self, textbox):
        textbox.tag_config("keyword", foreground="#ff7b72")
        textbox.tag_config("type", foreground="#79c0ff")
        textbox.tag_config("string", foreground="#a5d6ff")
        textbox.tag_config("comment", foreground="#8b949e")
        textbox.tag_config("function", foreground="#d2a8ff")
        textbox.tag_config("number", foreground="#79c0ff")
        textbox.tag_config("search", background="#f2cc60", foreground="black")

    def highlight_syntax(self, textbox):
        content = textbox.get("1.0", "end-1c")
        
        for tag in ["keyword", "type", "string", "comment", "function", "number"]:
            textbox.tag_remove(tag, "1.0", "end")
            
        keywords = r'\b(fn|let|struct|import|return|if|else|while|for|true|false)\b'
        types = r'\b(int|float|string|bool)\b'
        functions = r'\b([a-zA-Z_]\w*)\s*\('
        numbers = r'\b(\d+(\.\d+)?)\b'
        strings = r'(".*?")'
        comments = r'(//.*)'
        
        def apply_tag(pattern, tag, group=0):
            for match in re.finditer(pattern, content):
                start_idx = f"1.0 + {match.start(group)} chars"
                end_idx = f"1.0 + {match.end(group)} chars"
                textbox.tag_add(tag, start_idx, end_idx)

        apply_tag(keywords, "keyword")
        apply_tag(types, "type")
        apply_tag(functions, "function", 1)
        apply_tag(numbers, "number")
        apply_tag(strings, "string")
        apply_tag(comments, "comment")

    def open_find_replace(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Find & Replace")
        dialog.geometry("400x200")
        dialog.transient(self)
        
        ctk.CTkLabel(dialog, text="Find:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        find_entry = ctk.CTkEntry(dialog, width=200)
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(dialog, text="Replace:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        replace_entry = ctk.CTkEntry(dialog, width=200)
        replace_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def get_current_textbox():
            current_tab = self.tabview.get()
            if current_tab == "main.cr":
                return self.text_main
            return self.text_math
            
        def find_text():
            textbox = get_current_textbox()
            textbox.tag_remove("search", "1.0", "end")
            target = find_entry.get()
            if not target: return
            
            content = textbox.get("1.0", "end-1c")
            start_pos = "1.0"
            while True:
                start_pos = textbox.search(target, start_pos, stopindex="end")
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(target)}c"
                textbox.tag_add("search", start_pos, end_pos)
                start_pos = end_pos
                
        def replace_text():
            textbox = get_current_textbox()
            target = find_entry.get()
            replacement = replace_entry.get()
            if not target: return
            
            content = textbox.get("1.0", "end-1c")
            new_content = content.replace(target, replacement)
            textbox.delete("1.0", "end")
            textbox.insert("1.0", new_content)
            self.highlight_syntax(textbox)
            
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(btn_frame, text="Find", width=100, command=find_text).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Replace All", width=100, command=replace_text).pack(side="left", padx=10)

    def save_files(self):
        with open(os.path.join(self.workspace_dir, "main.cr"), "w") as f:
            f.write(self.text_main.get("1.0", "end-1c"))
        with open(os.path.join(self.workspace_dir, "math.cr"), "w") as f:
            f.write(self.text_math.get("1.0", "end-1c"))

    def run_code(self):
        self.save_files()
        self.terminal.delete("1.0", "end")
        
        main_file = os.path.join(self.workspace_dir, "main.cr")
        
        def execute():
            try:
                process = subprocess.Popen(
                    ["python3", "/opt/archforge/archforge-de/crust/crustc.py", main_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                for line in process.stdout:
                    self.terminal.insert("end", line)
                    self.terminal.see("end")
                    
                process.wait()
            except Exception as e:
                self.terminal.insert("end", f"Execution Error: {str(e)}\n")
                
        threading.Thread(target=execute, daemon=True).start()

if __name__ == "__main__":
    app = VibeEdit()
    app.mainloop()
