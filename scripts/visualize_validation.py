"""Visualización descriptiva del test congelado; no entrena ni selecciona umbrales."""
import csv
import hashlib
import json
import re
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "datos/predicciones_test.csv"


def main():
    with SOURCE.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    matrix = [[0, 0], [0, 0]]
    lengths = {"negative": [], "neutral": [], "positive": []}
    for row in rows:
        actual = int(row["y"])
        predicted = int(float(row["SVM_calibrada"]) >= 0.20)
        matrix[actual][predicted] += 1
        lengths[row["etiqueta"]].append(len(re.findall(r"\b\w+\b", row["texto"])))
    assert sum(map(sum, matrix)) == len(rows)
    assert sum(map(len, lengths.values())) == len(rows)
    out = ROOT / "evidencias"
    summary = {
        "source": "datos/predicciones_test.csv",
        "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "n": len(rows), "threshold": 0.20,
        "confusion_matrix": matrix,
        "matrix_axes": "filas: real 0/1; columnas: predicción 0/1; 1=negativa",
        "length_definition": "Número de coincidencias regex \\b\\w+\\b; no son tokens del modelo.",
        "length_by_original_label": {
            label: {"n": len(values), "median": statistics.median(values),
                    "min": min(values), "max": max(values)}
            for label, values in lengths.items()
        },
        "scope": "Descripción retrospectiva; no evaluación nueva, explicación causal ni criterio de ajuste."
    }
    (out / "analisis_visual.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fig, ax = plt.subplots(figsize=(7, 5), layout="constrained")
    ax.imshow(matrix, cmap="Blues")
    labels = [["TN", "FP"], ["FN", "TP"]]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{labels[i][j]}\n{matrix[i][j]}", ha="center", va="center", fontsize=20,
                    color="white" if matrix[i][j] > max(map(max, matrix)) / 2 else "#043263")
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["No negativa", "Negativa"],
           yticklabels=["No negativa", "Negativa"], xlabel="Predicción", ylabel="Clase real",
           title=f"Test conservado · {len(rows)} noticias · umbral 0.20")
    fig.savefig(out / "matriz_confusion_revision.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    ax.boxplot(list(lengths.values()), tick_labels=[f"{label}\n(n={len(values)})" for label, values in lengths.items()],
               patch_artist=True, boxprops={"facecolor": "#5BBEFF"}, medianprops={"color": "#043263"})
    ax.set(title="Longitud por etiqueta original · test retrospectivo", ylabel="Unidades léxicas por noticia")
    ax.grid(axis="y", alpha=.2)
    fig.savefig(out / "longitud_por_clase.png", dpi=170)
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
