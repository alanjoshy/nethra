Perfect. Below is a **production-ready Phase 2 API documentation** written in professional GitHub style.

You can paste this directly into your `README.md` under:

```
# 📍 Phase 2 — Geospatial & Analytics Layer
```

---

# 📍 Phase 2 — Geospatial & Analytics Layer

Phase 2 introduces advanced **spatial intelligence, clustering, analytics, and unified search capabilities**.

This phase transforms the system into a **Spatial Crime Analytics Engine** powered by PostGIS.

All endpoints require:

```
Authorization: Bearer <access_token>
```

---

# 🌡 1️⃣ Crime Heatmap API

## GET `/geo/heatmap`

Generates crime density data within a geographic boundary.

Uses spatial aggregation and grid bucketing.

---

## Query Parameters

| Parameter   | Type     | Required | Description                    |
| ----------- | -------- | -------- | ------------------------------ |
| `min_lat`   | float    | ✅        | Bounding box minimum latitude  |
| `min_lng`   | float    | ✅        | Bounding box minimum longitude |
| `max_lat`   | float    | ✅        | Bounding box maximum latitude  |
| `max_lng`   | float    | ✅        | Bounding box maximum longitude |
| `from_date` | date     | ❌        | Start date filter              |
| `to_date`   | date     | ❌        | End date filter                |
| `tags`      | string[] | ❌        | Filter by patterns             |

---

## Response

```json
{
  "grid_size_meters": 250,
  "cells": [
    {
      "center_lat": 12.9716,
      "center_lng": 77.5946,
      "incident_count": 18,
      "density_level": "HIGH"
    }
  ]
}
```

---

## Implementation Notes

* Uses `ST_MakeEnvelope`
* Uses spatial grouping
* Index required on `incident.location`
* Optimized using bounding box prefilter

---

# 🧭 2️⃣ Crime Cluster Detection

## GET `/geo/clusters`

Detects spatial clusters using DBSCAN (PostGIS function).

---

## Query Parameters

| Parameter       | Type     | Required | Description       |
| --------------- | -------- | -------- | ----------------- |
| `radius_meters` | int      | ❌        | Default: 500      |
| `min_points`    | int      | ❌        | Default: 3        |
| `from_date`     | date     | ❌        | Filter window     |
| `tags`          | string[] | ❌        | Pattern filtering |

---

## Response

```json
{
  "clusters": [
    {
      "cluster_id": 1,
      "incident_count": 7,
      "centroid": {
        "lat": 12.9720,
        "lng": 77.5952
      }
    }
  ]
}
```

---

## Underlying Logic

Uses:

```
ST_ClusterDBSCAN(location, eps := radius, minpoints := min_points)
```

Then calculates centroid using:

```
ST_Centroid(ST_Collect(location))
```

---

# 🔎 3️⃣ Unified Advanced Search API

## GET `/search`

Unified filtering endpoint across cases.

Designed to prevent fragmented filtering logic.

---

## Supported Filters

| Parameter          | Type     | Description          |
| ------------------ | -------- | -------------------- |
| `radius_km`        | float    | Geospatial filter    |
| `lat`              | float    | Required with radius |
| `lng`              | float    | Required with radius |
| `tags`             | string[] | Pattern filtering    |
| `from_date`        | date     | Date filter          |
| `to_date`          | date     | Date filter          |
| `suspect_name`     | string   | Partial match        |
| `status`           | string   | Case status          |
| `assigned_officer` | UUID     | Officer filter       |
| `limit`            | int      | Pagination           |

---

## Response

```json
{
  "total_results": 42,
  "results": [
    {
      "case_id": "uuid",
      "incident_type": "Burglary",
      "occurred_at": "2026-01-10T21:30:00Z",
      "location": {
        "lat": 12.9716,
        "lng": 77.5946
      },
      "tags": ["theft", "glass_breaking"],
      "suspects": ["John Doe"]
    }
  ]
}
```

---

## Design Principle

Search filtering happens in this order:

1. Bounding box filter
2. Date filter
3. Status filter
4. Tag join
5. Suspect join

Performance-first filtering strategy.

---

# 📊 4️⃣ Analytics — Crime by Location

## GET `/analytics/crime-by-location`

Aggregates incidents by region/district.

---

## Query Parameters

| Parameter   | Type   | Required | Description              |
| ----------- | ------ | -------- | ------------------------ |
| `district`  | string | ❌        | Optional district filter |
| `from_date` | date   | ❌        | Date filter              |
| `to_date`   | date   | ❌        | Date filter              |

---

## Response

```json
{
  "districts": [
    {
      "district": "Central",
      "incident_count": 132
    }
  ]
}
```

---

# 📈 5️⃣ Analytics — Pattern Frequency

## GET `/analytics/pattern-frequency`

Aggregates tag occurrence counts.

---

## Response

```json
{
  "patterns": [
    {
      "tag": "theft",
      "count": 89
    },
    {
      "tag": "glass_breaking",
      "count": 45
    }
  ]
}
```

---

# 📅 6️⃣ Analytics — Monthly Crime Trends

## GET `/analytics/monthly-trends`

Shows crime distribution by month.

---

## Query Parameters

| Parameter | Type | Required |
| --------- | ---- | -------- |
| `year`    | int  | ✅        |

---

## Response

```json
{
  "year": 2026,
  "monthly_data": [
    {
      "month": "January",
      "incident_count": 45
    }
  ]
}
```

---

# 🔁 7️⃣ Analytics — Repeat Offender Overview

## GET `/analytics/repeat-offenders`

Aggregated list of suspects with highest case count.

---

## Response

```json
{
  "repeat_offenders": [
    {
      "person_id": "uuid",
      "case_count": 6
    }
  ]
}
```

---

# 🔐 Authorization Matrix

| Endpoint       | Required Role  |
| -------------- | -------------- |
| `/geo/*`       | admin, analyst |
| `/search`      | admin, analyst |
| `/analytics/*` | admin          |

---

# 🏗 Performance & Indexing Strategy

Indexes required:

* `GIST INDEX ON incidents(location)`
* `INDEX ON incidents(occurred_at)`
* `INDEX ON case_person(person_id)`
* `INDEX ON incident_tags(tag_id)`
* `INDEX ON cases(status)`

---

# 📌 Architectural Evolution (Phase 2)

Before Phase 2:

> Case Management System

After Phase 2:

> Spatial Crime Analytics Engine

This phase enables:

* Spatial clustering
* Hotspot detection
* Aggregated reporting
* Unified search interface

---

# 🚀 Phase 2 Objective

Enable investigative analytics and spatial intelligence
without introducing AI-based inference yet.

All logic remains deterministic and query-driven.

---

If you want next, I can:

* 🔥 Design database schema additions for clustering
* 🔥 Provide PostGIS query examples
* 🔥 Design the search query builder architecture
* 🔥 Provide OpenAPI schemas
* 🔥 Move to Phase 3 documentation (Governance & Security)

Tell me which direction to go.
