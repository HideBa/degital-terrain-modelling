import os
from matplotlib import pyplot as plt
from ptio import read_laz
from gftin import GFTIN
from preprocess import clip_pc, preprocess
import numpy as np
import laspy
import config as cfg

from lasinfo import las_info


def find_optimistic_params():
    file_path = preprocess("./py/data/69BZ2_19.las")
    out_dir = "./py/data/out/figure"

    # benchmark distance threshold
    # input1 = [
    #     {"dist_threshold": 1, "max_angle": 10, "cell_size": 100},
    #     {"dist_threshold": 3, "max_angle": 10, "cell_size": 100},
    #     {"dist_threshold": 5, "max_angle": 10, "cell_size": 100},
    #     {"dist_threshold": 8, "max_angle": 10, "cell_size": 100},
    #     {"dist_threshold": 10, "max_angle": 10, "cell_size": 100},
    #     {"dist_threshold": 20, "max_angle": 10, "cell_size": 100},
    # ]
    # accuracies, f1_scores = [], []
    # for params in input1:
    #     accuracy, f1_score = benchmark(
    #         file_path,
    #         params["dist_threshold"],
    #         params["max_angle"],
    #         params["cell_size"],
    #     )
    #     accuracies.append(accuracy)
    #     f1_scores.append(f1_score)
    # plot_benchmarks(
    #     accuracies,
    #     f1_scores,
    #     [d["dist_threshold"] for d in input1],
    #     "Distance threshold",
    #     out_dir,
    # )
    # input2 = [
    #     {"dist_threshold": 0.5, "max_angle": 10, "cell_size": 100},
    #     {"dist_threshold": 0.5, "max_angle": 20, "cell_size": 100},
    #     {"dist_threshold": 0.5, "max_angle": 30, "cell_size": 100},
    #     {"dist_threshold": 0.5, "max_angle": 40, "cell_size": 100},
    # ]
    # accuracies, f1_scores = [], []
    # for params in input2:
    #     accuracy, f1_score = benchmark(
    #         file_path,
    #         params["dist_threshold"],
    #         params["max_angle"],
    #         params["cell_size"],
    #     )
    #     accuracies.append(accuracy)
    #     f1_scores.append(f1_score)
    # plot_benchmarks(
    #     accuracies, f1_scores, [d["max_angle"] for d in input2], "Max Angle", out_dir
    # )
    # input3 = [
    #     {"dist_threshold": 5, "max_angle": 30, "cell_size": 5},
    #     {"dist_threshold": 5, "max_angle": 30, "cell_size": 30},
    #     {"dist_threshold": 5, "max_angle": 30, "cell_size": 60},
    #     {"dist_threshold": 5, "max_angle": 30, "cell_size": 90},
    #     {"dist_threshold": 5, "max_angle": 30, "cell_size": 120},
    # ]
    # accuracies, f1_scores = [], []
    # for params in input3:
    #     accuracy, f1_score = benchmark(
    #         file_path,
    #         params["dist_threshold"],
    #         params["max_angle"],
    #         params["cell_size"],
    #     )
    #     accuracies.append(accuracy)
    #     f1_scores.append(f1_score)
    # plot_benchmarks(
    #     accuracies, f1_scores, [d["cell_size"] for d in input3], "Cell size", out_dir
    # )

    benchmark(file_path, 5, 30, 90)


def plot_benchmarks(accuracies, f1_scores, param_values, param_name, out_dir):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    ax[0].plot(param_values, accuracies, label="Accuracy", color="blue")
    ax[1].plot(param_values, f1_scores, label="F1 Score", color="red")

    ax[0].set_title(f"Accuracy vs {param_name}")
    ax[1].set_title(f"F1 Score vs {param_name}")
    ax[0].set_xlabel(f"Parameter {param_name}")
    ax[1].set_xlabel(f"Parameter {param_name}")
    ax[0].set_ylabel("Accuracy")
    ax[1].set_ylabel("F1 Score")
    ax[0].set_xticks(param_values)
    ax[0].set_xticklabels(param_values)
    ax[1].set_xticks(param_values)
    ax[1].set_xticklabels(param_values)
    ax[0].legend()
    ax[1].legend()
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, f"benchmark_{param_name}.png"))


def benchmark(filepath, dist_threshold, max_angle, cell_size):
    las = read_laz(filepath)
    las_info(las)
    extent = cfg.EXTENT
    buffered_extent = [
        extent[0] - cell_size * 2,
        extent[1] - cell_size * 2,
        extent[2],
        extent[3] + cell_size * 2,
        extent[4] + cell_size * 2,
        extent[5],
    ]
    clip_pc(las, buffered_extent)
    las.add_extra_dim(
        laspy.ExtraBytesParams(
            name="is_ground",
            type=np.uint8,  # 0: not ground, 1: ground
        )
    )
    las.is_ground = np.zeros(len(las.points), dtype=np.uint8)

    gftin = GFTIN(las, cell_size, extent, debug=False)
    _ = gftin.ground_filtering(dist_threshold, max_angle)

    x_valid = (extent[0] <= las.points.x) & (extent[3] >= las.points.x)
    y_valid = (extent[1] <= las.points.y) & (extent[4] >= las.points.y)
    z_valid = (extent[2] <= las.points.z) & (extent[5] >= las.points.z)
    valid_indices = np.where(x_valid & y_valid & z_valid)[0]
    points = las.points[valid_indices]
    print("valid points: ", len(points))
    true_positives = points[(points.is_ground == 1) & (points.classification == 2)]
    true_negatives = points[(points.is_ground == 0) & (points.classification != 2)]
    false_positives = points[(points.is_ground == 1) & (points.classification != 2)]
    false_negatives = points[(points.is_ground == 0) & (points.classification == 2)]

    print("true_positives: ", len(true_positives))
    print("true_negatives: ", len(true_negatives))
    print("false_positives: ", len(false_positives))
    print("false_negatives: ", len(false_negatives))
    accuracy = (len(true_positives) + len(true_negatives)) / len(points)
    precision = len(true_positives) / (len(true_positives) + len(false_positives))
    recall = len(true_positives) / (len(true_positives) + len(false_negatives))
    f1_score = 2 * (precision * recall) / (precision + recall)

    print("=============benchmark==============")
    print("true_positives: ", len(true_positives), " / ", len(points))
    print("true_negatives: ", len(true_negatives), " / ", len(points))
    print("false_positives: ", len(false_positives), " / ", len(points))
    print("false_negatives: ", len(false_negatives), " / ", len(points))
    print("accuracy", accuracy * 100, "%")
    print("precision", precision)
    print("recall", recall)
    print("f1_score", f1_score)
    print("====================================")

    return (accuracy, f1_score)


if __name__ == "__main__":
    find_optimistic_params()
