"""Create batches of worksheets with one shared operation setting."""

from pathlib import Path
import re

from pdf_output import write_worksheet
from worksheet import Question, make_worksheet


def export_batch(output_folder: str | Path, category: str, count: int = 5) -> list[Path]:
    if count < 1:
        raise ValueError("Batch size must be positive")
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)
    topic_slug = re.sub(r"[^A-Za-z0-9]+", "-", category).strip("-")

    sets: list[tuple[list[Question], list[Question]]] = []
    signatures: set[tuple[str, ...]] = set()
    attempts = 0
    while len(sets) < count:
        attempts += 1
        if attempts > count * 100:
            raise RuntimeError("Could not generate enough distinct worksheets")
        worksheet = make_worksheet(category)
        signature = tuple(q.prompt for part in worksheet for q in part)
        if signature in signatures:
            continue
        signatures.add(signature)
        sets.append(worksheet)

    outputs = []
    for set_number, (single, mixed) in enumerate(sets, start=1):
        stem = f"Daily Practice - {topic_slug} - 30 Questions - Set {set_number:02d} of {count:02d}"
        target = folder / f"{stem}.pdf"
        revision = 2
        while target.exists():
            target = folder / f"{stem} ({revision}).pdf"
            revision += 1
        outputs.append(write_worksheet(single, mixed, target))
    return outputs
