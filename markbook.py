#!/usr/bin/env python3
"""markbook: turn a CSV of student marks into ranked results and printable mark sheets.

Usage:
    python markbook.py examples/sample_marks.csv --out output
"""
import argparse
import csv
import html
import sys
from pathlib import Path

DEFAULT_GRADES = "80:A,70:B,60:C,50:D,0:F"


def parse_grades(text):
    pairs = []
    for item in text.split(","):
        low, letter = item.split(":")
        pairs.append((float(low), letter.strip()))
    return sorted(pairs, reverse=True)


def grade_for(avg, scale):
    for low, letter in scale:
        if avg >= low:
            return letter
    return scale[-1][1]


def load_marks(path, max_mark):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames) < 2:
            sys.exit("CSV needs a name column followed by at least one subject column.")
        name_col, subjects = reader.fieldnames[0], reader.fieldnames[1:]
        students = []
        for line_no, row in enumerate(reader, start=2):
            marks = {}
            for s in subjects:
                raw = (row[s] or "").strip()
                if raw == "":
                    marks[s] = None  # absent / not taken
                    continue
                try:
                    value = float(raw)
                except ValueError:
                    sys.exit(f"Line {line_no}: '{raw}' in {s} is not a number.")
                if not 0 <= value <= max_mark:
                    sys.exit(f"Line {line_no}: {s} mark {value} is outside 0-{max_mark}.")
                marks[s] = value
            students.append({"name": row[name_col].strip(), "marks": marks})
    return subjects, students


def compute(students, subjects, scale, pass_mark):
    for st in students:
        taken = [v for v in st["marks"].values() if v is not None]
        st["total"] = sum(taken)
        st["average"] = round(st["total"] / len(taken), 2) if taken else 0.0
        st["grade"] = grade_for(st["average"], scale)
        st["failed"] = [s for s in subjects
                        if st["marks"][s] is not None and st["marks"][s] < pass_mark]
    ordered = sorted(students, key=lambda s: s["total"], reverse=True)
    prev_total, prev_rank = None, 0
    for i, st in enumerate(ordered, start=1):
        st["rank"] = prev_rank if st["total"] == prev_total else i
        prev_total, prev_rank = st["total"], st["rank"]
    return ordered


def fmt(v):
    return "AB" if v is None else (str(int(v)) if v == int(v) else str(v))


def write_csv(path, subjects, ordered):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Rank", "Name", *subjects, "Total", "Average", "Grade", "Subjects failed"])
        for st in ordered:
            w.writerow([st["rank"], st["name"], *[fmt(st["marks"][s]) for s in subjects],
                        fmt(st["total"]), st["average"], st["grade"], "; ".join(st["failed"])])


def write_html(path, subjects, ordered, title, count):
    css = ("body{font-family:Arial,sans-serif}.sheet{max-width:640px;margin:24px auto;padding:24px;"
           "border:1px solid #333;page-break-after:always}h1{text-align:center;font-size:20px}"
           "table{width:100%;border-collapse:collapse;margin:12px 0}th,td{border:1px solid #999;"
           "padding:6px;text-align:left}.fail{color:#b00020;font-weight:bold}")
    parts = [f"<!doctype html><meta charset='utf-8'><title>{html.escape(title)}</title><style>{css}</style>"]
    for st in ordered:
        rows = "".join(
            f"<tr><td>{html.escape(s)}</td><td class='{'fail' if s in st['failed'] else ''}'>"
            f"{fmt(st['marks'][s])}</td></tr>" for s in subjects)
        parts.append(
            f"<div class='sheet'><h1>{html.escape(title)}</h1>"
            f"<p><b>Name:</b> {html.escape(st['name'])}</p>"
            f"<table><tr><th>Subject</th><th>Marks</th></tr>{rows}</table>"
            f"<p><b>Total:</b> {fmt(st['total'])} &nbsp; <b>Average:</b> {st['average']} &nbsp; "
            f"<b>Grade:</b> {st['grade']} &nbsp; <b>Rank:</b> {st['rank']} of {count}</p></div>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Generate ranked results and printable mark sheets from a CSV.")
    p.add_argument("csv_file", help="CSV: first column = student name, other columns = subjects")
    p.add_argument("--out", default="output", help="output folder (default: output)")
    p.add_argument("--title", default="Student Mark Sheet", help="title on each sheet")
    p.add_argument("--pass-mark", type=float, default=40, help="pass mark per subject (default 40)")
    p.add_argument("--max-mark", type=float, default=100, help="highest valid mark (default 100)")
    p.add_argument("--grades", default=DEFAULT_GRADES,
                   help=f"grade boundaries as min:letter (default '{DEFAULT_GRADES}')")
    a = p.parse_args()

    subjects, students = load_marks(a.csv_file, a.max_mark)
    ordered = compute(students, subjects, parse_grades(a.grades), a.pass_mark)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "results.csv", subjects, ordered)
    write_html(out / "marksheets.html", subjects, ordered, a.title, len(ordered))
    print(f"Done: {len(ordered)} students -> {out / 'results.csv'} and {out / 'marksheets.html'}")


if __name__ == "__main__":
    main()
