"""对话框模块"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.scrolled import ScrolledText
from tkinter import messagebox, Button
import json

from konata_api.utils import resource_path, save_config


class SettingsDialog:
    """API 接口设置对话框"""
    def __init__(self, parent, config):
        self.config = config
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("API 接口设置")
        self.dialog.geometry("800x400")
        self.dialog.resizable(True, True)

        # 设置窗口图标
        try:
            self.dialog.iconbitmap(resource_path("assets/icon.ico"))
        except:
            pass

        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        """创建对话框控件"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        ttk.Label(main_frame, text="自定义 API 接口路径", font=("Microsoft YaHei", 12, "bold")).pack(anchor=W, pady=(0, 15))
        ttk.Label(main_frame, text="留空则使用默认接口路径", font=("Microsoft YaHei", 9), bootstyle="secondary").pack(anchor=W, pady=(0, 20))

        # 日志每页条数
        page_size_frame = ttk.Frame(main_frame)
        page_size_frame.pack(fill=X, pady=8)
        ttk.Label(page_size_frame, text="日志每页条数:", width=15).pack(side=LEFT)
        self.page_size_var = ttk.StringVar()
        ttk.Entry(page_size_frame, textvariable=self.page_size_var, width=10, bootstyle="info").pack(side=LEFT)
        ttk.Label(page_size_frame, text="（默认 50）", bootstyle="secondary").pack(side=LEFT, padx=(10, 0))

        # 余额订阅接口
        sub_frame = ttk.Frame(main_frame)
        sub_frame.pack(fill=X, pady=8)
        ttk.Label(sub_frame, text="余额订阅接口:", width=15).pack(side=LEFT)
        self.sub_var = ttk.StringVar()
        ttk.Entry(sub_frame, textvariable=self.sub_var, bootstyle="info").pack(side=LEFT, fill=X, expand=YES)

        # 余额用量接口
        usage_frame = ttk.Frame(main_frame)
        usage_frame.pack(fill=X, pady=8)
        ttk.Label(usage_frame, text="余额用量接口:", width=15).pack(side=LEFT)
        self.usage_var = ttk.StringVar()
        ttk.Entry(usage_frame, textvariable=self.usage_var, bootstyle="info").pack(side=LEFT, fill=X, expand=YES)

        # 日志查询接口
        logs_frame = ttk.Frame(main_frame)
        logs_frame.pack(fill=X, pady=8)
        ttk.Label(logs_frame, text="日志查询接口:", width=15).pack(side=LEFT)
        self.logs_var = ttk.StringVar()
        ttk.Entry(logs_frame, textvariable=self.logs_var, bootstyle="info").pack(side=LEFT, fill=X, expand=YES)

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(30, 0))

        # 右侧按钮
        right_btns = ttk.Frame(btn_frame)
        right_btns.pack(side=RIGHT)

        save_btn = Button(right_btns, text="保存", command=self.save_settings,
                         bg="#28a745", fg="white", font=("Microsoft YaHei", 10),
                         relief="flat", padx=20, pady=8, cursor="hand2")
        save_btn.pack(side=LEFT, padx=5)

        cancel_btn = Button(right_btns, text="取消", command=self.dialog.destroy,
                           bg="#6c757d", fg="white", font=("Microsoft YaHei", 10),
                           relief="flat", padx=20, pady=8, cursor="hand2")
        cancel_btn.pack(side=LEFT, padx=5)

        # 左侧按钮
        reset_btn = Button(btn_frame, text="恢复默认", command=self.reset_defaults,
                          bg="white", fg="#fd7e14", font=("Microsoft YaHei", 10),
                          relief="solid", borderwidth=1, padx=15, pady=8, cursor="hand2")
        reset_btn.pack(side=LEFT)

    def load_settings(self):
        """加载当前设置"""
        endpoints = self.config.get("api_endpoints", {})
        self.sub_var.set(endpoints.get("balance_subscription", "/v1/dashboard/billing/subscription"))
        self.usage_var.set(endpoints.get("balance_usage", "/v1/dashboard/billing/usage"))
        self.logs_var.set(endpoints.get("logs", "/api/log/token"))
        self.page_size_var.set(str(endpoints.get("logs_page_size", 50)))

    def reset_defaults(self):
        """恢复默认设置"""
        self.sub_var.set("/v1/dashboard/billing/subscription")
        self.usage_var.set("/v1/dashboard/billing/usage")
        self.logs_var.set("/api/log/token")
        self.page_size_var.set("50")

    def save_settings(self):
        """保存设置"""
        try:
            page_size = int(self.page_size_var.get().strip())
            if page_size <= 0:
                page_size = 50
        except ValueError:
            page_size = 50

        self.config["api_endpoints"] = {
            "balance_subscription": self.sub_var.get().strip(),
            "balance_usage": self.usage_var.get().strip(),
            "logs": self.logs_var.get().strip(),
            "logs_page_size": page_size
        }
        save_config(self.config)
        messagebox.showinfo("成功", "API 接口设置已保存", parent=self.dialog)
        self.dialog.destroy()


class RawResponseDialog:
    """原始返回数据查看弹窗"""
    def __init__(self, parent, title, data):
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)

        # 设置窗口图标
        try:
            self.dialog.iconbitmap(resource_path("assets/icon.ico"))
        except:
            pass

        # 居中显示
        self.dialog.transient(parent)

        self.create_widgets(data)

    def create_widgets(self, data):
        """创建弹窗控件"""
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=BOTH, expand=YES)

        ttk.Label(main_frame, text="API 返回的原始 JSON 数据：", font=("Microsoft YaHei", 10)).pack(anchor=W, pady=(0, 10))

        # JSON 文本框
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=BOTH, expand=YES)

        self.text = ScrolledText(text_frame, font=("Consolas", 10), wrap="none", autohide=True)
        self.text.pack(fill=BOTH, expand=YES)

        # 格式化 JSON 并显示
        try:
            formatted_json = json.dumps(data, ensure_ascii=False, indent=2)
        except:
            formatted_json = str(data)

        self.text.insert("1.0", formatted_json)

        # 按钮区
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(15, 0))

        ttk.Button(btn_frame, text="📋 复制到剪贴板", command=self.copy_to_clipboard, bootstyle="info-outline", width=15).pack(side=LEFT)
        ttk.Button(btn_frame, text="关闭", command=self.dialog.destroy, bootstyle="secondary", width=10).pack(side=RIGHT)

    def copy_to_clipboard(self):
        """复制内容到剪贴板"""
        content = self.text.get("1.0", "end-1c")
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(content)
        messagebox.showinfo("成功", "已复制到剪贴板", parent=self.dialog)
