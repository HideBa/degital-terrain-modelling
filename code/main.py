import os

import config as cfg
import step3
import step4
import step5
from preprocess import preprocess


def main():
    processed_file = preprocess(cfg.INPUT_LAS)
    if not os.path.isfile(cfg.STEP3_OUTPUT):
        step3.create_dtm(processed_file, cfg.STEP3_OUTPUT)
    if not os.path.isfile(cfg.STEP4_OUTPUT):
        step4.extract_vegetation(processed_file, cfg.STEP4_OUTPUT)

    step5.create_chm(
        cfg.STEP3_OUTPUT,
        cfg.STEP4_OUTPUT,
        cfg.STEP5_OUTPUT,
    )


if __name__ == "__main__":
    main()
