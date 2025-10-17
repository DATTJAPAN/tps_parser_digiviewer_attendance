import argparse
import timeit
from pprint import pprint

from data_set_initializer import DataSetInitializer
from pre_process_csv import PreProcessCsv


def parse_arguments() -> argparse.Namespace:
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(
        description='DigiViewer TPS Parser for Attendance Data'
    )
    parser.add_argument(
        '--slim',
        action='store_true',
        help='Use slim/small dataset for testing'
    )
    parser.add_argument(
        '--dataset_path',
        type=str,
        default=None,
        help='Path to custom dataset file'
    )
    parser.add_argument(
        '--pre_process',
        action='store_true',
        help='Run pre-processing and display results'
    )

    return parser.parse_args()


def initialize_dataset(args: argparse.Namespace) -> DataSetInitializer:
    """
    Initialize the dataset based on command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        DataSetInitializer: Configured dataset initializer
    """
    if args.dataset_path:
        print(f"\nUsing custom dataset: {args.dataset_path}")
        initializer = DataSetInitializer()
        initializer.set_custom_data_set(args.dataset_path)
    elif args.slim:
        print("\nUsing slim dataset.")
        initializer = DataSetInitializer(use_slim_data_set=True)
    else:
        print("\nUsing full dataset.")
        initializer = DataSetInitializer(use_slim_data_set=False)

    return initializer


def run_preprocessing(pre_processor: PreProcessCsv) -> None:
    """
    Run the preprocessing and display results with timing information.

    Args:
        pre_processor: Configured PreProcessCsv instance
    """

    def run_parser():
        result = pre_processor.to_readable_format()
        pprint(result, sort_dicts=False, width=200, compact=True)

    # Measure execution time
    execution_time = timeit.timeit(run_parser, number=1)

    print(f"\n{'=' * 49}")
    print(f"Execution time: {execution_time:.4f} seconds")
    print(f"{'=' * 49}\n")


def main() -> None:
    """Main entry point for the DigiViewer TPS Parser."""
    args = parse_arguments()

    # Initialize dataset
    data_initializer = initialize_dataset(args)
    data_type, data_path, data_encoding = data_initializer.get_data_config()

    # Initialize preprocessor
    pre_processor = PreProcessCsv(file_path=data_path, encoding=data_encoding)

    # Run preprocessing if requested
    if args.pre_process:
        run_preprocessing(pre_processor)


if __name__ == "__main__":
    main()
