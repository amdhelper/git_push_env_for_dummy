import customtkinter as ctk
import os
import sys
import shutil
import subprocess
import threading
import time
import zipfile
from tkinter import filedialog, messagebox

# --- Configuration ---
APP_NAME = "Geinei Uploader (傻瓜版)"
REPO_URL = "git@github.com:amdhelper/geinei.git"
DATA_DIR = os.path.join(os.getcwd(), "geinei_data")
KEY_FILE = os.path.join(DATA_DIR, "geinei_key")
PUB_KEY_FILE = KEY_FILE + ".pub"
REPO_DIR = os.path.join(DATA_DIR, "site_repo")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Set Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("600x500")
        self.resizable(False, False)

        # Check phase
        if not os.path.exists(KEY_FILE):
            self.init_setup_phase()
        else:
            self.init_main_phase()

    def clear_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================
    # PHASE 1: SETUP (Generate Key)
    # ==========================================
    def init_setup_phase(self):
        self.clear_ui()
        
        self.lbl_title = ctk.CTkLabel(self, text="第一次使用初始化", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=20)

        self.lbl_desc = ctk.CTkLabel(self, text="我们需要生成一个安全钥匙连接到GitHub.\n点击下方按钮生成，然后把内容发给管理员(或者自己填入GitHub)。")
        self.lbl_desc.pack(pady=10)

        self.btn_gen = ctk.CTkButton(self, text="1. 生成安全钥匙 (SSH Key)", command=self.generate_key, height=40)
        self.btn_gen.pack(pady=10)

        self.txt_key = ctk.CTkTextbox(self, height=100)
        self.txt_key.pack(padx=20, pady=10, fill="x")
        self.txt_key.insert("0.0", "钥匙将显示在这里...")
        self.txt_key.configure(state="disabled")

        self.btn_copy = ctk.CTkButton(self, text="复制钥匙内容", command=self.copy_key_to_clipboard, fg_color="gray")
        self.btn_copy.pack(pady=5)

        self.lbl_step2 = ctk.CTkLabel(self, text="当GitHub上添加好钥匙后，点击下方按钮完成配置：")
        self.lbl_step2.pack(pady=(20, 5))

        self.btn_verify = ctk.CTkButton(self, text="2. 我已添加，开始初始化仓库", command=self.verify_and_clone, height=40, fg_color="green")
        self.btn_verify.pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(self, text="", text_color="yellow")
        self.lbl_status.pack(pady=5)

    def generate_key(self):
        try:
            if os.path.exists(KEY_FILE):
                os.remove(KEY_FILE)
            if os.path.exists(PUB_KEY_FILE):
                os.remove(PUB_KEY_FILE)
            
            # Generate SSH key using ssh-keygen (no passphrase)
            cmd = f'ssh-keygen -t rsa -b 4096 -f "{KEY_FILE}" -N "" -q'
            subprocess.run(cmd, shell=True, check=True)
            
            with open(PUB_KEY_FILE, 'r') as f:
                pub_key = f.read()
            
            self.txt_key.configure(state="normal")
            self.txt_key.delete("0.0", "end")
            self.txt_key.insert("0.0", pub_key)
            self.txt_key.configure(state="disabled")
            self.lbl_status.configure(text="钥匙生成成功！请复制上面的内容。", text_color="green")
        except Exception as e:
            self.lbl_status.configure(text=f"生成失败: {str(e)}", text_color="red")

    def copy_key_to_clipboard(self):
        try:
            content = self.txt_key.get("0.0", "end").strip()
            if content and "ssh-rsa" in content:
                self.clipboard_clear()
                self.clipboard_append(content)
                self.lbl_status.configure(text="已复制到剪贴板！", text_color="green")
        except:
            pass

    def verify_and_clone(self):
        self.lbl_status.configure(text="正在尝试连接 GitHub...", text_color="yellow")
        self.update() 
        
        # Start in thread
        threading.Thread(target=self._run_clone_process).start()

    def _run_clone_process(self):
        try:
            env = os.environ.copy()
            # Use the local key, ignore known_hosts for simplicity (dummy proof)
            ssh_cmd = f'ssh -i "{KEY_FILE}" -o StrictHostKeyChecking=no'
            env["GIT_SSH_COMMAND"] = ssh_cmd

            if os.path.exists(REPO_DIR):
                shutil.rmtree(REPO_DIR)
            
            # Clone
            cmd = f'git clone {REPO_URL} "{REPO_DIR}"'
            result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.after(0, lambda: self.init_main_phase())
            else:
                err_msg = result.stderr
                if "Permission denied" in err_msg:
                    msg = "权限被拒绝。请确认你真的把钥匙加到GitHub了吗？"
                else:
                    msg = f"连接错误: {err_msg}"
                self.after(0, lambda: self.lbl_status.configure(text=msg, text_color="red"))
        except Exception as e:
             self.after(0, lambda: self.lbl_status.configure(text=f"系统错误: {str(e)}", text_color="red"))

    # ==========================================
    # PHASE 2: MAIN USER INTERFACE
    # ==========================================
    def init_main_phase(self):
        self.clear_ui()
        
        # Header
        self.lbl_head = ctk.CTkLabel(self, text="Geinei 网站更新器", font=("Arial", 24, "bold"))
        self.lbl_head.pack(pady=(30, 20))

        # Main Drop/Select Area
        self.frame_drop = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=15, border_width=2, border_color="#555")
        self.frame_drop.pack(padx=30, pady=10, fill="both", expand=True)
        
        self.lbl_icon = ctk.CTkLabel(self.frame_drop, text="📂", font=("Arial", 60))
        self.lbl_icon.pack(pady=(40, 10))
        
        self.lbl_instr = ctk.CTkLabel(self.frame_drop, text="把文件拖进来\n或者点击这里选择文件/压缩包", font=("Arial", 16))
        self.lbl_instr.pack(pady=10)

        # Invisible button covering the frame to act as click area
        self.btn_overlay = ctk.CTkButton(self.frame_drop, text="", fg_color="transparent", hover_color=None, command=self.browse_files)
        self.btn_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Progress / Status
        self.lbl_progress = ctk.CTkLabel(self, text="准备就绪", font=("Arial", 14), text_color="gray")
        self.lbl_progress.pack(pady=10)

        self.progressbar = ctk.CTkProgressBar(self, width=400)
        self.progressbar.pack(pady=10)
        self.progressbar.set(0)

        # Add manual buttons for fallback
        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(pady=10)
        
        self.btn_select_file = ctk.CTkButton(self.frame_btns, text="选择文件/Zip", command=self.browse_file_manual, width=120)
        self.btn_select_file.pack(side="left", padx=10)
        
        self.btn_select_dir = ctk.CTkButton(self.frame_btns, text="选择文件夹", command=self.browse_folder_manual, width=120)
        self.btn_select_dir.pack(side="left", padx=10)

    def browse_files(self):
        # Default behavior: try to let user pick based on intuition.
        # Since we can't easily unify file/folder picker in one dialog on all OSs, 
        # we will ask or just default to file since zips are most common for "upload packages".
        self.browse_file_manual()

    def browse_file_manual(self):
        path = filedialog.askopenfilename(title="选择要上传的文件或压缩包")
        if path:
            self.start_processing(path)

    def browse_folder_manual(self):
        path = filedialog.askdirectory(title="选择要上传的文件夹")
        if path:
            self.start_processing(path)

    def start_processing(self, source_path):
        self.btn_overlay.configure(state="disabled")
        self.btn_select_file.configure(state="disabled")
        self.btn_select_dir.configure(state="disabled")
        self.progressbar.set(0.1)
        self.lbl_progress.configure(text="正在处理...", text_color="cyan")
        
        threading.Thread(target=self._process_upload, args=(source_path,)).start()

    def _update_status(self, text, progress=None, color="cyan"):
        self.lbl_progress.configure(text=text, text_color=color)
        if progress is not None:
            self.progressbar.set(progress)

    def _process_upload(self, source_path):
        try:
            env = os.environ.copy()
            ssh_cmd = f'ssh -i "{KEY_FILE}" -o StrictHostKeyChecking=no'
            env["GIT_SSH_COMMAND"] = ssh_cmd
            
            # Helper to run git
            def run_git(args, cwd=REPO_DIR):
                cmd = ["git"] + args
                # Use list args for subprocess to avoid shell injection, but need shell=False. 
                # However, for env vars to work with ssh, we pass env.
                res = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
                if res.returncode != 0:
                    raise Exception(f"Git Error ({args[0]}): {res.stderr}")
                return res.stdout

            # 1. Prepare Repo (Reset to match remote as base, or pull)
            self.after(0, self._update_status, "正在同步云端数据...", 0.2)
            
            # Config identity if missing
            run_git(["config", "user.email", "uploader@dummy.app"])
            run_git(["config", "user.name", "Geinei Uploader"])

            # Fetch first
            run_git(["fetch", "origin"])

            # RESET Logic: Since we want to upload *new* files, we ensure we are on clean state.
            # Strategy: Hard reset to origin/main. This solves "conflicts" by ignoring local history 
            # and accepting server history as truth before we apply our new changes.
            # Note: This assumes the user always wants to publish *their currently dropped files* 
            # on top of whatever is on the server.
            try:
                run_git(["reset", "--hard", "origin/main"])
            except:
                # Might fail if branch is different or empty repo, try pull
                run_git(["pull", "origin", "main"])

            self.after(0, self._update_status, "正在解压/复制文件...", 0.4)

            # 2. Copy Files
            # If zip -> Extract
            if source_path.lower().endswith(".zip"):
                with zipfile.ZipFile(source_path, 'r') as zip_ref:
                    zip_ref.extractall(REPO_DIR)
            elif os.path.isdir(source_path):
                # Copy folder contents to REPO_DIR (Merge mode)
                for item in os.listdir(source_path):
                    s = os.path.join(source_path, item)
                    d = os.path.join(REPO_DIR, item)
                    if os.path.isdir(s):
                        # Python 3.8+ supports dirs_exist_ok to merge
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
            else:
                # Single file
                shutil.copy2(source_path, REPO_DIR)

            self.after(0, self._update_status, "正在提交更改...", 0.7)

            # 3. Git Add, Commit, Push
            run_git(["add", "."])
            
            # Check if there are changes
            status = run_git(["status", "--porcelain"])
            if not status.strip():
                self.after(0, self._update_status, "没有发现文件变化", 1.0, "yellow")
                self._reset_ui_delayed()
                return

            run_git(["commit", "-m", f"Auto-update: {time.strftime('%Y-%m-%d %H:%M:%S')}"])
            
            self.after(0, self._update_status, "正在上传到服务器...", 0.8)
            run_git(["push", "origin", "main"])

            self.after(0, self._update_status, "上传成功！✅", 1.0, "green")
            
        except Exception as e:
            print(e)
            self.after(0, self._update_status, f"出错啦: {str(e)}", 0.0, "red")
        
        self._reset_ui_delayed()

    def _reset_ui_delayed(self):
        self.after(3000, lambda: self.btn_overlay.configure(state="normal"))
        self.after(3000, lambda: self.btn_select_file.configure(state="normal"))
        self.after(3000, lambda: self.btn_select_dir.configure(state="normal"))
        self.after(3000, lambda: self.progressbar.set(0))
        self.after(3000, lambda: self.lbl_progress.configure(text="准备就绪", text_color="gray"))

if __name__ == "__main__":
    app = App()
    app.mainloop()
