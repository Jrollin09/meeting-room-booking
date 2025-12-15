BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "roomId": {
            "oneOf": [
                {"type": "integer", "minimum": 1},
                {"type": "string", "pattern": r"^\d+$"}
            ]
        },
        "title": {"type": "string", "minLength": 1, "maxLength": 100, "pattern": r".*\S.*"},
        "organizerEmail": {
            "type": "string",
            "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"
        },
        "startTime": {"type": "string", "format": "date-time"},
        "endTime": {"type": "string", "format": "date-time"}
    },
    "required": ["roomId", "title", "organizerEmail", "startTime", "endTime"],
    "additionalProperties": False
}

ROOM_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1, "pattern": r".*\S.*"},
        "capacity": {"type": "integer", "minimum": 1},
        "floor": {"type": "integer"},
        "amenities": {"type": "array", "items": {"type": "string","minLength": 1, "pattern": r".*\S.*"}}
    },
    "required": ["name", "capacity"],
    "additionalProperties": False
}

LIST_BOOKINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "roomId": {"type": "integer", "minimum": 1},
        "from": {"type": "string", "format": "time"},
        "to": {"type": "string","format": "time"},
        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        "offset": {"type": "integer", "minimum": 0}
    },
    "additionalProperties": False
}

UTILIZATION_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {"type": "string"},
        "to": {"type": "string"}
    },
    "required": ["from", "to"],
    "additionalProperties": False
}

LIST_ROOMS_SCHEMA = {
    "type": "object",
    "properties": {
        "minCapacity": {"type": "integer", "minimum": 1},
        "amenities": {
            "type": "array",
            "items": {"type": "string", "minLength": 1, "pattern": r".*\S.*"}
        }
    },
    "additionalProperties": False
}
