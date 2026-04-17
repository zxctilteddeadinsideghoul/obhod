#!/usr/bin/env python3
from app.domain import (
    DefectSeverityInput,
    EquipmentStabilityInput,
    RuleBasedDefectSeverityCalculator,
    RuleBasedEquipmentStabilityCalculator,
)


def assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_stable_equipment_has_low_risk_factor() -> None:
    result = RuleBasedEquipmentStabilityCalculator().calculate(
        EquipmentStabilityInput(
            history_depth_days=240,
            warnings_last_30_days=1,
            critical_last_30_days=0,
            defects_last_90_days=0,
        )
    )

    assert_equal(result.stability_score, 97, "Stable equipment score")
    assert_equal(result.risk_factor, 1.03, "Stable equipment risk factor")


def test_unstable_equipment_increases_risk_factor() -> None:
    result = RuleBasedEquipmentStabilityCalculator().calculate(
        EquipmentStabilityInput(
            history_depth_days=120,
            warnings_last_30_days=6,
            critical_last_30_days=2,
            defects_last_90_days=3,
        )
    )

    assert_equal(result.stability_score, 36, "Unstable equipment score")
    assert_equal(result.risk_factor, 1.64, "Unstable equipment risk factor")


def test_same_defect_is_more_important_on_unstable_equipment() -> None:
    calculator = RuleBasedDefectSeverityCalculator()

    stable = calculator.calculate(
        DefectSeverityInput(
            impact_score=1,
            safety_score=0,
            deviation_score=1,
            repeat_score=1,
            downtime_score=1,
            equipment_risk_factor=1.03,
        )
    )
    unstable = calculator.calculate(
        DefectSeverityInput(
            impact_score=1,
            safety_score=0,
            deviation_score=1,
            repeat_score=1,
            downtime_score=1,
            equipment_risk_factor=1.64,
        )
    )

    assert_equal(stable.severity, "medium", "Stable equipment severity")
    assert_equal(unstable.severity, "high", "Unstable equipment severity")
    assert_true(unstable.final_score > stable.final_score, "Risk factor must increase final score")


def test_hard_rules_raise_minimum_severity() -> None:
    result = RuleBasedDefectSeverityCalculator().calculate(
        DefectSeverityInput(
            impact_score=0,
            safety_score=2,
            deviation_score=0,
            repeat_score=0,
            downtime_score=0,
            equipment_risk_factor=1.0,
        )
    )

    assert_equal(result.severity, "high", "Direct safety risk must be at least high")
    assert_true("direct_safety_risk_min_high" in result.rules_applied, "Safety hard rule must be recorded")


def test_invalid_factor_score_is_rejected() -> None:
    try:
        RuleBasedDefectSeverityCalculator().calculate(
            DefectSeverityInput(
                impact_score=3,
                safety_score=0,
                deviation_score=0,
                repeat_score=0,
                downtime_score=0,
                equipment_risk_factor=1.0,
            )
        )
    except ValueError:
        return

    raise AssertionError("Invalid factor score must raise ValueError")


def main() -> int:
    test_stable_equipment_has_low_risk_factor()
    test_unstable_equipment_increases_risk_factor()
    test_same_defect_is_more_important_on_unstable_equipment()
    test_hard_rules_raise_minimum_severity()
    test_invalid_factor_score_is_rejected()
    print("[unit] severity calculators OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
