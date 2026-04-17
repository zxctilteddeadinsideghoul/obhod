from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EquipmentStabilityInput:
    history_depth_days: int
    warnings_last_30_days: int
    critical_last_30_days: int
    defects_last_90_days: int


@dataclass(frozen=True)
class EquipmentStabilityResult:
    stability_score: int
    risk_factor: float
    basis: dict


class EquipmentStabilityCalculator(Protocol):
    def calculate(self, data: EquipmentStabilityInput) -> EquipmentStabilityResult:
        pass


@dataclass(frozen=True)
class DefectSeverityInput:
    impact_score: int
    safety_score: int
    deviation_score: int
    repeat_score: int
    downtime_score: int
    equipment_risk_factor: float = 1.0


@dataclass(frozen=True)
class DefectSeverityResult:
    base_score: int
    final_score: float
    severity_level: int
    severity: str
    factors: dict
    rules_applied: list[str]


class DefectSeverityCalculator(Protocol):
    def calculate(self, data: DefectSeverityInput) -> DefectSeverityResult:
        pass


class RuleBasedEquipmentStabilityCalculator:
    def calculate(self, data: EquipmentStabilityInput) -> EquipmentStabilityResult:
        history_penalty = self._history_penalty(data.history_depth_days)
        warning_penalty = min(data.warnings_last_30_days * 3, 30)
        critical_penalty = min(data.critical_last_30_days * 10, 40)
        defect_penalty = min(data.defects_last_90_days * 7, 35)

        stability_score = self._clamp_score(
            100 - history_penalty - warning_penalty - critical_penalty - defect_penalty
        )
        risk_factor = round(1 + (100 - stability_score) / 100, 2)

        return EquipmentStabilityResult(
            stability_score=stability_score,
            risk_factor=risk_factor,
            basis={
                "historyDepthDays": data.history_depth_days,
                "warningsLast30Days": data.warnings_last_30_days,
                "criticalLast30Days": data.critical_last_30_days,
                "defectsLast90Days": data.defects_last_90_days,
                "penalties": {
                    "history": history_penalty,
                    "warning": warning_penalty,
                    "critical": critical_penalty,
                    "defect": defect_penalty,
                },
            },
        )

    def _history_penalty(self, days: int) -> int:
        if days >= 180:
            return 0
        if days >= 90:
            return 5
        if days >= 30:
            return 10
        if days >= 7:
            return 20
        if days > 0:
            return 30
        return 35

    def _clamp_score(self, value: int) -> int:
        return max(0, min(100, value))


class RuleBasedDefectSeverityCalculator:
    def calculate(self, data: DefectSeverityInput) -> DefectSeverityResult:
        self._validate_score("impact_score", data.impact_score)
        self._validate_score("safety_score", data.safety_score)
        self._validate_score("deviation_score", data.deviation_score)
        self._validate_score("repeat_score", data.repeat_score)
        self._validate_score("downtime_score", data.downtime_score)

        base_score = (
            data.impact_score
            + data.safety_score
            + data.deviation_score
            + data.repeat_score
            + data.downtime_score
        )
        final_score = round(base_score * data.equipment_risk_factor, 2)
        severity_level, severity = self._map_score(final_score)
        rules_applied: list[str] = []

        if data.safety_score == 2 and severity_level < 4:
            severity_level, severity = 4, "high"
            rules_applied.append("direct_safety_risk_min_high")

        if data.deviation_score == 2 and severity_level < 4:
            severity_level, severity = 4, "high"
            rules_applied.append("critical_deviation_min_high")

        if data.impact_score == 2 and data.downtime_score == 2:
            severity_level, severity = 5, "critical"
            rules_applied.append("unstable_work_and_downtime_risk_critical")

        return DefectSeverityResult(
            base_score=base_score,
            final_score=final_score,
            severity_level=severity_level,
            severity=severity,
            factors={
                "impact": data.impact_score,
                "safety": data.safety_score,
                "deviation": data.deviation_score,
                "repeat": data.repeat_score,
                "downtime": data.downtime_score,
                "equipmentRiskFactor": data.equipment_risk_factor,
            },
            rules_applied=rules_applied,
        )

    def _map_score(self, score: float) -> tuple[int, str]:
        if score <= 1:
            return 1, "info"
        if score <= 3:
            return 2, "low"
        if score <= 5:
            return 3, "medium"
        if score <= 7:
            return 4, "high"
        return 5, "critical"

    def _validate_score(self, field_name: str, value: int) -> None:
        if value < 0 or value > 2:
            raise ValueError(f"{field_name} must be between 0 and 2")
