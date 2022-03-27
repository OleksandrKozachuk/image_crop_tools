import sys

from PyQt5.QtWidgets import QApplication

from source.image_crop_tool import ImageCropTool
from source.modules.logger import LoggerConfigurator


def _get_parser():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=" Image crop tool ")
    parser.add_argument('-cfg', '--config', type=str, default="./data/config.json", help='project config')

    return parser


def _parse_config(config_file: str) -> dict:
    import json
    from os import path

    if not path.exists(config_file):
        raise FileExistsError(f"File '{config_file}' is not exists.")

    with open(config_file) as data_file:
        config = json.load(data_file)
    return config


def main():
    # initialize logger
    LoggerConfigurator().set_level_warning().add_console().add_timed_rotating()

    app = QApplication(sys.argv)
    main_window = ImageCropTool(app_config=app_config)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # parsing args
    args = _get_parser().parse_args(args=None)
    app_config = _parse_config(args.config)

    main()
