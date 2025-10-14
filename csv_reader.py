import os
import json
import chardet
import pandas as pd
from typing import List


class CsvReader:
    csv_small_file_path = './data_small.csv'
    csv_big_file_path = './data.csv'
    csv_encoding = 'ms932'  # 'cp932' or 'shift_jis' or 'shift_jis_2004' or 'ms932'

    def __init__(self, slim: bool = False) -> None:
        # Store absolute paths in instance variables
        self.csv_small_file_path_abs = os.path.abspath(self.csv_small_file_path)
        self.csv_big_file_path_abs = os.path.abspath(self.csv_big_file_path)
        self.use_slim_file = slim

    def _get_exact_file_to_use(self):
        return self.csv_small_file_path_abs if self.use_slim_file else self.csv_big_file_path_abs

    def _open_and_read_csv_file(self):
        with open(self._get_exact_file_to_use(), 'rb') as f:
            raw = f.read()
            result = chardet.detect(raw)

            # Add defaults
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', -1)
            language = result.get('language') or 'Unknown'

            return encoding, confidence, language

    def _internal_display_selected_data_banner(self):
        encoding, confidence, language = self._open_and_read_csv_file()

        print("")
        print("===========================")
        print("Reading: ")
        print("csv path:", self._get_exact_file_to_use())
        print("encoding:", encoding)
        print("confidence:", confidence)
        print("language:", language)
        print("===========================")
        print("")

    def _internal_display_processing_banner(self):
        print("")
        print("===========================")
        print("Processing......")
        print("===========================")
        print("")

    def _open_csv_file(self):
        self._internal_display_selected_data_banner()

        return pd.read_csv(
            self._get_exact_file_to_use(),
            header=None,
            encoding=self.csv_encoding,
            engine='python',
            encoding_errors="ignore",  # ignore invalid characters
        )

    def handle_get_rows(self, row_ids: List[str], parse_rows: bool = False):
        """
        Currently can filter what type of row type to display

        ex. if row_ids = A1, A2 -> print only A1 and A2

        :param row_ids:
        :param parse_rows:
        :return:

        """
        df = self._open_csv_file()
        self._internal_display_processing_banner()

        # since the data has a composite id we can use it to maintain the data integrity
        integrity_holder: dict = {}
        # trigger only if selected row_ids is more than 1
        should_validate_integrity = len(row_ids) > 1
        # if there's an error within the data we should report the line and row of data


        # ! Start Here !
        # Loop through the rows
        for line, row in enumerate(df.itertuples(index=False)):
            _ROW_LINE_ = line + 1
            _ROW_DATA_ = row[0]
            _COMPOSITE_ID_ = _ROW_DATA_.split(":")[1]

            for row_id in row_ids:
                if _ROW_DATA_.startswith(f"{row_id}:"):
                    if should_validate_integrity:
                        # Ensure the composite id is in the integrity holder
                        if _COMPOSITE_ID_ not in integrity_holder:
                            integrity_holder[_COMPOSITE_ID_] = {}

                        integrity_holder[_COMPOSITE_ID_][row_id] = dict(
                            _i=_ROW_LINE_,
                            _r=_ROW_DATA_,
                        )
                    else:
                        print(f"line: {_ROW_LINE_}")
                        print(f"data: {_ROW_DATA_}")

        if should_validate_integrity:
            print(json.dumps(integrity_holder, indent=4, ensure_ascii=False))