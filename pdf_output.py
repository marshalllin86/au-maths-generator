"""A4 PDF layout for Daily Practice worksheets and answer keys."""

from pathlib import Path
from fpdf import FPDF
from fpdf.enums import MethodReturnValue, XPos, YPos

from worksheet import Question


def _student_header(pdf: FPDF, continuation: bool = False) -> None:
    pdf.set_font("Helvetica", style="B", size=22)
    title = "Daily Practice (continued)" if continuation else "Daily Practice"
    pdf.cell(0, 12, title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 8, "Name: __________________  Date: __________  Time: ______  Score: ____ / 30",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)


def _question_rows(pdf: FPDF, questions: list[Question], start_number: int) -> None:
    page_count = 15
    for offset in range(0, len(questions), page_count):
        page_items = questions[offset:offset + page_count]
        if offset:
            pdf.add_page()
            _student_header(pdf, continuation=True)
        for idx, question in enumerate(page_items, start=start_number + offset):
            pdf.set_font("Helvetica", size=12)
            line_height = 6
            number_width = 12
            question_x = pdf.l_margin + number_width
            question_width = pdf.w - pdf.r_margin - question_x
            text_height = pdf.multi_cell(
                question_width,
                line_height,
                txt=question.prompt,
                dry_run=True,
                output=MethodReturnValue.HEIGHT,
            )
            row_height = max(12, text_height)
            if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
                pdf.add_page()
                _student_header(pdf, continuation=True)
            row_y = pdf.get_y()
            pdf.set_font("Helvetica", size=12)
            pdf.cell(number_width, row_height, f"{idx}.")
            pdf.set_xy(question_x, row_y)
            pdf.multi_cell(
                question_width,
                line_height,
                txt=question.prompt,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.line(pdf.l_margin, row_y + row_height, pdf.w - pdf.r_margin, row_y + row_height)
            pdf.set_y(row_y + row_height + 2)


def write_worksheet(
    single: list[Question],
    mixed: list[Question],
    output: str | Path,
    *,
    include_answer_key: bool = True,
) -> Path:
    if len(single) != 20 or len(mixed) != 10:
        raise ValueError("A worksheet must have 20 single-operation and 10 mixed questions")
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF(format="A4")
    pdf.set_margins(18, 14, 18)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    _student_header(pdf)
    _question_rows(pdf, single, 1)
    _question_rows(pdf, mixed, 21)

    if include_answer_key:
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=20)
        pdf.cell(0, 14, "Answer Key", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(7)
        all_questions = single + mixed
        pdf.set_font("Helvetica", size=11)
        column_width = (pdf.w - pdf.l_margin - pdf.r_margin) / 3
        for row in range(10):
            for column in range(3):
                index = column * 10 + row
                question = all_questions[index]
                pdf.cell(column_width, 11, f"{index + 1}.  {question.answer}")
            pdf.ln(11)
    pdf.output(str(target))
    return target
