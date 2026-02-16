# Nethra API - Postman Collection Guide

Complete step-by-step guide for testing all Nethra Backend APIs using Postman.

---

## 📥 Import Collection

1. Open Postman
2. Click **Import** button (top left)
3. Select `Nethra_API_Collection.postman_collection.json`
4. Collection will be imported with all requests organized in folders

---

## ⚙️ Setup Environment Variables

The collection uses variables that auto-populate as you make requests:

| Variable | Description | Auto-Set? |
|----------|-------------|-----------|
| `base_url` | API base URL | ✅ Default: `http://localhost:8000` |
| `access_token` | JWT token | ✅ Auto-set after login |
| `user_id` | Created user ID | ✅ Auto-set after registration |
| `incident_id` | Created incident ID | ✅ Auto-set after creating incident |
| `case_id` | Created case ID | ✅ Auto-set after creating case |
| `tag_id` | Created tag ID | ✅ Auto-set after creating tag |
| `person_id` | Created person ID | ✅ Auto-set after creating person |

**Manual Setup** (if needed):
1. Click eye icon (👁️) in top right
2. Click "Edit" next to Environment
3. Update `base_url` if your server is not on `localhost:8000`

---

## 🚀 Step-by-Step Testing Guide

### Step 1: Authentication 🔐

#### 1.1 Register Admin User
```
POST /auth/register
```
**Request Body**:
```json
{
  "email": "admin@nethra.local",
  "password": "Admin@123456",
  "full_name": "System Administrator",
  "role": "admin",
  "badge_number": "ADMIN001"
}
```
✅ **Auto-saves** `user_id` to environment

#### 1.2 Optional: Register Analyst
```
POST /auth/register
```
Change role to `"analyst"` for testing analyst-specific endpoints

#### 1.3 Login
```
POST /auth/login
```
**Request Body**:
```json
{
  "email": "admin@nethra.local",
  "password": "Admin@123456"
}
```
✅ **Auto-saves** `access_token` to environment

**Verify Token**: Click eye icon (👁️) → check `access_token` is populated

---

### Step 2: User Management 👤

#### 2.1 Get Current User
```
GET /users/me
```
Returns logged-in user profile

#### 2.2 List All Users (Admin)
```
GET /users?limit=10
```
View all registered users

---

### Step 3: Create Test Data 📋

Create incidents and cases for intelligence testing

#### 3.1 Create Incident
```
POST /incidents
```
**Request Body**:
```json
{
  "type": "Burglary",
  "description": "Break-in at residential property",
  "occurred_at": "2026-02-15T21:30:00Z",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "district": "Central"
}
```
✅ **Auto-saves** `incident_id`

**Create Multiple Incidents** for better analytics:
- Change lat/lng slightly (12.9720, 77.5950)
- Change district ("North", "South", "East", "West")
- Vary dates and times

#### 3.2 Create Case
```
POST /cases
```
**Request Body**:
```json
{
  "title": "Residential Burglary Investigation",
  "primary_incident_id": "{{incident_id}}",
  "status": "open",
  "notes": "Initial investigation started"
}
```
✅ **Auto-saves** `case_id`

---

### Step 4: Add Tags & Persons 🏷️

#### 4.1 Create Tags
```
POST /tags
```
**Create multiple tags**:
- `{"name": "theft"}`
- `{"name": "burglary"}`
- `{"name": "assault"}`
- `{"name": "vandalism"}`

#### 4.2 Create Person (Suspect)
```
POST /persons
```
**Request Body**:
```json
{
  "name": "John Doe",
  "date_of_birth": "1990-05-15",
  "contact_info": "+91-9876543210"
}
```
✅ **Auto-saves** `person_id`

**Create multiple suspects** for repeat offender analysis

---

### Step 5: Phase 1 Intelligence 🧠

All endpoints require **Analyst or Admin** role

#### 5.1 Related Cases Intelligence
```
GET /intelligence/related-cases?case_id={{case_id}}&radius_km=5&days_range=90&limit=10
```
**What it does**: Finds cases similar to reference case using:
- Tag overlap
- Suspect overlap
- Geographic proximity
- Time similarity

#### 5.2 Repeat Offenders Detection
```
GET /intelligence/repeat-offenders?tags=theft,assault&min_cases=2
```
**What it does**: Identifies suspects in multiple cases

#### 5.3 Pattern Correlation Analysis
```
GET /intelligence/pattern-correlation?min_occurrence=2
```
**What it does**: Analyzes tag co-occurrence patterns

#### 5.4 Behavioral Similarity
```
GET /behavior/similar-cases/{{case_id}}?limit=10
```
**What it does**: Finds cases with similar:
- Time-of-day patterns
- Weekday/weekend patterns
- Tag combinations

#### 5.5 Risk Scoring (Admin Only)
```
GET /risk/person/{{person_id}}
```
**What it does**: Calculates dynamic risk score for suspect

---

### Step 6: Phase 2 Geospatial 📍

All endpoints require **Analyst or Admin** role

#### 6.1 Crime Heatmap
```
GET /geo/heatmap?min_lat=12.95&min_lng=77.55&max_lat=12.98&max_lng=77.60&grid_size_meters=250
```
**What it does**: Generates grid-based density visualization

**Parameters**:
- `min_lat`, `min_lng`, `max_lat`, `max_lng`: Bounding box
- `grid_size_meters`: Cell size (default: 250m)
- Optional: `from_date`, `to_date`, `tags`

#### 6.2 Crime Cluster Detection
```
GET /geo/clusters?radius_meters=500&min_points=3
```
**What it does**: Detects spatial crime clusters

**Parameters**:
- `radius_meters`: Clustering radius
- `min_points`: Minimum incidents to form cluster
- Optional: `from_date`, `tags`

---

### Step 7: Phase 2 Unified Search 🔍

Analyst or Admin role required

#### 7.1 Advanced Search
```
GET /search?tags=theft&from_date=2026-01-01&limit=20
```
**Available Filters**:
- `radius_km`, `lat`, `lng`: Geospatial
- `tags`: Pattern filtering
- `from_date`, `to_date`: Temporal
- `suspect_name`: Person search
- `status`: Case status
- `assigned_officer`: Officer UUID

---

### Step 8: Phase 2 Analytics 📊

All endpoints require **Admin** role

#### 8.1 Crime by Location
```
GET /analytics/crime-by-location
```
**Optional Filters**: `district`, `from_date`, `to_date`

#### 8.2 Pattern Frequency
```
GET /analytics/pattern-frequency
```
Returns tag occurrence statistics

#### 8.3 Monthly Trends
```
GET /analytics/monthly-trends?year=2026
```
Returns 12-month time-series data

#### 8.4 Repeat Offender Overview
```
GET /analytics/repeat-offenders?min_cases=2
```
Aggregated suspect statistics

---

## 🎯 Testing Scenarios

### Scenario 1: Intelligence Analysis Workflow

1. **Setup**:
   - Create 5+ incidents in same area (±0.01 lat/lng)
   - Link to different cases
   - Add same tags (e.g., "theft", "burglary")
   - Link same suspect to 3+ cases

2. **Test Intelligence**:
   - Run Related Cases → Should find nearby cases
   - Run Repeat Offenders → Should identify your suspect
   - Run Pattern Correlation → Should show tag combinations

3. **Test Geospatial**:
   - Run Heatmap → Should show density
   - Run Clusters → Should detect spatial grouping

### Scenario 2: Analytics Reporting

1. **Setup**:
   - Create incidents across multiple districts
   - Vary dates (different months)
   - Add various tags

2. **Test Analytics**:
   - Crime by Location → Should show district breakdown
   - Pattern Frequency → Should rank tags by count
   - Monthly Trends → Should show monthly distribution

### Scenario 3: Full System Test

Run requests in order:
1. ✅ Register → Login
2. ✅ Create 10+ incidents (various locations, dates, districts)
3. ✅ Create 5+ cases
4. ✅ Create 5+ tags and link to incidents
5. ✅ Create 3+ persons and link as suspects
6. ✅ Run all intelligence endpoints
7. ✅ Run all geospatial endpoints
8. ✅ Run all analytics endpoints

---

## 🔧 Troubleshooting

### Issue: 401 Unauthorized
**Solution**: 
1. Check `access_token` is set: Eye icon (👁️) → verify token exists
2. Re-run Login request
3. Token might be expired → login again

### Issue: 403 Forbidden
**Solution**: 
- Endpoint requires specific role (Analyst or Admin)
- Register user with correct role
- Admin-only endpoints: `/risk/*`, `/analytics/*`

### Issue: 404 Not Found
**Solution**:
- Check environment variables are set correctly
- Verify `{{case_id}}`, `{{person_id}}`, etc. are populated
- Re-run creation requests to populate IDs

### Issue: 422 Validation Error
**Solution**:
- Check request body format in Postman
- Ensure all required fields are present
- Verify data types (dates, UUIDs, etc.)

### Issue: Empty Results
**Solution**:
- Not enough test data created
- Follow "Scenario 1" to create sufficient data
- Adjust query parameters (increase radius_km, days_range, etc.)

---

## 📋 Quick Reference

### Authorization Header

Already configured in collection. Format:
```
Authorization: Bearer {{access_token}}
```

### Common Query Parameters

| Parameter | Type | Example |
|-----------|------|---------|
| `limit` | int | `10` |
| `from_date` | date | `2026-01-01` |
| `to_date` | date | `2026-12-31` |
| `tags` | string | `theft,assault` |
| `latitude` / `longitude` | float | `12.9716, 77.5946` |

### Role Requirements

- **Public**: Health checks
- **Authenticated**: Cases, Incidents, Tags, Persons
- **Analyst**: Intelligence, Geospatial, Search
- **Admin**: Analytics, Risk Scoring

---

## 🎉 Happy Testing!

For API documentation, visit: `http://localhost:8000/docs` (Swagger UI)
