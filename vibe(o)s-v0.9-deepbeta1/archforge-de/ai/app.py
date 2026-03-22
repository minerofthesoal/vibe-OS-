#!/usr/bin/env python3
import os
import threading
import customtkinter as ctk
from huggingface_hub import hf_hub_download, HfApi

# Target model requested by user
TARGET_REPO = "unsloth/Qwen3.5-4B-GGUF"
FALLBACK_REPO = "unsloth/Qwen2.5-Coder-7B-GGUF" # Fallback if 3.5 is not yet available on HF

class ArchForgeAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ArchForge AI (Local Qwen)")
        self.geometry("850x650")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.llm = None
        self.is_loading = False
        
        # UI Setup
        self.chat_history = ctk.CTkTextbox(self, state="disabled", font=("Inter", 14), wrap="word", fg_color="#1e1e1e")
        self.chat_history.pack(expand=True, fill="both", padx=20, pady=(20, 10))
        
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Click here to load the AI model into memory...", font=("Inter", 14), height=40)
        self.entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        # Lazy load triggers
        self.entry.bind("<FocusIn>", self.lazy_load_model)
        self.entry.bind("<Button-1>", self.lazy_load_model)
        self.entry.bind("<Return>", self.send_message)
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=80, height=40, command=self.send_message, state="disabled")
        self.send_btn.pack(side="right")
        
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", height=4)
        self.progress.set(0)
        # Hidden initially
        
        self.append_chat("System", "Welcome to ArchForge Local AI.\nTo save RAM, the model is currently unloaded.\nClick the input box below to auto-download (if needed) and load the model into memory.")

    def append_chat(self, sender, message):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"[{sender}]\n{message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def lazy_load_model(self, event=None):
        if self.llm is None and not self.is_loading:
            self.is_loading = True
            self.entry.configure(placeholder_text="Downloading/Loading model... Please wait.")
            self.progress.pack(fill="x", padx=20, pady=(0, 10), before=self.input_frame)
            self.progress.start()
            self.append_chat("System", "Initializing local AI engine...")
            threading.Thread(target=self._load_model_thread, daemon=True).start()

    def _load_model_thread(self):
        try:
            self.append_chat("System", "[1/4] Importing Llama.cpp and HuggingFace Hub...")
            from llama_cpp import Llama
            
            api = HfApi()
            self.append_chat("System", f"[2/4] Querying HuggingFace API for {TARGET_REPO}...")
            try:
                files = api.list_repo_files(repo_id=TARGET_REPO)
                repo_to_use = TARGET_REPO
            except Exception:
                self.append_chat("System", f"Warning: {TARGET_REPO} not found. Falling back to {FALLBACK_REPO}.")
                repo_to_use = FALLBACK_REPO
                files = api.list_repo_files(repo_id=repo_to_use)
            
            gguf_files = [f for f in files if f.endswith(".gguf")]
            if not gguf_files:
                raise ValueError("No GGUF files found in repository.")
            
            # Prefer a Q4_K_M quant if available, else take the first one
            model_file = next((f for f in gguf_files if "q4_k_m" in f.lower()), gguf_files[0])
            
            self.append_chat("System", f"[3/4] Resolving weights: {model_file}\nDownloading (or verifying cache)... Check terminal for exact byte progress.")
            model_path = hf_hub_download(repo_id=repo_to_use, filename=model_file)
            
            self.append_chat("System", "[4/4] Allocating RAM/VRAM and instantiating Llama engine. This may take a moment depending on your hardware...")
            # n_gpu_layers=-1 offloads all layers to GPU if available
            self.llm = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=-1, verbose=False)
            
            self.entry.configure(placeholder_text="Type your message...")
            self.send_btn.configure(state="normal")
            self.append_chat("System", "Model loaded successfully! You can now chat.")
            
        except ImportError:
            self.append_chat("System", "Error: llama-cpp-python is not installed. Run: pip install llama-cpp-python huggingface_hub")
        except Exception as e:
            self.append_chat("System", f"Error loading model: {str(e)}")
        finally:
            self.is_loading = False
            self.progress.stop()
            self.progress.pack_forget()

    def send_message(self, event=None):
        if self.llm is None or self.is_loading:
            return
        
        user_text = self.entry.get().strip()
        if not user_text:
            return
            
        self.entry.delete(0, "end")
        self.append_chat("You", user_text)
        self.send_btn.configure(state="disabled")
        
        threading.Thread(target=self._generate_response, args=(user_text,), daemon=True).start()

    def _generate_response(self, prompt):
        try:
            # Qwen ChatML format
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            response = self.llm(formatted_prompt, max_tokens=1024, stop=["<|im_end|>"], echo=False)
            output = response["choices"][0]["text"].strip()
            self.append_chat("AI", output)
        except Exception as e:
            self.append_chat("System", f"Error generating response: {str(e)}")
        finally:
            self.send_btn.configure(state="normal")

if __name__ == "__main__":
    app = ArchForgeAI()
    app.mainloop()
