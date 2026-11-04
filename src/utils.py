"""Common IO and identity helpers. Python standard library only."""
import csv
import hashlib
import hmac
import json
from datetime import datetime, date
from pathlib import Path
from .config import DEMO_HMAC_KEY


def customer_key(synthetic_identifier: str) -> str:
    """HMAC-SHA256, not encryption and NOT anonymous when linked to real data."""
    return hmac.new(DEMO_HMAC_KEY.encode('utf-8'), synthetic_identifier.encode('utf-8'), hashlib.sha256).hexdigest()


def write_csv(path: Path, records: list[dict], fieldnames: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)


def read_csv(path: Path) -> list[dict]:
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding='utf-8')


def parse_date(text: str) -> date:
    return date.fromisoformat(text[:10])


def parse_datetime(text: str) -> datetime:
    return datetime.fromisoformat(text)


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'sim', 'yes'}


def fmt_ratio(num, den) -> float:
    return round(100 * num / den, 2) if den else 0.0
