import gzip
import os
from pathlib import Path

data_dir = Path(os.environ.get(
    "CELLSCOPE_DATA_DIR",
    "data/processed/filtered_feature_bc_matrix"
))

with gzip.open(data_dir / "features.tsv.gz", "rt") as f:
    features = [line.rstrip().split("\t") for line in f]

with gzip.open(data_dir / "barcodes.tsv.gz", "rt") as f:
    barcodes = [line.rstrip() for line in f]

feature_types = {}
for feature in features:
    kind = feature[2]
    feature_types[kind] = feature_types.get(kind, 0) + 1

with gzip.open(data_dir / "matrix.mtx.gz", "rt") as f:
    for line in f:
        if not line.startswith("%"):
            n_features, n_cells, n_nonzero = map(int, line.split())
            break

output = Path(os.environ.get(
    "CELLSCOPE_OUTPUT", "results/dataset_summary.txt"
))
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w") as f:
    f.write("CellScope Dataset Summary\n")
    f.write("=========================\n")
    f.write(f"Cells: {len(barcodes)}\n")
    f.write(f"Features: {len(features)}\n")
    f.write(f"Matrix dimensions: {n_features} features x {n_cells} cells\n")
    f.write(f"Nonzero expression entries: {n_nonzero}\n")
    f.write("\nFeature types:\n")
    for name, count in sorted(feature_types.items()):
        f.write(f"  {name}: {count}\n")

print(f"Summary written to {output}")
