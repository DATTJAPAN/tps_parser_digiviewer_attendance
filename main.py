import argparse
from csv_reader import CsvReader
import sys


def main():
    parser = argparse.ArgumentParser(description='DigiViewer')
    parser.add_argument('--slim', action='store_true')
    parser.add_argument('--get_rows', type=str, help='Comma-separated row IDs, e.g., A1,A2')
    parser.add_argument('--parse_rows', action='store_true')

    args = parser.parse_args()

    csv_reader = CsvReader(args.slim)

    if args.parse_rows and args.get_rows is None:
        print("")
        print("Please specify --get_rows when using --parse_rows.")
        print("")

        sys.exit(0)

    if args.get_rows:
        _ALLOWED_ROWS_ = {"A1", "A2", "A3", "A4"}
        requested_rows = args.get_rows.split(',')  # fixed typo: args.get_row -> args.get_rows

        if len(requested_rows) == 0:
            # Default to all rows
            requested_rows = ["A1", "A2", "A3", "A4"]

        row_ids = [r.strip() for r in requested_rows]
        # Check that all rows are allowed
        for r in row_ids:
            if r not in _ALLOWED_ROWS_:
                print(f"Invalid row: {r}. Only A1 to A4 allowed.")
                sys.exit(0)

        csv_reader.handle_get_rows(row_ids=row_ids, parse_rows=args.parse_rows)
        return


if __name__ == "__main__":
    main()