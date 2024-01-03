import os
from matplotlib import pyplot as plt
from ptio import read_laz
from gftin import GFTIN
from preprocess import remove_outliers
from step3 import GFTIN_CELL_SIZE
import numpy as np
import laspy


def find_optimistic_params():
    if not os.path.isfile("./py/data/out/thinned_without_outliers.las"):
        remove_outliers(
            "./py/data/thinned.las",
            "./py/data/out/thinned_without_outliers.las",
        )

    file_path = "./py/data/out/thinned_without_outliers.las"
    out_dir = "./py/data/out/figure"

    # benchmark distance threshold
    input = [
        {
            "dist_threshold": 0.5,
            "max_angle": 10,
        },
        {
            "dist_threshold": 1,
            "max_angle": 10,
        },
        {
            "dist_threshold": 2,
            "max_angle": 10,
        },
        {
            "dist_threshold": 5,
            "max_angle": 10,
        },
        {
            "dist_threshold": 10,
            "max_angle": 10,
        },
        {
            "dist_threshold": 20,
            "max_angle": 10,
        },
        {
            "dist_threshold": 30,
            "max_angle": 10,
        },
    ]
    accuracies, f1_scores = [], []
    for params in input:
        accuracy, f1_score = benchmark(
            file_path, params["dist_threshold"], params["max_angle"]
        )
        accuracies.append(accuracy)
        f1_scores.append(f1_score)
    plot_benchmarks(accuracies, f1_scores, "Distance Threshold", out_dir)

    input2 = [
        {
            "dist_threshold": 0.5,
            "max_angle": 5,
        },
        {
            "dist_threshold": 0.5,
            "max_angle": 20,
        },
        {
            "dist_threshold": 0.5,
            "max_angle": 30,
        },
        {
            "dist_threshold": 0.5,
            "max_angle": 40,
        },
    ]
    accuracies, f1_scores = [], []
    for params in input2:
        accuracy, f1_score = benchmark(
            file_path, params["dist_threshold"], params["max_angle"]
        )
        accuracies.append(accuracy)
        f1_scores.append(f1_score)
    plot_benchmarks(accuracies, f1_scores, "Max Angle", out_dir)


def plot_benchmarks(accuracies, f1_scores, param_name, out_dir):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    ax[0].plot(range(len(accuracies)), accuracies, label="Accuracy", color="blue")
    ax[1].plot(range(len(f1_scores)), f1_scores, label="F1 Score", color="red")

    ax[0].set_title("Accuracy vs Parameter")
    ax[1].set_title("F1 Score vs Parameter")
    ax[0].set_xlabel(f"Parameter {param_name}")
    ax[1].set_xlabel(f"Parameter {param_name}")
    ax[0].set_ylabel("Accuracy")
    ax[1].set_ylabel("F1 Score")
    ax[0].legend()
    ax[1].legend()
    plt.tight_layout()
    # plt.show()
    fig.savefig(os.path.join(out_dir, f"benchmark_{param_name}.png"))


def benchmark(
    filepath,
    dist_threshold,
    max_angle,
):
    las = read_laz(filepath)
    las.add_extra_dim(
        laspy.ExtraBytesParams(
            name="is_ground",
            type=np.uint8,  # 0: not ground, 1: ground
        )
    )
    las.is_ground = np.zeros(len(las.points), dtype=np.uint8)

    bbox = np.concatenate((las.header.mins, las.header.maxs))
    gftin = GFTIN(las, GFTIN_CELL_SIZE, bbox)

    _ = gftin.ground_filtering(dist_threshold, max_angle)
    points = las.points

    print("number of ground", len(points[points.classification == 2]))

    true_positives = points[(points.is_ground == 1) & (points.classification == 2)]
    true_negatives = points[(points.is_ground == 0) & (points.classification != 2)]
    false_positives = points[(points.is_ground == 1) & (points.classification != 2)]
    false_negatives = points[(points.is_ground == 0) & (points.classification == 2)]

    accuracy = (len(true_positives) + len(true_negatives)) / len(points)
    print("accuracy", accuracy)

    precision = len(true_positives) / (len(true_positives) + len(false_positives))
    recall = len(true_positives) / (len(true_positives) + len(false_negatives))

    f1_score = 2 * (precision * recall) / (precision + recall)
    print("f1_score", f1_score)

    return (accuracy, f1_score)


if __name__ == "__main__":
    find_optimistic_params()
