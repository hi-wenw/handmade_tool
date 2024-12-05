import tkinter as tk
from tkinter import messagebox, ttk
import psutil
from collections import defaultdict


class AppInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("系统进程监视器")

        self.tree = ttk.Treeview(root, columns=('pid', 'name', 'cpu', 'memory', 'cmdline'), show='headings')
        self.tree.heading('pid', text='PID')
        self.tree.heading('name', text='应用名称')
        self.tree.heading('cpu', text='CPU 占用 (%)')
        self.tree.heading('memory', text='内存占用 (MB)')
        self.tree.heading('cmdline', text='命令行')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.cpu_label = tk.Label(root, text="总 CPU 使用率: ")
        self.cpu_label.pack(side=tk.TOP, anchor=tk.W)

        self.mem_label = tk.Label(root, text="总内存使用率: ")
        self.mem_label.pack(side=tk.TOP, anchor=tk.W)

        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        refresh_button = tk.Button(button_frame, text="刷新", command=self.refresh)
        refresh_button.pack(side=tk.LEFT, expand=True)

        terminate_button = tk.Button(button_frame, text="终止应用", command=self.terminate_process)
        terminate_button.pack(side=tk.LEFT, expand=True)

        self.sort_cpu_ascending = True
        sort_cpu_button = tk.Button(button_frame, text="按 CPU 排序", command=self.sort_by_cpu)
        sort_cpu_button.pack(side=tk.LEFT, expand=True)

        self.sort_mem_ascending = True
        sort_mem_button = tk.Button(button_frame, text="按内存排序", command=self.sort_by_memory)
        sort_mem_button.pack(side=tk.LEFT, expand=True)

        close_button = tk.Button(button_frame, text="关闭", command=root.quit)
        close_button.pack(side=tk.LEFT, expand=True)

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        processes_by_cmdline = defaultdict(lambda: {"pids": [], "name": "", "cpu_percent": 0, "memory_info": 0})

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info["cmdline"]) if proc.info["cmdline"] else '[No Command Line]'
                name = proc.info['name']
                cpu_percent = proc.info['cpu_percent']
                memory_info = proc.info['memory_info'].rss / (1024 * 1024)

                processes_by_cmdline[cmdline]["pids"].append(proc.info["pid"])
                processes_by_cmdline[cmdline]["name"] = name
                processes_by_cmdline[cmdline]["cpu_percent"] += cpu_percent
                processes_by_cmdline[cmdline]["memory_info"] += memory_info
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        for cmdline, info in processes_by_cmdline.items():
            pid = info["pids"][0]  # 使用第一个 PID 作为代表
            name = info["name"]
            cpu_percent = info["cpu_percent"]
            memory_info = info["memory_info"]
            self.tree.insert('', 'end', values=(pid, name, cpu_percent, memory_info, cmdline))

        # 更新总 CPU 和内存使用率信息
        cpu_percent = psutil.cpu_percent(interval=1)
        mem_info = psutil.virtual_memory()

        self.cpu_label.config(text=f"总 CPU 使用率: {cpu_percent:.2f}%")
        self.mem_label.config(
            text=f"总内存使用率: {mem_info.percent:.2f}% ({mem_info.used / (1024 * 1024):.2f}MB / {mem_info.total / (1024 * 1024):.2f}MB)")

    def terminate_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个进程")
            return

        item = self.tree.item(selected_item)
        pid = item['values'][0]

        try:
            process = psutil.Process(pid)
            process.terminate()
            self.refresh()
            messagebox.showinfo("信息", f"成功终止进程 {pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("错误", f"无法终止进程 {pid}: {str(e)}")

    def sort_by_cpu(self):
        self.sort_tree("cpu", self.sort_cpu_ascending)
        self.sort_cpu_ascending = not self.sort_cpu_ascending

    def sort_by_memory(self):
        self.sort_tree("memory", self.sort_mem_ascending)
        self.sort_mem_ascending = not self.sort_mem_ascending

    def sort_tree(self, col, ascending):
        # 获取所有行数据
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        # 对数据进行排序
        items.sort(reverse=not ascending, key=lambda t: float(t[0]) if t[0] else 0)

        # 根据排序后的顺序重新插入数据
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)

        # 更新标题的排序符号
        col_names = {'pid': 'PID', 'name': '应用名称', 'cpu': 'CPU 占用 (%)', 'memory': '内存占用 (MB)',
                     'cmdline': '命令行'}
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col_names[col])

        if ascending:
            self.tree.heading(col, text=f"{col_names[col]} ▲")
        else:
            self.tree.heading(col, text=f"{col_names[col]} ▼")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppInfoApp(root)
    root.mainloop()