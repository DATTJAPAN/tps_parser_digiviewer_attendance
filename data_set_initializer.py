import os
from typing import Optional, Tuple
from charset_normalizer import detect, from_path


class DataSetInitializer:
    """
    Initializes dataset configuration and file path.
    Supports slim, full, or custom datasets.
    """
    # Default dataset paths
    _default_small_data_set_path = './data/mock/data_small.csv'
    _default_big_data_set_path = 'data/mock/data.csv'
    _default_file_encoding = 'cp932'  # 'cp932', 'shift_jis', etc.

    def __init__(self, use_slim_data_set: Optional[bool] = None, desired_encoding: Optional[str] = 'cp932') -> None:
        """
        Initialize the dataset configuration.
        :param use_slim_data_set:
            True -> use small dataset
            False -> use full dataset
            None -> leave dataset uninitialized
        """
        # self.

        if desired_encoding is None:
            self.desired_encoding = self._default_file_encoding
        else:
            self.desired_encoding = desired_encoding

        if use_slim_data_set is None:
            self.data_set_type = None
            self.data_set_path = None
        else:
            self.data_set_type = 'slim' if use_slim_data_set else 'full'
            self.data_set_path = os.path.abspath(
                self._default_small_data_set_path if use_slim_data_set else self._default_big_data_set_path
            )

    def _ensure_encoding_match_desired(self):
        result = from_path(self.data_set_path).best()
        file_encoding = result.encoding

        print(f"")
        print(f"==================================")
        print(f"Detected encoding: {file_encoding}")
        print(f"Expected encoding: {self.desired_encoding}")
        print(f"==================================")
        print(f"")

        if file_encoding != self.desired_encoding:
            raise Exception(f"Expected encoding {self.desired_encoding} but got {result.encoding}")
        else:
            return file_encoding

    def set_custom_data_set(self, path: str):
        """
        Set a custom dataset path.
        :param path: Path to the custom dataset file
        """
        self.data_set_type = 'custom'
        self.data_set_path = os.path.abspath(path)

    def get_data_config(self) -> tuple[str, str, str]:
        """
        Retrieve the dataset configuration.
        :return: Tuple of (dataset type, absolute file path)
        :raises Exception: if no dataset is set
        """
        if self.data_set_type is None or self.data_set_path is None:
            raise Exception("No dataset is set.")

        return self.data_set_type, self.data_set_path, self._ensure_encoding_match_desired()