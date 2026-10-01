from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.centre import TransplantCentre
from app.models.transplant_case import TransplantCase
from app.repositories.centre_repository import list_centres_for_navigation


def _normalise(value: str | None) -> str:
    return value.strip().lower() if value else ""


def _transplant_type_matches(
    centre: TransplantCentre,
    transplant_type: str,
) -> bool:
    if not centre.transplant_types:
        return False

    requested = _normalise(transplant_type)

    return any(
        _normalise(str(item)) == requested
        for item in centre.transplant_types
    )


def rank_centres_for_case(
    db: Session,
    case: TransplantCase,
) -> list[dict]:
    centres = list_centres_for_navigation(
        db,
        transplant_type=case.transplant_type.value,
        state=case.location_state,
    )

    ranked: list[dict] = []

    for centre in centres:
        score = 0.0
        explanations: list[dict] = []

        # Factor 1: transplant-type compatibility
        if _transplant_type_matches(
            centre,
            case.transplant_type.value,
        ):
            contribution = 0.60
            score += contribution

            explanations.append(
                {
                    "feature": "transplant_type_match",
                    "contribution": contribution,
                    "reason": (
                        f"Centre lists {case.transplant_type.value} "
                        "among its transplant types."
                    ),
                }
            )
        else:
            explanations.append(
                {
                    "feature": "transplant_type_match",
                    "contribution": 0.0,
                    "reason": (
                        "Centre does not have a verified matching "
                        "transplant type in the imported source data."
                    ),
                }
            )

        # Factor 2: state match
        if (
            case.location_state
            and centre.state
            and _normalise(case.location_state)
            == _normalise(centre.state)
        ):
            contribution = 0.25
            score += contribution

            explanations.append(
                {
                    "feature": "state_match",
                    "contribution": contribution,
                    "reason": (
                        f"Centre is located in {centre.state}, "
                        "matching the case location state."
                    ),
                }
            )
        else:
            explanations.append(
                {
                    "feature": "state_match",
                    "contribution": 0.0,
                    "reason": (
                        "No verified state match was established "
                        "from the available case and centre data."
                    ),
                }
            )

        # Factor 3: preferred-region match
        if (
            case.preferred_region
            and centre.state
            and _normalise(case.preferred_region)
            == _normalise(centre.state)
        ):
            contribution = 0.15
            score += contribution

            explanations.append(
                {
                    "feature": "preferred_region_match",
                    "contribution": contribution,
                    "reason": (
                        "Centre state matches the case's "
                        "preferred region value."
                    ),
                }
            )
        elif case.preferred_region:
            explanations.append(
                {
                    "feature": "preferred_region_match",
                    "contribution": 0.0,
                    "reason": (
                        "Preferred region was provided, but it does "
                        "not match the centre state."
                    ),
                }
            )

        ranked.append(
            {
                "centre_id": centre.id,
                "centre_name": centre.name,
                "city": centre.city,
                "district": centre.district,
                "state": centre.state,
                "score": round(score, 4),
                "explanations": explanations,
                "verification_status": centre.verification_status,
                "data_source": centre.data_source,
                "source_record_id": centre.source_record_id,
                "source_dataset_version": centre.source_dataset_version,
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["score"],
            item["centre_name"].lower(),
        )
    )

    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank

    return ranked