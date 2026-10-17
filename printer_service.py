"""Windows printer discovery and SumatraPDF print submission."""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from pathlib import Path
import shutil
import subprocess


class _PrinterInfo4(ctypes.Structure):
    _fields_ = [
        ("pPrinterName", wintypes.LPWSTR),
        ("pServerName", wintypes.LPWSTR),
        ("Attributes", wintypes.DWORD),
    ]


def list_printers() -> list[str]:
    if os.name != "nt":
        return []
    spool = ctypes.WinDLL("winspool.drv", use_last_error=True)
    enum_printers = spool.EnumPrintersW
    enum_printers.argtypes = [
        wintypes.DWORD, wintypes.LPWSTR, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
    ]
    enum_printers.restype = wintypes.BOOL
    needed, returned = wintypes.DWORD(), wintypes.DWORD()
    flags = 0x00000002 | 0x00000004  # local and connected printers
    enum_printers(flags, None, 4, None, 0, ctypes.byref(needed), ctypes.byref(returned))
    if not needed.value:
        return []
    buffer = ctypes.create_string_buffer(needed.value)
    if not enum_printers(flags, None, 4, buffer, needed.value,
                         ctypes.byref(needed), ctypes.byref(returned)):
        raise ctypes.WinError(ctypes.get_last_error())
    entries = ctypes.cast(buffer, ctypes.POINTER(_PrinterInfo4))
    return sorted({entries[index].pPrinterName for index in range(returned.value)})


def sumatra_path() -> Path:
    project_copy = Path(__file__).parent / "tools" / "sumatra" / "SumatraPDF-3.6.1-64.exe"
    if project_copy.is_file():
        return project_copy
    installed = shutil.which("SumatraPDF.exe") or shutil.which("SumatraPDF")
    if installed:
        return Path(installed)
    raise FileNotFoundError("SumatraPDF portable print engine is missing from tools/sumatra.")


def print_pdf_pages(pdf_path: str | Path, printer_name: str, pages: str = "1-2") -> None:
    executable = sumatra_path()
    target = Path(pdf_path)
    if not target.is_file():
        raise FileNotFoundError(target)
    result = subprocess.run(
        [str(executable), "-print-to", printer_name, "-print-settings", pages,
         "-silent", str(target)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise RuntimeError(f"Print failed for {target.name}: {detail}")
