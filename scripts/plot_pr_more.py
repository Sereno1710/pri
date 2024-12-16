#!/usr/bin/env python3

import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np

def calculate_pr(y_pred, y_true):
    precision = []
    recall = []
    relevant_ranks = []
    relevant_count = 0

    for i in range(1, len(y_pred) + 1):
        if y_pred[i - 1] in y_true:
            relevant_count += 1
            relevant_ranks.append(relevant_count / i)

        precision.append(relevant_count / i)
        recall.append(relevant_count / len(y_true))

    map_score = np.sum(relevant_ranks) / len(y_true) if relevant_ranks else 0
    recall_levels = np.linspace(0.0, 1.0, 11)
    interpolated_precision = [
        max([p for p, r in zip(precision, recall) if r >= r_level], default=0)
        for r_level in recall_levels
    ]
    auc_score = np.trapz(interpolated_precision, recall_levels)

    return recall_levels, interpolated_precision, map_score, auc_score

def main(qrels_file, outputs):
    with open(qrels_file, "r") as f:
        y_true = {line.strip().split()[2] for line in f}

    plt.figure()

    for output in outputs:
        pred_file, label, color = output.split(",")
        with open(pred_file, "r") as f:
            y_pred = [line.strip().split()[2] for line in f]

        if not y_pred or not y_true:
            print(f"Error: No predictions or qrels found in {pred_file}.")
            sys.exit(1)

        recall_levels, interp_precision, map_score, auc_score = calculate_pr(y_pred, y_true)

        plt.plot(
            recall_levels,
            interp_precision,
            drawstyle="steps-post",
            label=f"{label} (AvP: {map_score:.4f}, AUC: {auc_score:.4f})",
            color=color,
            linewidth=1,
        )

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend(loc="lower left", prop={"size": 10})
    plt.title("Precision-Recall Curve")
    plt.savefig("evaluation/p-r_curves/combined_prec_rec.png", format="png", dpi=300)
    print("Combined Precision-Recall plot saved to evaluation/p-r_curves/combined_prec_rec.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Precision-Recall curves for multiple systems from Solr results and qrels."
    )
    parser.add_argument("--qrels", type=str, required=True, help="Path to the qrels file.")
    parser.add_argument(
        "--outputs",
        nargs="+",
        required=True,
        help="List of prediction files, labels, and colors (format: 'file,label,color').",
    )
    args = parser.parse_args()
    main(args.qrels, args.outputs)
