import re
from typing import List, Optional
import pandas as pd
import json


def day_block_parser(day_block: str):
    pattern = re.compile(
        r'^'
        r'([^:]+):'  # 1
        r'([^:]+):'  # 2
        r'([^:]+):'  # 3
        r'([^:]+):'  # 4
        r'([^:]+):'  # 5
        r'([^:]+):'  # 6
        r'([^:]+):'  # 7
        r'([^:]+):'  # 8
        r'([^:]+):'  # 9
        r'([^:]+):'  # 10
        r'([^:]+):'  # 11
        r'(.+):'  # 12 — allow internal colons here
        r'([^:]+)$'  # 13 — last column
    )

    match = pattern.match(day_block)
    if match:
        return match.groups()
    else:
        raise ValueError(f"Invalid day block: {day_block}")


class PreProcessCsv:
    _header_block_length: int = 26
    _data_A2_period: str = '1_10'
    _data_A3_period: str = '11_20'
    _data_A4_period: str = '21_30'
    _data_A4_period_ext: str = '21_31'

    def __init__(
            self,
            file_path: Optional[str] = None,
            encoding: Optional[str] = 'utf-8',
    ):
        self.file_path = file_path
        self.encoding = encoding

    def _read_file(self):
        return pd.read_csv(
            self.file_path,
            header=None,
            encoding=self.encoding,
            engine='python',
            encoding_errors="ignore",
        )

    def _process_format(self):
        df = self._read_file()

        group_by_composite: dict = {}

        for line, row in enumerate(df.itertuples(index=False), start=1):
            _ROW_LINE_ = line
            _ROW_DATA_ = str(row[0]).strip()
            _ROW_DATA_SPLIT_ = _ROW_DATA_.split(":")

            # GET SET ID and COMPOSITE ID
            _ROW_SET_ID_ = _ROW_DATA_SPLIT_[0]
            _ROW_COMPOSITE_ID_ = _ROW_DATA_SPLIT_[1]

            # Build the row composite id
            _REBUILD_ROW_COMPOSITE_ID_ = f"{_ROW_COMPOSITE_ID_}:{_ROW_SET_ID_}"

            # Get the offset data without using the split to maintain the pre-split data
            _PRE_SPLIT_OFFSET_ROW_DATA_ = _ROW_DATA_[len(_REBUILD_ROW_COMPOSITE_ID_):-1]

            if _ROW_COMPOSITE_ID_ not in group_by_composite:
                group_by_composite[_ROW_COMPOSITE_ID_] = {}

            if _ROW_SET_ID_ == "A1":
                # TODO: process A1
                # since the A1 doesn't have uncertainty in inputs unlike A2 ~ A4
                # we can just split it normally

                # first left trim and remove ":" since we subtracted the composite id from the data
                # then split the data using ":" as the delimiter
                _A1_ROW_DATA_SPLIT = _PRE_SPLIT_OFFSET_ROW_DATA_.lstrip(":").split(":")
                _A1_ROW_DATA_SPLIT_LEN = len(_A1_ROW_DATA_SPLIT)

                group_by_composite[_ROW_COMPOSITE_ID_][_ROW_SET_ID_] = dict(
                    _i=_ROW_LINE_,
                    _r=_A1_ROW_DATA_SPLIT,
                    _rl=_A1_ROW_DATA_SPLIT_LEN,
                    _el=self._header_block_length,
                    _vl=_A1_ROW_DATA_SPLIT_LEN == self._header_block_length,
                )
                pass
            else:
                # TODO: process A2 ~ A4
                # attach day period indicator
                day_period_indicator = "?_?"

                if _ROW_SET_ID_ == 'A2':
                    day_period_indicator = self._data_A2_period
                elif _ROW_SET_ID_ == 'A3':
                    day_period_indicator = self._data_A3_period
                elif _ROW_SET_ID_ == 'A4':
                    # TODO: handle A4 if 30 or 31
                    day_period_indicator = self._data_A4_period

                group_by_composite[_ROW_COMPOSITE_ID_][_ROW_SET_ID_] = dict(
                    _i=_ROW_LINE_,
                    _r=_PRE_SPLIT_OFFSET_ROW_DATA_,
                    _dp=day_period_indicator,
                )
                pass

        print(json.dumps(group_by_composite, indent=4, ensure_ascii=False))

    def process_to_workable_format(self):
        return self._process_format()
