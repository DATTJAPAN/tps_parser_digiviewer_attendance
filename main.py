import argparse
from pprint import pprint, PrettyPrinter
from data_set_initializer import DataSetInitializer
from pre_process_csv import PreProcessCsv
import timeit


def main():
    parser = argparse.ArgumentParser(description='DigiViewer')
    parser.add_argument('--slim', action='store_true')
    parser.add_argument('--dataset_path', action='store', type=str, default=None)
    parser.add_argument('--pre_process', action='store_true')

    args = parser.parse_args()

    # args var
    _is_slim_ = args.slim
    _is_trying_custom_dataset_ = args.dataset_path is not None
    _call_pre_process_csv_ = args.pre_process

    if _is_trying_custom_dataset_:
        print(f"\nUsing custom data set: {_is_trying_custom_dataset_}")
        data_set_initializer = DataSetInitializer()
        data_set_initializer.set_custom_data_set(args.dataset_path)
    elif _is_slim_:
        print("\nUsing slim data set.")
        data_set_initializer = DataSetInitializer(_is_slim_)
    else:
        print("\nUsing full data set.")
        data_set_initializer = DataSetInitializer(False)

    _data_type, _data_path, _data_encoding = data_set_initializer.get_data_config()

    pre_processor = PreProcessCsv(file_path=_data_path, encoding=_data_encoding)

    if _call_pre_process_csv_:
        # Define the callable
        def run_parser():
            result = pre_processor.to_readable_format()
            pprint(result, sort_dicts=False, width=200, compact=True)

        # Measure the actual execution
        execution_time = timeit.timeit(run_parser, number=1)

        print("")
        print("=================================================")
        print(f"Execution time: {execution_time:.4f} seconds")
        print("=================================================")
        print("")


if __name__ == "__main__":
    main()