import dataclasses


@dataclasses.dataclass
class AppConfig:
    save_folder_path: str = None
    image_folder_path: str = None

    class_name: str = None
    rect_box_shape: tuple = None
    last_opened_image: str = None
