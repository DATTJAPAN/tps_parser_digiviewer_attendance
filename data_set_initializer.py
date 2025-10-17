import os
from typing import Optional, Tuple
from charset_normalizer import from_path


class DataSetInitializer:
    """
    Initializes dataset configuration and file path.
    Supports slim, full, or custom datasets.
    """
    DEFAULT_SMALL_DATASET_PATH = './data/mock/data_small.csv'
    DEFAULT_BIG_DATASET_PATH = 'data/mock/data_30.csv'
    DEFAULT_FILE_ENCODING = 'cp932'

    def __init__(
            self,
            use_slim_data_set: Optional[bool] = None,
            desired_encoding: Optional[str] = 'cp932'
    ) -> None:
        """
        Initialize the dataset configuration.

        Args:
            use_slim_data_set: True for small dataset, False for full dataset, None for uninitialized
            desired_encoding: Expected file encoding (default: cp932)
        """
        self.desired_encoding = desired_encoding or self.DEFAULT_FILE_ENCODING

        if use_slim_data_set is None:
            self.data_set_type = None
            self.data_set_path = None
        else:
            self._initialize_default_dataset(use_slim_data_set)

    def _initialize_default_dataset(self, use_slim: bool) -> None:
        """Initialize with default slim or full dataset."""
        self.data_set_type = 'slim' if use_slim else 'full'
        dataset_path = self.DEFAULT_SMALL_DATASET_PATH if use_slim else self.DEFAULT_BIG_DATASET_PATH
        self.data_set_path = os.path.abspath(dataset_path)

    def _validate_encoding(self) -> str:
        """
        Validate that file encoding matches desired encoding.

        Returns:
            str: The detected file encoding

        Raises:
            Exception: If encoding doesn't match expected encoding
        """
        result = from_path(self.data_set_path).best()
        detected_encoding = result.encoding

        print(f"\n{'=' * 43}")
        print(f"Detected encoding: {detected_encoding}")
        print(f"Expected encoding: {self.desired_encoding}")
        print(f"{'=' * 43}\n")

        if detected_encoding != self.desired_encoding:
            raise Exception(
                f"Expected encoding {self.desired_encoding} but got {detected_encoding}"
            )

        return detected_encoding

    def set_custom_data_set(self, path: str) -> None:
        """
        Set a custom dataset path.

        Args:
            path: Path to the custom dataset file
        """
        self.data_set_type = 'custom'
        self.data_set_path = os.path.abspath(path)

    def get_data_config(self) -> Tuple[str, str, str]:
        """
        Retrieve the dataset configuration.

        Returns:
            Tuple of (dataset type, absolute file path, encoding)

        Raises:
            Exception: If no dataset is set
        """
        if self.data_set_type is None or self.data_set_path is None:
            raise Exception("No dataset is set.")

        return self.data_set_type, self.data_set_path, self._validate_encoding()