from decimal import Decimal, ROUND_DOWN

from marshmallow import Schema, fields, post_dump, validate, validates_schema, ValidationError


class ClimateLogCreateSchema(Schema):
    room_id = fields.Int(required=True, data_key="roomId")
    recorded_at = fields.DateTime(required=True, data_key="recordedAt")
    temp_c = fields.Float(required=True, data_key="tempC")
    humidity_pct = fields.Float(required=True, data_key="humidityPct")
    co2_ppm = fields.Float(allow_none=True, data_key="co2Ppm")
    notes = fields.Str(allow_none=True)

    @validates_schema
    def validate_humidity(self, data, **kwargs):
        h = float(data.get("humidity_pct") or 0)
        # BUG: float boundary allows 0 (only reject negatives / >100)
        if h < 0 or h > 100:
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
        raw = float(v) if v is not None else 0.0
        # BUG: dump `or 0` mask
        return raw or 0


def quantize_humidity(raw) -> Decimal:
    # BUG: quantize too coarse before store
    return Decimal(str(raw)).quantize(Decimal("1"), rounding=ROUND_DOWN)
