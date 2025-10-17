from typing import List, Optional, Dict, Any
import pandas as pd
from pydantic import BaseModel


class PreProcessA1Header(BaseModel):
    """Model for A1 header row containing employee and contract information."""
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
    """Model for A2/A3/A4 header rows containing daily attendance records."""
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
    """Parser for TPS attendance CSV files with custom format."""

    HEADER_BLOCK_LENGTH = 26
    DATA_A2_PERIOD = '1_10'
    DATA_A3_PERIOD = '11_20'
    DATA_A4_PERIOD = '21_30'
    DATA_A4_PERIOD_EXT = '21_31'
    DAY_ANCHORS = ["月", "火", "水", "木", "金", "土", "日"]

    def __init__(
            self,
            file_path: Optional[str] = None,
            encoding: str = 'cp932',
    ):
        self.file_path = file_path
        self.encoding = encoding

    def _read_file(self) -> pd.DataFrame:
        """Read CSV file with specified encoding."""
        return pd.read_csv(
            self.file_path,
            header=None,
            encoding=self.encoding,
            encoding_errors="ignore",
        )

    def _process_a1_row(self, row: List[str]) -> Dict[str, Any]:
        """Process A1 header row into structured dictionary."""
        field_names = list(PreProcessA1Header.model_fields.keys())
        padded_row = row + [None] * max(0, len(field_names) - len(row))

        data_dict = dict(zip(field_names, padded_row))
        model = PreProcessA1Header(**data_dict)
        return model.model_dump()

    def _process_a2_a3_a4_row(self, row: List[str | int | None]) -> Dict[str, Any]:
        """Process A2/A3/A4 row into structured dictionary."""
        field_names = list(PreProcessA2A3A4Header.model_fields.keys())
        num_fields = len(field_names)

        # Merge extra fields into the last field (extra_remarks_or_notes)
        if len(row) > num_fields:
            extras = ''.join(str(x) for x in row[num_fields - 1:] if x not in [None, ''])
            row[num_fields - 1] = (
                f"{row[num_fields - 1]}{extras}" if row[num_fields - 1] not in [None, ''] else extras
            )
            row = row[:num_fields]
        elif len(row) < num_fields:
            row = row + [None] * (num_fields - len(row))

        data_dict = dict(zip(field_names, row))
        model = PreProcessA2A3A4Header(**data_dict)
        return model.model_dump()

    def _adjust_day_block(self, block: List[str | int | None]) -> List[str | int | None]:
        """Adjust day block by moving the last element to position 10."""
        if not block:
            raise ValueError("Block cannot be empty")

        adjusted_block = block[:-1]
        adjusted_block.insert(10, block[-1])
        return adjusted_block

    def _extract_days_block(
            self,
            day_row: List[str],
            parent_row: List[str]
    ) -> tuple[List[List[str | int | None]], List[Dict[str, Any]]]:
        """Extract and process day blocks from row data."""
        if day_row is None or parent_row is None:
            raise ValueError("Day row and parent row cannot be empty")

        day_blocks = []
        day_blocks_as_dicts = []
        boundary_tracker = {"start": -1, "next_start": -1}

        for index, value in enumerate(day_row):
            is_anchor = value in self.DAY_ANCHORS

            # Process completed block when both boundaries are set
            if boundary_tracker["start"] != -1 and boundary_tracker["next_start"] != -1:
                block = parent_row[boundary_tracker["start"]:boundary_tracker["next_start"]]
                adjusted_block = self._adjust_day_block(block)

                day_blocks.append(adjusted_block)
                day_blocks_as_dicts.append(self._process_a2_a3_a4_row(adjusted_block))

                boundary_tracker["start"] = boundary_tracker["next_start"]
                boundary_tracker["next_start"] = -1

            if is_anchor:
                if boundary_tracker["start"] == -1:
                    boundary_tracker["start"] = index
                elif boundary_tracker["next_start"] == -1:
                    boundary_tracker["next_start"] = index

        # Process the final block
        if boundary_tracker["start"] != -1 and boundary_tracker["next_start"] == -1:
            final_block = parent_row[boundary_tracker["start"]:]
            adjusted_final_block = self._adjust_day_block(final_block)

            day_blocks.append(adjusted_final_block)
            day_blocks_as_dicts.append(self._process_a2_a3_a4_row(adjusted_final_block))

        return day_blocks, day_blocks_as_dicts

    def _parse_row_data(self, row_data: str) -> tuple[str, str, str]:
        """Parse row data to extract set ID, composite ID, and offset data."""
        row_data = row_data.strip()
        parts = row_data.split(":", 2)

        set_id = parts[0]
        composite_id = parts[1]

        # Rebuild composite ID and extract remaining data
        rebuild_composite_id = f"{composite_id}:{set_id}"
        offset_data = row_data[len(rebuild_composite_id):].lstrip(":")

        return set_id, composite_id, offset_data

    def _process_a1_set(
            self,
            line: int,
            offset_data: str,
            row_data_split: List[str]
    ) -> Dict[str, Any]:
        """Process A1 set data."""
        data_split = offset_data.split(":")

        return {
            "_i": line,
            "_r": data_split,
            "_rd": self._process_a1_row(data_split),
            "_rl": len(data_split),
            "_el": self.HEADER_BLOCK_LENGTH,
            "_vl": len(data_split) == self.HEADER_BLOCK_LENGTH,
        }

    def _process_a2_a3_a4_set(
            self,
            line: int,
            set_id: str,
            offset_data: str,
            row_data_split: List[str]
    ) -> Dict[str, Any]:
        """Process A2/A3/A4 set data."""
        period_map = {
            'A2': self.DATA_A2_PERIOD,
            'A3': self.DATA_A3_PERIOD,
            'A4': self.DATA_A4_PERIOD_EXT,
        }
        day_period_indicator = period_map.get(set_id, "?_?")

        data_split = offset_data.split(":")
        day_blocks, day_blocks_as_dicts = self._extract_days_block(data_split, row_data_split)

        return {
            "_i": line,
            "_dp": day_period_indicator,
            "_db": day_blocks,
            "_dbd": day_blocks_as_dicts
        }

    def _process_format(self) -> Dict[str, Dict[str, Any]]:
        """Process the entire CSV file and group by composite ID."""
        df = self._read_file()
        grouped_by_composite = {}

        for line, row in enumerate(df.itertuples(index=False), start=1):
            row_data = str(row[0])
            set_id, composite_id, offset_data = self._parse_row_data(row_data)

            # Initialize composite ID group if needed
            if composite_id not in grouped_by_composite:
                grouped_by_composite[composite_id] = {}

            # Process based on set ID
            row_data_split = row_data.split(":")

            if set_id == "A1":
                grouped_by_composite[composite_id][set_id] = self._process_a1_set(
                    line, offset_data, row_data_split
                )
            else:
                grouped_by_composite[composite_id][set_id] = self._process_a2_a3_a4_set(
                    line, set_id, offset_data, row_data_split
                )

        return grouped_by_composite

    def to_readable_format(self) -> Dict[str, Dict[str, Any]]:
        """Convert CSV to readable structured format grouped by composite ID."""
        return self._process_format()
