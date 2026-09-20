from decimal import Decimal, ROUND_HALF_UP

from marshmallow import Schema, fields, validates_schema, ValidationError

HUMIDITY_MIN = Decimal("1")
HUMIDITY_MAX = Decimal("100")
HUMIDITY_QUANT = Decimal("0.01")


class ClimateLogCreateSchema(Schema):
    room_id = fields.Int(required=True, data_key="roomId")
    recorded_at = fields.DateTime(required=True, data_key="recordedAt")
    temp_c = fields.Float(required=True, data_key="tempC")
    humidity_pct = fields.Decimal(
        required=True,
        data_key="humidityPct",
        error_messages={"invalid": "humidityPct 必须是数字"},
    )
    co2_ppm = fields.Float(allow_none=True, data_key="co2Ppm")
    notes = fields.Str(allow_none=True)

    @validates_schema
    def validate_humidity(self, data, **kwargs):
        h = data.get("humidity_pct")
        # Decimal comparison — rejects 0/101 and boundary-adjacent values outside [1, 100].
        if not isinstance(h, Decimal) or not h.is_finite() or h < HUMIDITY_MIN or h > HUMIDITY_MAX:
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
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        v = v.quantize(HUMIDITY_QUANT)
        # Render whole values as int (88, not 88.0) while preserving fractions (1.5).
        return int(v) if v == v.to_integral_value() else float(v)


def quantize_humidity(raw) -> Decimal:
    if not isinstance(raw, Decimal):
        raw = Decimal(str(raw))
    return raw.quantize(HUMIDITY_QUANT, rounding=ROUND_HALF_UP)
