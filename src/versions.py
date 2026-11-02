"""Comparison, normalization and ranges for NuGet package versions."""

import re

from .config import VERSION_PATTERN


def version_key(version):
    """Compare four numeric fields and numeric-aware prerelease labels."""
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"Invalid version: {version}")
    name = version.split("+", 1)[0].lower()
    number, marker, suffix = name.partition("-")
    fields = [int(value) for value in number.split(".")]
    fields += [0] * (4 - len(fields))
    labels = ()
    if marker:
        labels = tuple(
            (0, int(value)) if value.isdigit() else (1, value)
            for value in suffix.split(".")
        )
    return tuple(fields), not bool(marker), labels


def normalize(version):
    """Normalize an exact NuGet version for Flat Container URLs."""
    numbers, stable, labels = version_key(version)
    fields = list(numbers)
    if not fields[-1]:
        fields.pop()
    normalized = ".".join(map(str, fields))
    if not stable:
        normalized += "-" + ".".join(str(part[1]) for part in labels)
    return normalized


def parse_bounds(requirement):
    """Return lower/upper versions and their inclusive flags."""
    value = requirement.strip()
    if value in ("", "*"):
        return None, None, True, True
    if value[0] in "[(":
        if value[-1] not in ")]":
            raise ValueError("Unclosed version range")
        inside = value[1:-1]
        if "," not in inside:
            if value[0] == "[" and value[-1] == "]":
                key = version_key(inside)
                return key, key, True, True
            raise ValueError("Invalid exact-version range")
        lower, upper = (part.strip() for part in inside.split(",", 1))
        return (version_key(lower) if lower else None,
                version_key(upper) if upper else None,
                value[0] == "[", value[-1] == "]")
    return version_key(value), None, True, False


def satisfies(version, bounds):
    """Evaluate both inclusive or exclusive range boundaries."""
    lower, upper, low_inclusive, high_inclusive = bounds
    current = version_key(version)
    low_ok = lower is None or current > lower
    high_ok = upper is None or current < upper
    return (low_ok or (low_inclusive and current == lower)) and (
        high_ok or (high_inclusive and current == upper)
    )


def select_version(versions, requirement):
    """Choose lowest compatible version, or highest stable floating one."""
    value = requirement.strip()
    floating = value.endswith(".*")
    if floating:
        prefix = value[:-1]
        version_key(value[:-2])
        pool = [item for item in versions if item.startswith(prefix)]
        bounds = parse_bounds("*")
    else:
        pool = versions
        bounds = parse_bounds(value)
    candidates = [
        item for item in pool
        if satisfies(item, bounds)
        and (version_key(item)[1] or "-" in value)
    ]
    if not candidates:
        raise ValueError(f"No version satisfies {requirement!r}")
    chosen = max if floating else min
    return normalize(chosen(candidates, key=version_key))
