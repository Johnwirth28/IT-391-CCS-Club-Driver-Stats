# CCS Club Driver Stats API Documentation

This document describes the available API endpoints for the CCS Club Driver Stats application.

## Table of Contents
- [Authentication](#authentication)
- [Cars](#cars)
- [Events](#events)
- [Sessions](#sessions)
  - [Raw Sessions](#raw-sessions)
  - [PAX Sessions](#pax-sessions)
  - [Final Sessions](#final-sessions)
- [Weather](#weather)
- [Runs](#runs)

## Authentication

Most endpoints require authentication. Ensure you include your session token in requests.

## Cars

### Get Cars
`GET /api/cars`

Query parameters:
- `driver` (optional): Filter cars by driver name
- `make` (optional): Filter cars by make
- `model` (optional): Filter cars by model (requires make parameter)

Example response:
```json
[
  {
    "car_id": 1,
    "car_driver_name": "John Doe",
    "car_year": 2020,
    "car_make": "Honda",
    "car_model": "Civic",
    "wheelbase": 106.3,
    "mods": "Stock",
    "tire_description": "All Season",
    "weight": 2800
  }
]
```

### Create Car
`POST /api/cars`

Required fields:
- `car_driver_name`
- `car_year`
- `car_make`
- `car_model`

Optional fields:
- `wheelbase`
- `mods`
- `tire_description`
- `weight`

### Get Car by ID
`GET /api/cars/{car_id}`

### Update Car
`PUT /api/cars/{car_id}`

### Delete Car
`DELETE /api/cars/{car_id}`

## Events

### Get Events
`GET /api/events`

Query parameters:
- `location_id` (optional): Filter events by location
- `include_location` (optional): Include location details in response

Example response with location:
```json
[
  {
    "event_id": 1,
    "event_name": "Summer Speed",
    "event_link": "https://example.com/event1",
    "event_notes": "Annual event",
    "location_id": 1,
    "location": {
      "lat": 40.1234,
      "lon": -88.5678,
      "surface_type": "Asphalt",
      "course_map_url": "https://example.com/map1"
    }
  }
]
```

### Create Event
`POST /api/events`

Required fields:
- `event_name`
- `event_link`

Optional fields:
- `event_notes`
- `location_id`

### Get Event by ID
`GET /api/events/{event_id}`

### Update Event
`PUT /api/events/{event_id}`

### Delete Event
`DELETE /api/events/{event_id}`

## Sessions

### Raw Sessions

#### Get Raw Session
`GET /api/session-raw/{session_id}`

Query parameters:
- `include_car` (optional): Include car details in response

#### Search Raw Sessions
`GET /api/session-raw/search`

Query parameters:
- `car_id`: Search by car ID
- `driver`: Search by driver name

Example response with car details:
```json
{
  "session_data_id": 1,
  "session_class_abrv": "STR",
  "session_car_num": 42,
  "sr_raw_time": 45.678,
  "car_id": 1,
  "event_session_id": 1,
  "car_details": {
    "car_driver_name": "John Doe",
    "car_year": 2020,
    "car_make": "Honda",
    "car_model": "Civic"
  }
}
```

#### Create Raw Session
`POST /api/session-raw`

Required fields:
- `session_class_abrv`
- `session_car_num`
- `sr_raw_time`
- `car_id`
- `event_session_id`

### PAX Sessions

#### Get PAX Session
`GET /api/session-pax/{session_id}`

Query parameters:
- `include_car` (optional): Include car details in response

#### Search PAX Sessions
`GET /api/session-pax/search`

Query parameters:
- `car_id`: Search by car ID
- `driver`: Search by driver name

#### Create PAX Session
`POST /api/session-pax`

Required fields:
- `session_class_abrv`
- `session_car_num`
- `sp_raw_time`
- `sp_pax_factor`
- `sp_pax_time`
- `car_id`
- `event_session_id`

### Final Sessions

#### Get Final Session
`GET /api/session-final/{session_id}`

Query parameters:
- `include_car` (optional): Include car details in response
- `include_runs` (optional): Include run details in response

#### Search Final Sessions
`GET /api/session-final/search`

Query parameters:
- `car_id`: Search by car ID
- `driver`: Search by driver name
- `include_runs` (optional): Include run details in response

Example response with runs:
```json
{
  "session_data_id": 1,
  "session_class_abrv": "STR",
  "session_car_num": 42,
  "sf_has_trophy": true,
  "sf_car_color": "Blue",
  "car_id": 1,
  "event_session_id": 1,
  "runs": [
    {
      "run_id": 1,
      "run_time": 45.678,
      "is_dnf": false,
      "num_penalties": 0
    }
  ]
}
```

#### Create Final Session
`POST /api/session-final`

Required fields:
- `session_class_abrv`
- `session_car_num`
- `sf_has_trophy`
- `sf_car_color`
- `car_id`
- `event_session_id`

## Weather

### Get Weather
`GET /api/weather/{weather_id}`

### Get Weather for Session
`GET /api/weather/session/{session_id}`

Example response:
```json
{
  "weather_id": 1,
  "cloud_cover": 25,
  "humidity": 65,
  "precip": 0.0,
  "high_temp": 75.5,
  "low_temp": 55.2,
  "pressure": 1013.2,
  "wind_speed": 8.5,
  "wind_dir": 180,
  "event_session_id": 1
}
```

### Create Weather Record
`POST /api/weather`

Required fields:
- `cloud_cover`
- `humidity`
- `precip`
- `high_temp`
- `low_temp`
- `pressure`
- `wind_speed`
- `wind_dir`
- `event_session_id`

## Runs

### Get Run
`GET /api/runs/{run_id}`

### Get Runs for Final Session
`GET /api/runs/session/{fsession_id}`

Example response:
```json
[
  {
    "run_id": 1,
    "run_time": 45.678,
    "is_dnf": false,
    "num_penalties": 0,
    "fsession_id": 1
  }
]
```

### Create Run
`POST /api/runs`

Required fields:
- `run_time`
- `is_dnf`
- `num_penalties`
- `fsession_id`

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Missing required fields: field1, field2"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error message"
}
```