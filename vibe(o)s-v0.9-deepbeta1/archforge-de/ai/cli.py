#!/usr/bin/env python3
import sys
from huggingface_hub import hf_hub_download, HfApi

TARGET_REPO = "unsloth/Qwen3.5-4B-GGUF"
FALLBACK_REPO = "unsloth/Qwen2.5-Coder-7B-GGUF"

def main():
    print("========================================")
    print("      ArchForge Local AI CLI            ")
    print("========================================")
    print("Initializing and loading model into memory...")
    
    try:
        from llama_cpp import Llama
        api = HfApi()
        try:
            files = api.list_repo_files(repo_id=TARGET_REPO)
            repo_to_use = TARGET_REPO
        except Exception:
            print(f"[WARN] {TARGET_REPO} not found. Falling back to {FALLBACK_REPO}.")
            repo_to_use = FALLBACK_REPO
            files = api.list_repo_files(repo_id=repo_to_use)
            
        gguf_files = [f for f in files if f.endswith(".gguf")]
        model_file = next((f for f in gguf_files if "q4_k_m" in f.lower()), gguf_files[0])
        
        print(f"Downloading/Verifying {model_file}...")
        model_path = hf_hub_download(repo_id=repo_to_use, filename=model_file)
        
        print("Loading into RAM/VRAM...")
        llm = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=-1, verbose=False)
        print("\n[SUCCESS] Model loaded! Type 'exit' or 'quit' to end the session.\n")
        
        while True:
            user_input = input("\033[94mYou:\033[0m ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            formatted_prompt = f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
            response = llm(formatted_prompt, max_tokens=1024, stop=["<|im_end|>"], echo=False)
            output = response['choices'][0]['text'].strip()
            print(f"\033[92mAI:\033[0m {output}\n")
            
    except ImportError:
        print("[ERROR] Missing dependencies. Run: pip install llama-cpp-python huggingface_hub")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
