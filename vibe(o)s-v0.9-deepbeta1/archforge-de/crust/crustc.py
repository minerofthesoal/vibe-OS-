#!/usr/bin/env python3
import sys
import os
import subprocess
import re

"""
CRust Compiler / Transpiler (crustc) - vibe(O)s Edition
Made by Gemini 3.1 Pro (so far) | Prompted by ray0ffire/minerofthesoal

Features:
- Multi-file compilation via `import "filename.cr";`
- Structs and object-oriented data (`struct Name { ... }`)
- Rust-like function syntax and C++ memory power
- Colored terminal output
"""

# ANSI Colors
C_GREEN = '\033[92m'
C_BLUE = '\033[94m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_RESET = '\033[0m'

def resolve_imports(filepath, visited=None):
    if visited is None:
        visited = set()
    
    abs_path = os.path.abspath(filepath)
    if abs_path in visited:
        return "" # Prevent infinite loops
    visited.add(abs_path)
    
    if not os.path.exists(abs_path):
        print(f"{C_RED}[!] Error: Imported file '{filepath}' not found.{C_RESET}")
        sys.exit(1)
        
    with open(abs_path, 'r') as f:
        lines = f.readlines()
        
    resolved_lines = []
    for line in lines:
        # Match `import "file.cr";`
        match = re.match(r'^\s*import\s+"([^"]+)"\s*;?', line)
        if match:
            import_file = match.group(1)
            import_path = os.path.join(os.path.dirname(abs_path), import_file)
            print(f"{C_BLUE}[*] Resolving import: {import_file}{C_RESET}")
            resolved_lines.append(resolve_imports(import_path, visited))
        else:
            resolved_lines.append(line)
            
    return "\n".join(resolved_lines)

def transpile_crust_to_cpp(source_code):
    cpp_code = """#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <map>

// CRust Standard Library Mappings
#define println(msg) std::cout << msg << std::endl
#define print(msg) std::cout << msg
using namespace std;

"""
    lines = source_code.split('\n')
    transpiled_lines = []
    
    in_struct = False
    
    for line in lines:
        original = line
        
        # 1. Struct Definitions: struct Point { x: int, y: int }
        if "struct " in line and "{" in line:
            in_struct = True
            
        if in_struct and "}" in line:
            in_struct = False
            line = line.replace("}", "};") # C++ structs need trailing semicolon
            
        # 2. Function Definitions: fn name() -> type {
        if "fn main" in line:
            line = line.replace("fn main", "int main")
        else:
            match = re.search(r'fn\s+(\w+)\s*\((.*?)\)\s*(?:->\s*(\w+))?\s*\{', line)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                ret_type = match.group(3) if match.group(3) else "void"
                
                cpp_args = []
                if args_str.strip():
                    for arg in args_str.split(','):
                        parts = arg.split(':')
                        if len(parts) == 2:
                            cpp_args.append(f"{parts[1].strip()} {parts[0].strip()}")
                        else:
                            cpp_args.append(arg.strip())
                
                line = f"{ret_type} {func_name}({', '.join(cpp_args)}) {{"
        
        # 3. Variable Declarations
        line = re.sub(r'\blet\s+mut\s+(\w+)\s*=', r'auto \1 =', line)
        line = re.sub(r'\blet\s+(\w+)\s*=', r'const auto \1 =', line)
        
        # 4. Print macros
        line = line.replace("println!(", "println(")
        line = line.replace("print!(", "print(")
        
        transpiled_lines.append(line)
        
    return cpp_code + "\n".join(transpiled_lines)

def compile_and_run(filepath):
    if not filepath.endswith(".cr"):
        print(f"{C_RED}[!] Error: File must have a .cr extension{C_RESET}")
        sys.exit(1)
        
    print(f"{C_GREEN}>>> vibe(O)s CRust Compiler <<<{C_RESET}")
    print(f"{C_BLUE}[*] Analyzing {filepath}...{C_RESET}")
    
    # 1. Resolve all imports into a single translation unit
    bundled_source = resolve_imports(filepath)
    
    # 2. Transpile to C++
    cpp_source = transpile_crust_to_cpp(bundled_source)
    
    base_name = os.path.splitext(filepath)[0]
    cpp_file = f"{base_name}.cpp"
    bin_file = f"{base_name}.out"
    
    with open(cpp_file, 'w') as f:
        f.write(cpp_source)
        
    print(f"{C_BLUE}[*] Transpiled to C++20. Compiling...{C_RESET}")
    
    # 3. Compile via g++
    compile_proc = subprocess.run(["g++", "-std=c++20", "-O3", cpp_file, "-o", bin_file])
    
    if compile_proc.returncode == 0:
        print(f"{C_GREEN}[*] Compilation successful!{C_RESET}")
        print(f"{C_YELLOW}--- Executing {bin_file} ---{C_RESET}\n")
        subprocess.run([f"./{bin_file}"])
        print(f"\n{C_YELLOW}--- Execution Finished ---{C_RESET}")
    else:
        print(f"{C_RED}[!] Compilation failed.{C_RESET}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: crustc <file.cr>")
        sys.exit(1)
    compile_and_run(sys.argv[1])
