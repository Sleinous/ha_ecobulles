"""Persistent accounting for the Ecobulles CO2 valve-open counter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CO2UsageState:
    """Keep bottle usage cumulative across resets of the device counter."""

    offset_ms: int = 0
    baseline_ms: int = 0
    last_raw_ms: int | None = None

    def apply(self, raw_total_ms: int | None) -> int | None:
        """Apply an API reading and return valve-open time for this bottle."""
        if raw_total_ms is None:
            return None

        raw_total_ms = int(raw_total_ms)
        if raw_total_ms < 0:
            raise ValueError("CO2 valve-open time cannot be negative")

        if self.last_raw_ms is not None and raw_total_ms < self.last_raw_ms:
            # The box or portal reset its counter. Preserve use from this segment.
            self.offset_ms += max(0, self.last_raw_ms - self.baseline_ms)
            self.baseline_ms = 0

        self.last_raw_ms = raw_total_ms
        return self.offset_ms + max(0, raw_total_ms - self.baseline_ms)

    def as_dict(self) -> dict[str, int | None]:
        """Serialize counter state for Home Assistant storage."""
        return {
            "offset_ms": self.offset_ms,
            "baseline_ms": self.baseline_ms,
            "last_raw_ms": self.last_raw_ms,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, int | None] | None) -> "CO2UsageState":
        """Restore counter state from Home Assistant storage."""
        raw = raw or {}
        last_raw_ms = raw.get("last_raw_ms")
        return cls(
            offset_ms=max(0, int(raw.get("offset_ms", 0) or 0)),
            baseline_ms=max(0, int(raw.get("baseline_ms", 0) or 0)),
            last_raw_ms=(
                None if last_raw_ms is None else max(0, int(last_raw_ms))
            ),
        )
