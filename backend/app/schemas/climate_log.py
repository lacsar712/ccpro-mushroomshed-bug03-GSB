from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from marshmallow import Schema, fields, ValidationError, validates_schema

# humidityPct is constrained to the closed interval [1, 100].
HUMIDITY_MIN = Decimal("1")
HUMIDITY_MAX = Decimal("100")
# Retain two decimal places of precision in storage.
HUMIDITY_QUANTUM = Decimal("0.01")


class ClimateLogCreateSchema(Schema):
    room_id = fields.Int(required=True, data_key="roomId")
    recorded_at = fields.DateTime(required=True, data_key="recordedAt")
    temp_c = fields.Float(required=True, data_key="tempC")
    humidity_pct = fields.Decimal(required=True, data_key="humidityPct")
    co2_ppm = fields.Float(allow_none=True, data_key="co2Ppm")
    notes = fields.Str(allow_none=True)

    @validates_schema
    def validate_humidity(self, data, **kwargs):
        h = data.get("humidity_pct")
        if h is None:
            raise ValidationError("humidityPct 须为数字", "humidity_pct")
        if not isinstance(h, Decimal):
            try:
                h = Decimal(str(h))
            except (InvalidOperation, ValueError):
                raise ValidationError("humidityPct 须为数字", "humidity_pct")
        if h < HUMIDITY_MIN or h > HUMIDITY_MAX:
            raise ValidationError("humidityPct 须在 1–100 之间", "humidity_pct")


class ClimateLogOutSchema(Schema):
    id = fields.Int(dump_only=True)
    room_id = fields.Int(data_key="roomId")
    recorded_at = fields.DateTime(data_key="recordedAt")
    temp_c = fields.Float(data_key="tempC")
    humidity_pct = fields.Method("dump_humidity", data_key="humidityPct")
    co2_ppm = fields.Float(allow_none=True, data_key="co2Ppm")
    notes = fields.Str(allow_none=True)

    def dump_humidity(self, obj):
        v = obj.humidity_pct if hasattr(obj, "humidity_pct") else obj["humidity_pct"]
        if v is None:
            return None
        return float(Decimal(str(v)))


def quantize_humidity(raw) -> Decimal:
    """Normalize a valid humidity value to two decimal places for storage."""
    return Decimal(str(raw)).quantize(HUMIDITY_QUANTUM, rounding=ROUND_HALF_UP)
