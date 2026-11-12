# markbook

A tiny, dependency-free tool that turns a CSV of student marks into ranked results and printable mark sheets. Built for teachers and school admins who track marks in spreadsheets and are tired of formatting every sheet by hand.

## What it does

- Calculates **total, average, grade and rank** for every student
- Handles **ties** (equal totals share a rank) and **absent students** (leave the cell empty)
- Flags subjects below the **pass mark**
- Produces `results.csv` (open in Excel/Sheets) and `marksheets.html` (one printable page per student)
- Configurable pass mark, maximum mark and grade boundaries
- Pure Python 3, no installs needed

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/markbook.git
cd markbook
python markbook.py examples/sample_marks.csv --out output
```

Open `output/marksheets.html` in a browser and print (or save as PDF).

## Input format

First column is the student name, every other column is a subject:

```csv
Name,Maths,Science,English
Nimal Perera,88,92,75
Ishara Wijesinghe,70,,65
```

An empty cell means the student was absent for that subject.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--out` | `output` | Output folder |
| `--title` | `Student Mark Sheet` | Heading on each sheet |
| `--pass-mark` | `40` | Subjects below this are flagged |
| `--max-mark` | `100` | Highest valid mark |
| `--grades` | `80:A,70:B,60:C,50:D,0:F` | Grade boundaries as `min:letter` |

Example with custom grades: `python markbook.py marks.csv --grades "75:A,65:B,50:C,35:S,0:W"`

## Roadmap

- [ ] Per-subject class averages and highest marks
- [ ] Weighted subjects
- [ ] PDF export
- [ ] Sinhala/Tamil sheet templates
- [ ] Tests

## Contributing

Issues and pull requests are welcome, especially for new grading schemes and sheet layouts.

## License

MIT
