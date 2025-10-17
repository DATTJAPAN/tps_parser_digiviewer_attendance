from typing import List, Optional
import pandas as pd
from pydantic import BaseModel


class PreProcessA1Header(BaseModel):
    record_composite_id: str  # 1
    uf_2__: str  # 2 - part of the composite id
    dispatch_code: str  # 3
    contract_code: str  # 4
    staff_id: str  # 5
    target_year_month: str  # 6
    date_period_range: str  # 7
    dispatch_src: str  # 8
    dispatch_name: str  # 9
    uf_11__: Optional[str] = None  # 10
    staff_name: Optional[str] = None  # 11
    uf_13__: Optional[str] = None  # 12
    uf_14__: Optional[str] = None  # 13
    total_work_time: Optional[str] = None  # 14 - total_work_time
    overtime_total_time: Optional[str] = None  # 15 - overtime_total_time
    uf_17__: Optional[str] = None  # 16
    uf_18__: Optional[str] = None  # 17
    uf_19__: Optional[str] = None  # 18
    uf_20__: Optional[str] = None  # 19
    uf_21__: Optional[str] = None  # 20
    uf_22__: Optional[str] = None  # 21
    uf_23__: Optional[str] = None  # 22
    uf_24__: Optional[str] = None  # 23
    uf_25__: Optional[str] = None  # 24
    approver_name: Optional[str] = None
    uf_27: Optional[str] = None  # 27


class PreProcessA2A3A4Header(BaseModel):
    day: str  # 1
    uf_2__: int  # 2
    day_of_week: str  # 3
    uf_4__: Optional[int] = None  # 4
    start_working_time_mins: int = 0  # 5
    end_working_time_mins: int = 0  # 6
    break_time_mins: int = 0  # 7
    day_notification_category: Optional[str] = None  # 8
    work_time_mins: int = 0  # 9
    work_overtime_mins: int = 0  # 10
    work_late_overtime_mins: int = 0  # 11

    #  we modified the idx 13 to 12 so that the last element is the extra remarks or notes
    uf_12__: Optional[int] = None  # 12
    extra_remarks_or_notes: Optional[str] = None  # 13


class PreProcessCsv:
    _header_block_length: int = 26
    _data_A2_period: str = '1_10'
    _data_A3_period: str = '11_20'
    _data_A4_period: str = '21_30'
    _data_A4_period_ext: str = '21_31'
    _data_anchor_point: List[str] = ["月", "火", "水", "木", "金", "土", "日"]

    def __init__(
            self,
            file_path: Optional[str] = None,
            encoding: Optional[str] = 'cp932',
    ):
        self.file_path = file_path
        self.encoding = encoding

    def _read_file(self):
        return pd.read_csv(
            self.file_path,
            header=None,
            encoding=self.encoding,
            # engine='python',
            encoding_errors="ignore",
        )

    def _process_a1_row(self, row: List[str]) -> dict:
        field_names = list(PreProcessA1Header.model_fields.keys())

        if len(row) < len(field_names):
            row = row + [None] * (len(field_names) - len(row))

        data_dict = dict(zip(field_names, row))
        model = PreProcessA1Header(**data_dict)
        return model.model_dump()

    def _process_a2_a3_a4_row(self, row: List[str | int | None]) -> dict:
        field_names = list(PreProcessA2A3A4Header.model_fields.keys())
        num_fields = len(field_names)

        # If the row has more items than expected → merge extras into last field (index 12)
        if len(row) > num_fields:
            extras = ''.join(str(x) for x in row[num_fields - 1:] if x not in [None, ''])
            # Append extras to existing 13th element (index 12)
            row[num_fields - 1] = (
                f"{row[num_fields - 1]}{extras}" if row[num_fields - 1] not in [None, ''] else extras
            )
            # Trim to match expected model fields
            row = row[:num_fields]

        # If the row is shorter → pad with None
        elif len(row) < num_fields:
            row = row + [None] * (num_fields - len(row))

        data_dict = dict(zip(field_names, row))
        model = PreProcessA2A3A4Header(**data_dict)
        return model.model_dump()

    def _modify_day_block(self, block: list[str | int | None] | None = None):
        if block is None:
            raise ValueError("Block cannot be empty")

        last_element = block[-1]
        block.insert(10, last_element)
        block.pop()

        return block

    def _day_block_to_dict(self, day_block: List[str | int | None]):
        return self._process_a2_a3_a4_row(day_block)

    def _extract_days_block(self, day_row: List[str] = None, parent_row: List[str] = None):
        if day_row is None or parent_row is None:
            raise ValueError("Day row and parent row cannot be empty")

        _DAY_BLOCK_ = []
        _DAY_BLOCK_AS_DICT_ = []

        # Get the boundaries properly
        # our anchor of the is the japanese "days" -> 月,火,水,木,金,土,日
        _DAY_BOUNDARY_TRACKER_ = {"s": -1, "ns": -1}
        for _index, _value in enumerate(day_row):
            anchor_found = _value in self._data_anchor_point

            # Check if the tracker is fully partner
            if _DAY_BOUNDARY_TRACKER_["s"] != -1 and _DAY_BOUNDARY_TRACKER_["ns"] != -1:
                modified_row = self._modify_day_block(
                    parent_row[_DAY_BOUNDARY_TRACKER_["s"]:_DAY_BOUNDARY_TRACKER_["ns"]]
                )

                _DAY_BLOCK_.append(modified_row)
                _DAY_BLOCK_AS_DICT_.append(self._day_block_to_dict(modified_row))
                # Change the s will get the ns then ns -> -1 so we can start over the other data
                _DAY_BOUNDARY_TRACKER_["s"] = _DAY_BOUNDARY_TRACKER_["ns"]
                _DAY_BOUNDARY_TRACKER_["ns"] = -1

            if anchor_found:
                # Ensure first the first "s" is set"
                if _DAY_BOUNDARY_TRACKER_["s"] == -1:
                    _DAY_BOUNDARY_TRACKER_["s"] = _index
                else:
                    if _DAY_BOUNDARY_TRACKER_["ns"] == -1:
                        _DAY_BOUNDARY_TRACKER_["ns"] = _index

        # at the last iteration
        if _DAY_BOUNDARY_TRACKER_["s"] != -1 and _DAY_BOUNDARY_TRACKER_["ns"] == -1:
            _MODIFIED_DAY_BLOCK = self._modify_day_block(parent_row[_DAY_BOUNDARY_TRACKER_["s"]:])

            _DAY_BLOCK_.append(_MODIFIED_DAY_BLOCK)
            _DAY_BLOCK_AS_DICT_.append(self._day_block_to_dict(_MODIFIED_DAY_BLOCK))

        return _DAY_BLOCK_, _DAY_BLOCK_AS_DICT_

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

            # Remove the ":" in the beginning of the data
            _PRE_SPLIT_OFFSET_ROW_DATA_STRIP_ = _PRE_SPLIT_OFFSET_ROW_DATA_.lstrip(":")

            if _ROW_COMPOSITE_ID_ not in group_by_composite:
                group_by_composite[_ROW_COMPOSITE_ID_] = {}

            if _ROW_SET_ID_ == "A1":
                # since the A1 doesn't have uncertainty in inputs unlike A2 ~ A4
                # we can just split it normally

                # first left trim and remove ":" since we subtracted the composite id from the data
                # then split the data using ":" as the delimiter
                _A1_ROW_DATA_SPLIT = _PRE_SPLIT_OFFSET_ROW_DATA_STRIP_.split(":")
                _A1_ROW_DATA_SPLIT_LEN = len(_A1_ROW_DATA_SPLIT)

                group_by_composite[_ROW_COMPOSITE_ID_][_ROW_SET_ID_] = {
                    "_i": _ROW_LINE_,
                    "_r": _A1_ROW_DATA_SPLIT,
                    "_rd": self._process_a1_row(_A1_ROW_DATA_SPLIT),
                    "_rl": _A1_ROW_DATA_SPLIT_LEN,
                    "_el": self._header_block_length,
                    "_vl": _A1_ROW_DATA_SPLIT_LEN == self._header_block_length,
                }

            else:
                # attach day period indicator
                day_period_indicator = "?_?"

                if _ROW_SET_ID_ == 'A2':
                    day_period_indicator = self._data_A2_period
                elif _ROW_SET_ID_ == 'A3':
                    day_period_indicator = self._data_A3_period
                elif _ROW_SET_ID_ == 'A4':
                    day_period_indicator = self._data_A4_period_ext

                _DAY_ROW_DATA_ = _PRE_SPLIT_OFFSET_ROW_DATA_STRIP_
                _DAY_ROW_DATA_SPLIT_ = _DAY_ROW_DATA_.split(":")

                extract_day_block, extracted_day_block_as_dict = self._extract_days_block(
                    day_row=_DAY_ROW_DATA_SPLIT_,
                    parent_row=_ROW_DATA_SPLIT_
                )

                group_by_composite[_ROW_COMPOSITE_ID_][_ROW_SET_ID_] = {
                    "_i": _ROW_LINE_,
                    "_dp": day_period_indicator,
                    "_db": extract_day_block,
                    "_dbd": extracted_day_block_as_dict
                }

        return group_by_composite

    def to_readable_format(self):
        return self._process_format()
