import argparse
from pprint import pprint
from data_set_initializer import DataSetInitializer
from pre_process_csv import PreProcessCsv


def main():
    parser = argparse.ArgumentParser(description='DigiViewer')
    parser.add_argument('--slim', action='store_true')
    parser.add_argument('--pre_process', action='store_true')

    args = parser.parse_args()

    # args var
    _is_slim_ = args.slim
    _call_pre_process_csv_ = args.pre_process

    if _is_slim_:
        print("Using slim data set.")
        data_set_initializer = DataSetInitializer(_is_slim_)
    else:
        print("Using full data set.")
        data_set_initializer = DataSetInitializer(False)

    _data_type, _data_path, _data_encoding = data_set_initializer.get_data_config()

    pre_processor = PreProcessCsv(file_path=_data_path, encoding=_data_encoding)

    if _call_pre_process_csv_:
        result = pre_processor.to_readable_format()
        pprint(result, width=200, compact=True)


if __name__ == "__main__":
    main()