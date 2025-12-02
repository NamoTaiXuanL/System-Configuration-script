# 系统配置安装器项目组Seraphiel 2025.12.02 v1.0 可视化系统配置安装器

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os

class SystemConfigInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("系统配置安装器")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 设置图标（如果有）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主标题
        title_label = ttk.Label(self.root, text="系统配置安装器", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 安装选项框架
        options_frame = ttk.LabelFrame(self.root, text="安装选项")
        options_frame.pack(pady=10, padx=20, fill="x")
        
        # Python安装选项
        self.python_var = tk.BooleanVar()
        python_check = ttk.Checkbutton(options_frame, text="安装 Python 3.14.0", variable=self.python_var)
        python_check.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # PowerShell策略修复
        self.powershell_var = tk.BooleanVar()
        powershell_check = ttk.Checkbutton(options_frame, text="修复 PowerShell 执行策略", variable=self.powershell_var)
        powershell_check.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Claude GLM安装
        self.claude_var = tk.BooleanVar()
        claude_check = ttk.Checkbutton(options_frame, text="安装 Claude Code + GLM", variable=self.claude_var)
        claude_check.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        # Git安装
        self.git_var = tk.BooleanVar()
        git_check = ttk.Checkbutton(options_frame, text="安装 Git", variable=self.git_var)
        git_check.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(pady=20, padx=20, fill="x")
        
        # 状态标签
        self.status_label = ttk.Label(self.root, text="准备就绪")
        self.status_label.pack(pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 安装按钮
        install_btn = ttk.Button(button_frame, text="开始安装", command=self.start_installation)
        install_btn.pack(side="left", padx=10)
        
        # 退出按钮
        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.quit)
        exit_btn.pack(side="left", padx=10)
        
    def start_installation(self):
        # 检查是否有选中的选项
        if not any([self.python_var.get(), self.powershell_var.get(), 
                   self.claude_var.get(), self.git_var.get()]):
            messagebox.showwarning("警告", "请至少选择一个安装选项")
            return
        
        # 禁用安装按钮
        self.root.winfo_children()[-1].winfo_children()[0].config(state="disabled")
        
        # 重置进度条
        self.progress["value"] = 0
        self.progress["maximum"] = self.count_selected_tasks()
        
        self.status_label.config(text="正在安装...")
        
        # 在新线程中执行安装
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
        
    def run_installation(self):
        try:
            # 执行选中的安装任务
            if self.python_var.get():
                self.install_python()
                
            if self.powershell_var.get():
                self.fix_powershell_policy()
                
            if self.claude_var.get():
                self.install_claude_glm()
                
            if self.git_var.get():
                self.install_git()
                
            # 安装完成
            self.root.after(0, self.installation_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.installation_failed(str(e)))
    
    def install_python(self):
        self.update_status("正在安装 Python 3.14.0...")
        script_path = os.path.join(os.path.dirname(__file__), "install_python.bat")
        subprocess.run([script_path], check=True, shell=True)
    
    def fix_powershell_policy(self):
        self.update_status("正在修复 PowerShell 执行策略...")
        script_path = os.path.join(os.path.dirname(__file__), "fix_powershell_policy.py")
        subprocess.run(["python", script_path], check=True)
    
    def install_claude_glm(self):
        self.update_status("正在安装 Claude Code + GLM...")
        script_path = os.path.join(os.path.dirname(__file__), "install_claude_glm.py")
        subprocess.run(["python", script_path], check=True)
    
    def install_git(self):
        self.update_status("正在安装 Git...")
        script_path = os.path.join(os.path.dirname(__file__), "install_git.py")
        subprocess.run(["python", script_path], check=True)
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def installation_complete(self):
        self.progress.stop()
        self.status_label.config(text="安装完成！")
        self.root.winfo_children()[-1].winfo_children()[0].config(state="normal")
        messagebox.showinfo("完成", "所有选中的安装任务已完成")
    
    def installation_failed(self, error_message):
        self.progress.stop()
        self.status_label.config(text="安装失败")
        self.root.winfo_children()[-1].winfo_children()[0].config(state="normal")
        messagebox.showerror("错误", f"安装过程中出现错误:\n{error_message}")

def main():
    root = tk.Tk()
    app = SystemConfigInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()