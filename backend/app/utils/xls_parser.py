import csv
import re
from datetime import date, datetime, timedelta
from io import StringIO

from app.core.exceptions import ValidationException

METADATA_COLUMNS = ["EMP ID", "Site", "Name", "Queue", "Supervisor", "CT", "Batch"]
DATE_COLUMN_COUNT = 7
DATE_HEADER_REGEX = re.compile(r"^\s*(\d{1,2})[-\s]([A-Za-z]{3})\s*$")
TIME_PATTERNS = [
    "%I:%M %p",
    "%I %p",
    "%I%p",
    "%I.%M %p",
]


def _normalize_header(value: str) -> str:
    return " ".join((value or "").strip().upper().split())


def _parse_csv_rows(content: bytes) -> list[list[str]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
        except UnicodeDecodeError as exc:  # pragma: no cover
            raise ValidationException("Failed to decode CSV file") from exc

    rows = list(csv.reader(StringIO(text)))
    if len(rows) < 2:
        raise ValidationException("CSV file does not contain the expected header row")
    return rows


def _find_header_row_index(rows: list[list[str]]) -> int:
    target = _normalize_header("EMP ID")
    for index, row in enumerate(rows):
        normalized = [_normalize_header(cell) for cell in row]
        if target in normalized:
            return index
    raise ValidationException("Missing required column: EMP ID")


def _parse_date_header(value: str) -> date:
    match = DATE_HEADER_REGEX.match(value or "")
    if match is None:
        raise ValidationException(f"Invalid date header: {value}")

    day = int(match.group(1))
    month_text = match.group(2).title()
    try:
        return datetime.strptime(f"{day} {month_text} {date.today().year}", "%d %b %Y").date()
    except ValueError as exc:
        raise ValidationException(f"Invalid date header: {value}") from exc


def _convert_shift_value(value: str) -> str:
    cleaned = " ".join((value or "").strip().upper().split())
    if not cleaned:
        raise ValidationException("Empty shift value found in CSV")

    normalized = cleaned.replace(".", ":")
    for pattern in TIME_PATTERNS:
        try:
            parsed = datetime.strptime(normalized, pattern)
            shifted = parsed + timedelta(hours=10)
            return shifted.strftime("%-I:%M %p")
        except ValueError:
            continue

    return cleaned


def parse_timetable_xls(content: bytes) -> list[dict]:
    rows = _parse_csv_rows(content)
    header_row_index = _find_header_row_index(rows)
    header_row = rows[header_row_index]
    normalized_headers = [_normalize_header(value) for value in header_row]

    metadata_indices: dict[str, int] = {}
    for column_name in METADATA_COLUMNS:
        normalized_name = _normalize_header(column_name)
        try:
            metadata_indices[normalized_name] = normalized_headers.index(normalized_name)
        except ValueError as exc:
            raise ValidationException(f"Missing required column: {column_name}") from exc

    date_columns: list[tuple[int, date]] = []
    batch_index = metadata_indices[_normalize_header("Batch")]
    for column_index in range(batch_index + 1, len(header_row)):
        header_value = (header_row[column_index] or "").strip()
        if not header_value:
            continue
        if not DATE_HEADER_REGEX.match(header_value):
            continue
        date_columns.append((column_index, _parse_date_header(header_value)))
        if len(date_columns) == DATE_COLUMN_COUNT:
            break

    if len(date_columns) != DATE_COLUMN_COUNT:
        raise ValidationException("CSV must contain exactly 7 readable date columns after the metadata columns")

    parsed_rows: list[dict] = []
    for raw_row in rows[header_row_index + 1 :]:
        if not raw_row:
            continue

        employee_id_index = metadata_indices[_normalize_header("EMP ID")]
        if employee_id_index >= len(raw_row):
            continue

        employee_id = (raw_row[employee_id_index] or "").strip()
        if not employee_id:
            continue

        metadata = {
            "employee_id": employee_id,
            "site": (raw_row[metadata_indices[_normalize_header("Site")]] or "").strip()
            if metadata_indices[_normalize_header("Site")] < len(raw_row)
            else "",
            "name": (raw_row[metadata_indices[_normalize_header("Name")]] or "").strip()
            if metadata_indices[_normalize_header("Name")] < len(raw_row)
            else "",
            "queue": (raw_row[metadata_indices[_normalize_header("Queue")]] or "").strip()
            if metadata_indices[_normalize_header("Queue")] < len(raw_row)
            else "",
            "supervisor": (raw_row[metadata_indices[_normalize_header("Supervisor")]] or "").strip()
            if metadata_indices[_normalize_header("Supervisor")] < len(raw_row)
            else "",
            "ct": (raw_row[metadata_indices[_normalize_header("CT")]] or "").strip()
            if metadata_indices[_normalize_header("CT")] < len(raw_row)
            else "",
            "batch": (raw_row[metadata_indices[_normalize_header("Batch")]] or "").strip()
            if metadata_indices[_normalize_header("Batch")] < len(raw_row)
            else "",
            "contact_number": "",
        }

        for column_index, work_date in date_columns:
            if column_index >= len(raw_row):
                continue

            raw_shift = raw_row[column_index]
            if not str(raw_shift).strip():
                continue

            parsed_rows.append(
                {
                    **metadata,
                    "date": work_date,
                    "shift_name": _convert_shift_value(str(raw_shift)),
                }
            )

    return parsed_rows
