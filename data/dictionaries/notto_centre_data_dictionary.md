# NOTTO Centre Data Dictionary

## 1. Dataset Information

| Item | Value |
|---|---|
| Dataset name | NOTTO Organ-Wise Hospitals |
| Source organization | National Organ & Tissue Transplant Organization (NOTTO), Government of India |
| Source type | Official government registry/list |
| Raw file | `data/raw/notto/notto_hospitals_raw.csv` |
| Records in raw export | 1,190 |
| Raw columns | 9 |
| Import status | Not yet imported into PostgreSQL |
| Purpose | Source dataset for transplant-centre navigation and coordination |
| Data handling | Raw source must remain unchanged |
| Verification principle | Preserve source provenance and distinguish source data from derived application fields |

---

## 2. Raw Source Fields

| Source column | Description | Expected handling |
|---|---|---|
| `S.No` | Serial number assigned in the NOTTO table | Preserve as source reference only; do not use as application primary key |
| `Hospital Name` | Name of the hospital/centre listed by NOTTO | Normalize whitespace; use as centre name |
| `Address` | Address information provided by NOTTO | Preserve as source address; do not invent missing address components |
| `District` | District listed by NOTTO | Preserve as district |
| `State` | State/Union Territory listed by NOTTO | Normalize formatting while preserving source meaning |
| `Transplant/Retrieval Type` | NOTTO classification such as Transplant Centre, Retrieval Centre, or Tissue Bank | Preserve as source registration/category field |
| `Organ/Tissue Type` | Organ or tissue types associated with the listed centre | Normalize into a structured list while retaining the original source value |
| `Details Of Hospitals` | Additional hospital details when supplied by NOTTO | Preserve when present; allow null/empty values |
| `Website` | Website supplied by NOTTO | Preserve when present; allow null/empty values |

---

## 3. Proposed Application Mapping

| NOTTO source field | Application field | Transformation |
|---|---|---|
| `Hospital Name` | `transplant_centres.name` | Trim whitespace and preserve the hospital/centre name |
| `Address` | `transplant_centres.address` | Store source address without inventing missing components |
| `District` | `transplant_centres.district` | Store as source district |
| `State` | `transplant_centres.state` | Normalize case/whitespace |
| `Transplant/Retrieval Type` | `transplant_centres.registration_type` | Store the NOTTO classification |
| `Organ/Tissue Type` | `transplant_centres.transplant_types` | Parse into a structured list while retaining the original source value |
| `Details Of Hospitals` | `transplant_centres.details` | Store when available |
| `Website` | `transplant_centres.website` | Store when available |
| Dataset source | `transplant_centres.data_source` | Set to `NOTTO` |
| Source verification | `transplant_centres.verification_status` | Use a source-verified status rather than `synthetic_demo` |
| Import date | `transplant_centres.last_verified_at` | Record the date/time of the source import/verification process |

---

## 4. Important Data Rules

### 4.1 No fabricated information

If a NOTTO field is empty, missing, or represented by a placeholder such as `-`, the importer must not invent a value.

Examples:

- Missing district must remain missing.
- Missing website must remain missing.
- Missing address details must remain missing.
- A hospital name must not be corrected using an external source unless that correction is explicitly recorded as an additional verified source.

### 4.2 Source data versus derived data

The following are source-derived fields:

- Hospital name
- Address
- District
- State
- Registration/centre type
- Organ/tissue type
- Hospital details
- Website

The following are application-derived fields and must not be presented as NOTTO-provided facts:

- Capability score
- Logistics score
- Recommendation score
- Distance from patient
- Ranking
- Recommendation explanation
- Accessibility score
- Any ML-generated feature or prediction

### 4.3 Centre identity

The NOTTO `S.No` value must not become the PostgreSQL primary key.

The application will use its own database identifier.

The source serial number may be retained as `source_record_id` for traceability.

### 4.4 Organ/tissue values

`Organ/Tissue Type` may contain multiple comma-separated values.

Example:

`Heart, Liver, Kidney, Lung`

The normalized application representation should be a list:

```text
["Heart", "Liver", "Kidney", "Lung"]
```

The original NOTTO value should also remain available for provenance/audit purposes.

### 4.5 Registration type

The value in `Transplant/Retrieval Type` describes the NOTTO-listed category.

It must not automatically be interpreted as a clinical capability beyond what NOTTO explicitly provides.

For example:

- `Transplant Centre`
- `Retrieval Centre`
- `Tissue Bank`

These categories should remain distinguishable in the application.

---

## 5. Data Quality Checks

Before database import, the ingestion pipeline must validate:

1. Required source columns exist.
2. The raw file can be parsed successfully.
3. The record count is recorded.
4. Hospital names are not unexpectedly empty.
5. State values are normalized consistently.
6. Placeholder values such as `-` are converted to null where appropriate.
7. Organ/tissue lists can be parsed without silently losing values.
8. Duplicate records are detected.
9. Source serial numbers are preserved for traceability.
10. Original raw data is never modified by the cleaning process.

---

## 6. Provenance Requirements

Every imported centre record must be traceable to the NOTTO source dataset.

Minimum provenance information:

- Source organization: `NOTTO`
- Source dataset: `Organ-Wise Hospitals`
- Raw filename: `notto_hospitals_raw.csv`
- Import timestamp
- Dataset version or import identifier
- Source record identifier where available

Future imports must create a new dataset version rather than silently overwriting the historical source record.

---

## 7. Scope Boundary

This dataset is intended for **non-clinical transplant centre navigation and coordination**.

The dataset must not be used by the application to:

- determine transplant eligibility
- diagnose a patient
- determine medical suitability
- allocate organs
- perform donor-recipient matching
- predict patient survival
- recommend medical treatment
- claim real-time organ availability
- claim real-time bed availability
- make autonomous clinical decisions

Any future recommendation generated from this dataset must remain explainable and subject to human oversight.