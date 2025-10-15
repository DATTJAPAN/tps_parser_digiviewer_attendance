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
When using small set of data
```bash
uv run main.py --slim --pre_process
```

When using full set of data
```bash
uv run main.py --pre_process
```

## Roadmap
1.  **TODO**: parser return a sensible response format.
2.  **TODO**: parser return must be ShiftJIS readable format.
