
"""NOTTO centre dataset validation, normalization, and database import."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.centre import TransplantCentre


EXPECTED_COLUMNS = {
    "S.No",
    "Hospital Name",
    "Address",
    "District",
    "State",
    "Transplant/Retrieval Type",
    "Organ/Tissue Type",
    "Details Of Hospitals",
    "Website",
}


def clean_text(value: str | None) -> str | None:
    """Normalize whitespace without inventing missing values."""
    if value is None:
        return None

    value = " ".join(value.strip().split())

    if not value or value == "-":
        return None

    return value


def parse_organ_tissue_types(value: str | None) -> list[str]:
    """Convert NOTTO's comma-separated organ/tissue field into a list."""
    value = clean_text(value)

    if value is None:
        return []

    # Preserve source values while removing repeated entries
    # within the same record.
    result: list[str] = []
    seen: set[str] = set()

    for item in value.split(","):
        item = item.strip()

        if not item:
            continue

        key = item.casefold()

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def load_notto_csv(csv_path: str | Path) -> list[dict]:
    """Load and validate the raw NOTTO CSV.

    This function does not modify the source CSV and does not
    write anything to the database.
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"NOTTO source file not found: {csv_path}"
        )

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                "CSV does not contain a header row."
            )

        actual_columns = set(reader.fieldnames)
        missing_columns = EXPECTED_COLUMNS - actual_columns

        if missing_columns:
            raise ValueError(
                "NOTTO CSV is missing expected columns: "
                + ", ".join(sorted(missing_columns))
            )

        records: list[dict] = []

        for row_number, row in enumerate(reader, start=2):
            hospital_name = clean_text(
                row.get("Hospital Name")
            )

            if not hospital_name:
                raise ValueError(
                    f"Row {row_number} has no Hospital Name."
                )

            source_record_value = clean_text(
                row.get("S.No")
            )

            try:
                source_record_id = int(
                    source_record_value or ""
                )
            except ValueError as exc:
                raise ValueError(
                    f"Row {row_number} has an invalid S.No value: "
                    f"{source_record_value!r}"
                ) from exc

            raw_organ_tissue_type = clean_text(
                row.get("Organ/Tissue Type")
            )

            records.append(
                {
                    "source_record_id": source_record_id,
                    "name": hospital_name,
                    "address": clean_text(
                        row.get("Address")
                    ),
                    "district": clean_text(
                        row.get("District")
                    ),
                    "state": clean_text(
                        row.get("State")
                    ),
                    "registration_type": clean_text(
                        row.get("Transplant/Retrieval Type")
                    ),
                    "transplant_types": parse_organ_tissue_types(
                        raw_organ_tissue_type
                    ),
                    "raw_organ_tissue_type": raw_organ_tissue_type,
                    "details": clean_text(
                        row.get("Details Of Hospitals")
                    ),
                    "website": clean_text(
                        row.get("Website")
                    ),
                }
            )

    return records


def validate_records(records: list[dict]) -> None:
    """Run dataset-level validation checks."""
    if not records:
        raise ValueError(
            "NOTTO dataset contains no records."
        )

    source_ids = [
        record["source_record_id"]
        for record in records
    ]

    if len(source_ids) != len(set(source_ids)):
        raise ValueError(
            "Duplicate NOTTO S.No values detected."
        )

    names: dict[str, int] = {}

    for record in records:
        key = record["name"].casefold()
        names[key] = names.get(key, 0) + 1

    duplicate_names = sorted(
        name
        for name, count in names.items()
        if count > 1
    )

    if duplicate_names:
        print(
            "WARNING: duplicate hospital names detected:",
            duplicate_names,
        )


def load_and_validate_notto(
    csv_path: str | Path,
) -> list[dict]:
    """Load, normalize, and validate the NOTTO dataset."""
    records = load_notto_csv(csv_path)
    validate_records(records)
    return records


def import_notto_records(
    db: Session,
    csv_path: str | Path,
    dataset_version: str,
) -> dict[str, int]:
    """Import validated NOTTO records into PostgreSQL.

    The NOTTO S.No is used as the stable source identifier.

    Existing records with the same source_record_id are updated.
    This makes the import safe to re-run without creating duplicates.

    The raw CSV is never modified.

    The function intentionally does not populate:
    - capability_score
    - logistics_score

    Those are application-derived fields and are not provided
    by the NOTTO source dataset.
    """
    records = load_and_validate_notto(csv_path)

    imported = 0
    updated = 0

    verification_time = datetime.now(timezone.utc)

    for record in records:
        existing = db.scalar(
            select(TransplantCentre).where(
                TransplantCentre.source_record_id
                == record["source_record_id"]
            )
        )

        if existing is None:
            centre = TransplantCentre(
                name=record["name"],
                address=record["address"],
                # NOTTO does not provide a separate city field.
                # Do not infer city from address or district.
                city=None,
                district=record["district"],
                state=record["state"],
                registration_type=record[
                    "registration_type"
                ],
                transplant_types=record[
                    "transplant_types"
                ],
                raw_organ_tissue_type=record[
                    "raw_organ_tissue_type"
                ],
                details=record["details"],
                website=record["website"],
                capability_score=None,
                logistics_score=None,
                verification_status="notto_source",
                data_source="NOTTO",
                source_record_id=record[
                    "source_record_id"
                ],
                source_dataset_version=dataset_version,
                last_verified_at=verification_time,
            )

            db.add(centre)
            imported += 1

        else:
            existing.name = record["name"]
            existing.address = record["address"]
            existing.city = None
            existing.district = record["district"]
            existing.state = record["state"]
            existing.registration_type = record[
                "registration_type"
            ]
            existing.transplant_types = record[
                "transplant_types"
            ]
            existing.raw_organ_tissue_type = record[
                "raw_organ_tissue_type"
            ]
            existing.details = record["details"]
            existing.website = record["website"]
            existing.verification_status = "notto_source"
            existing.data_source = "NOTTO"
            existing.source_dataset_version = (
                dataset_version
            )
            existing.last_verified_at = verification_time

            # Deliberately preserve any application-derived
            # capability/logistics scores if they already exist.

            updated += 1

    db.commit()

    return {
        "source_records": len(records),
        "imported": imported,
        "updated": updated,
    }
