import argparse
from csv_reader import CsvReader
import sys
from pprint import pprint
import json
from data_set_initializer import DataSetInitializer
from pre_process_csv import PreProcessCsv


def main():
    parser = argparse.ArgumentParser(description='DigiViewer')
    parser.add_argument('--slim', action='store_true')
    parser.add_argument('--vectorized', action='store_true')

    args = parser.parse_args()

    # args var
    _is_slim_ = args.slim
    _call_vectorized_csv_reader_ = args.vectorized

    if _is_slim_:
        print("Using slim data set.")
        data_set_initializer = DataSetInitializer(_is_slim_)
    else:
        print("Using full data set.")
        data_set_initializer = DataSetInitializer(False)



    _data_type, _data_path, _data_encoding = data_set_initializer.get_data_config()

    pre_processor = PreProcessCsv(
        file_path=_data_path,
        encoding='utf-8'
    )

    if _call_vectorized_csv_reader_:
        result = pre_processor.process_to_workable_format()



if __name__ == "__main__":
    main()