"""Desktop GUI for generating Daily Practice PDFs."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from batch_export import export_batch
from printer_service import list_printers
from weekly_print import print_weekly_pack
from worksheet import SINGLE_CATEGORIES


PROJECT_FOLDER = Path(__file__).resolve().parent
ENV_FILE = PROJECT_FOLDER / ".env"
DEFAULT_WEEKLY_SELECTION = ["整数加减法"] * 3 + ["整数乘除法", "分数加法"]


def _read_env_value(name: str) -> str:
    try:
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key.strip() == name:
                    return value.strip().strip("\"'")
    except OSError:
        pass
    return ""


def _load_math_folder() -> Path:
    """Load MATH_OUTPUT_DIR from the local .env, resolving relative paths here."""
    configured_path = _read_env_value("MATH_OUTPUT_DIR")
    if not configured_path:
        return PROJECT_FOLDER / "Math"
    path = Path(configured_path).expanduser()
    return path if path.is_absolute() else (PROJECT_FOLDER / path).resolve()


MATH_FOLDER = _load_math_folder()
PREFERRED_PRINTER = _read_env_value("PREFERRED_PRINTER")
WEEKLY_SELECTION_FILE = MATH_FOLDER / "weekly_selection.json"


class DailyPracticeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Daily Practice 练习卷生成器")
        root.geometry("720x720")
        root.minsize(650, 650)

        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Daily Practice 练习卷生成器", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="选择本周要生成的五份练习卷题型；每份可单独选择，也可以重复。", wraplength=660).pack(
            anchor="w", pady=(8, 12)
        )

        weekly_frame = ttk.LabelFrame(frame, text="本周五份练习卷", padding=(10, 6))
        weekly_frame.pack(fill="x", pady=(0, 12))
        saved_selection = self._load_weekly_selection()
        self.weekly_labels: list[tk.StringVar] = []
        for index, default_label in enumerate(saved_selection, start=1):
            row = ttk.Frame(weekly_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"第 {index} 份：", width=9).pack(side="left")
            selection = tk.StringVar(value=default_label)
            self.weekly_labels.append(selection)
            ttk.Combobox(
                row,
                textvariable=selection,
                values=list(SINGLE_CATEGORIES),
                state="readonly",
                width=28,
            ).pack(side="left")

        ttk.Label(frame, text="打印机：").pack(anchor="w")
        try:
            self.printers = list_printers()
        except Exception as exc:
            self.printers = []
            messagebox.showwarning("打印机读取失败", f"无法读取 Windows 打印机列表：\n{exc}")
        initial_printer = PREFERRED_PRINTER if PREFERRED_PRINTER in self.printers else (
            self.printers[0] if self.printers else ""
        )
        self.printer_name = tk.StringVar(value=initial_printer)
        self.printer_box = ttk.Combobox(
            frame,
            textvariable=self.printer_name,
            values=self.printers,
            state="readonly" if self.printers else "disabled",
            width=48,
        )
        self.printer_box.pack(anchor="w", pady=(4, 8))

        ttk.Button(
            frame,
            text="生成本周 5 份并打印（只打印第 1–2 页）",
            command=self.print_weekly,
            state="normal" if self.printers else "disabled",
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(
            frame,
            text=f"原始含答案 PDF：{MATH_FOLDER}\\Generated\\日期\n"
            f"打印后的两页学生卷：{MATH_FOLDER}\\Printed\\日期",
            wraplength=620,
        ).pack(anchor="w", pady=(0, 8))

        ttk.Separator(frame).pack(fill="x", pady=(0, 14))
        ttk.Label(frame, text="额外自选题型批量生成（5 份）：").pack(anchor="w")

        ttk.Label(frame, text="选择 20 题的单一运算类型：").pack(anchor="w")
        self.selected_label = tk.StringVar(value="整数加法")
        self.category_box = ttk.Combobox(
            frame,
            textvariable=self.selected_label,
            values=list(SINGLE_CATEGORIES),
            state="readonly",
            width=34,
        )
        self.category_box.pack(anchor="w", pady=(6, 18))

        actions = ttk.Frame(frame)
        actions.pack(fill="x")
        ttk.Button(actions, text="生成自选题型 5 份…", command=self.generate).pack(side="left")
        ttk.Button(actions, text="退出", command=root.destroy).pack(side="right")

        ttk.Label(
            frame,
            text="每日练习记录和错题追踪计划放在第二阶段。",
            foreground="#555555",
        ).pack(anchor="w", side="bottom", pady=(18, 0))

    def generate(self) -> None:
        label = self.selected_label.get()
        category = SINGLE_CATEGORIES[label]
        folder = filedialog.askdirectory(title="选择练习卷保存文件夹", mustexist=True)
        if not folder:
            return
        try:
            saved_paths = export_batch(folder, category, count=5)
        except Exception as exc:
            messagebox.showerror("生成失败", f"无法生成练习卷：\n{exc}")
            return
        messagebox.showinfo(
            "生成完成",
            f"已生成 5 份英文练习卷（每份含独立答案页），保存位置：\n{folder}\n\n"
            + "\n".join(path.name for path in saved_paths),
        )

    def print_weekly(self) -> None:
        printer = self.printer_name.get()
        if not printer:
            messagebox.showerror("没有可用打印机", "请先连接并安装打印机，然后重新打开程序。")
            return
        labels = [selection.get() for selection in self.weekly_labels]
        try:
            WEEKLY_SELECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
            WEEKLY_SELECTION_FILE.write_text(json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("保存设置失败", f"无法保存本周题型选择：\n{exc}")
            return
        categories = [SINGLE_CATEGORIES[label] for label in labels]
        try:
            result = print_weekly_pack(MATH_FOLDER, printer, categories=categories)
        except Exception as exc:
            messagebox.showerror("生成失败", f"无法生成本周练习卷：\n{exc}")
            return

        summary = (
            f"已生成 {len(result.generated_pdfs)} 份含答案原卷。\n"
            f"打印并归档了 {len(result.printed_student_pdfs)} 份两页学生卷。\n"
            f"打印机：{printer}\n"
            f"归档位置：{MATH_FOLDER}\\Printed\\日期"
        )
        if result.failed_jobs:
            summary += "\n\n打印失败的文件保留在 Print Queue 文件夹：\n"
            summary += "\n".join(f"{path.name}: {error}" for path, error in result.failed_jobs)
            messagebox.showwarning("部分打印失败", summary)
        else:
            messagebox.showinfo("每周练习完成", summary)

    @staticmethod
    def _load_weekly_selection() -> list[str]:
        try:
            saved = json.loads(WEEKLY_SELECTION_FILE.read_text(encoding="utf-8"))
            if (
                isinstance(saved, list)
                and len(saved) == 5
                and all(isinstance(item, str) and item in SINGLE_CATEGORIES for item in saved)
            ):
                return saved
        except (OSError, json.JSONDecodeError):
            pass
        return DEFAULT_WEEKLY_SELECTION.copy()


def main() -> None:
    root = tk.Tk()
    DailyPracticeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
