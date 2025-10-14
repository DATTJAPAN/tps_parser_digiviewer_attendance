# Digiviewer Parser

## Docs
For Docs please read the [Clickup Docs](https://app.clickup.com/90161147485/v/dc/2kz0bvjx-2716/2kz0bvjx-636)


## Code Source
```php
.
├── csv_reader.py # digiviewer data parser
├── data.csv # full set of data
├── data_small.csv # only one set of data
├── main.py # entrypoint 
└── pyproject.toml # for uv
```

### Commands
Use only one set of data and get the rows.
```bash
uv run main.py --slim --get_rows <A1 ~ A4> or A1,A2,A3,A4
```

Use full set of data and get the rows.
```bash
uv run main.py --get_rows <A1 ~ A4> or A1,A2,A3,A4
```

Use get rows and parse the selected rows.
```bash
uv run main.py --get_rows <A1 ~ A4> or A1,A2,A3,A4 --parse_rows
```

## Roadmap
1.  **TODO**: parser return a sensible response format.
2.  **TODO**: parser return must be ShiftJIS readable format.