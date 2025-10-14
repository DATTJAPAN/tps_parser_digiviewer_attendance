import os
from typing import Optional, Tuple

class DataSetInitializer:
    """
    Initializes dataset configuration and file path.
    Supports slim, full, or custom datasets.
    """
    # Default dataset paths
    _default_small_data_set_path = './data/mock/data_small.csv'
    _default_big_data_set_path = './data/mock/data.csv'
    _default_file_encoding = 'ms932'  # 'cp932', 'shift_jis', etc.

    def __init__(self, use_slim_data_set: Optional[bool] = None):
        """
        Initialize the dataset configuration.
        :param use_slim_data_set:
            True -> use small dataset
            False -> use full dataset
            None -> leave dataset uninitialized
        """
        if use_slim_data_set is None:
            self.data_set_type = None
            self.data_set_path = None
        else:
            self.data_set_type = 'slim' if use_slim_data_set else 'full'
            self.data_set_path = os.path.abspath(
                self._default_small_data_set_path if use_slim_data_set else self._default_big_data_set_path
            )

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

        return self.data_set_type, self.data_set_path, self._default_file_encoding
