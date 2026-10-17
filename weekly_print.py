"""Generate this week's five worksheets and print student pages only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import shutil

from pdf_output import write_worksheet
from printer_service import print_pdf_pages
from worksheet import SINGLE_CATEGORIES, Question, make_worksheet


WEEKLY_PLAN = (
    ("integer_add_subtract", 3),
    ("integer_multiply_divide", 1),
    ("fraction_add", 1),
)


@dataclass(frozen=True)
class WeeklySet:
    topic: str
    generated_pdf: Path
    queued_student_pdf: Path
    archive_folder: Path


@dataclass(frozen=True)
class WeeklyPrintResult:
    generated_pdfs: tuple[Path, ...]
    printed_student_pdfs: tuple[Path, ...]
    failed_jobs: tuple[tuple[Path, str], ...]


def _available_pair(generated_folder: Path, queue_folder: Path, stem: str) -> tuple[Path, Path]:
    candidate = stem
    revision = 2
    while (generated_folder / f"{candidate}.pdf").exists() or (queue_folder / f"{candidate}.pdf").exists():
        candidate = f"{stem} ({revision})"
        revision += 1
    return generated_folder / f"{candidate}.pdf", queue_folder / f"{candidate}.pdf"


def create_weekly_pack(
    base_folder: str | Path,
    run_date: date | None = None,
    categories: list[str] | None = None,
) -> list[WeeklySet]:
    if categories is None:
        categories = [category for category, count in WEEKLY_PLAN for _ in range(count)]
    if len(categories) != 5:
        raise ValueError("Choose exactly five worksheet types")
    supported_categories = set(SINGLE_CATEGORIES.values())
    if any(category not in supported_categories for category in categories):
        raise ValueError("The selection contains an unsupported worksheet type")

    date_label = (run_date or date.today()).isoformat()
    generated_folder = Path(base_folder) / "Generated" / date_label
    queue_folder = Path(base_folder) / "Print Queue" / date_label
    archive_folder = Path(base_folder) / "Printed" / date_label
    generated_folder.mkdir(parents=True, exist_ok=True)
    queue_folder.mkdir(parents=True, exist_ok=True)

    total = len(categories)
    used_signatures: set[tuple[str, ...]] = set()
    files: list[WeeklySet] = []
    set_number = 0
    for category in categories:
        topic = category.replace("_", "-")
        for _attempt in range(100):
            single, mixed = make_worksheet(category)
            signature = tuple(question.prompt for part in (single, mixed) for question in part)
            if signature not in used_signatures:
                used_signatures.add(signature)
                break
        else:
            raise RuntimeError("Could not produce five distinct worksheet sets")

        set_number += 1
        stem = f"Daily Practice - {topic} - 30 Questions - Set {set_number:02d} of {total:02d}"
        generated_pdf, queued_pdf = _available_pair(generated_folder, queue_folder, stem)
        write_worksheet(single, mixed, generated_pdf)
        write_worksheet(single, mixed, queued_pdf, include_answer_key=False)
        files.append(WeeklySet(category, generated_pdf, queued_pdf, archive_folder))
    return files


def print_weekly_pack(
    base_folder: str | Path,
    printer_name: str,
    categories: list[str] | None = None,
) -> WeeklyPrintResult:
    weekly_sets = create_weekly_pack(base_folder, categories=categories)
    printed: list[Path] = []
    failures: list[tuple[Path, str]] = []
    for worksheet in weekly_sets:
        try:
            print_pdf_pages(worksheet.queued_student_pdf, printer_name, pages="1-2")
            worksheet.archive_folder.mkdir(parents=True, exist_ok=True)
            archive_target = worksheet.archive_folder / worksheet.queued_student_pdf.name
            revision = 2
            while archive_target.exists():
                archive_target = worksheet.archive_folder / f"{worksheet.queued_student_pdf.stem} ({revision}).pdf"
                revision += 1
            shutil.move(str(worksheet.queued_student_pdf), str(archive_target))
            printed.append(archive_target)
        except Exception as exc:
            failures.append((worksheet.queued_student_pdf, str(exc)))
    return WeeklyPrintResult(
        tuple(item.generated_pdf for item in weekly_sets),
        tuple(printed),
        tuple(failures),
    )
