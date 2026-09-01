import csv
from pathlib import Path

from systemictau_declare.cli import main
from systemictau_declare.fixtures import g0_independent_ar


def test_cli_writes_html(tmp_path: Path):
    X = g0_independent_ar(T=120, N=3, seed=3)
    csv_path = tmp_path / "g0.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "x1", "x2", "x3"])
        for i, row in enumerate(X):
            w.writerow([i, *row.tolist()])
    out = tmp_path / "report.html"
    rc = main([str(csv_path), "--B", "3", "--out", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "FAR: undefined" in text
    assert "event claimed: false" in text.lower()
    assert "predict_outbreak" in text
