"""Confidence score calculation for detection results."""

from typing import Dict


def compute_confidence_score(detection_result: Dict) -> float:
    """Compute a confidence score (0.0–1.0) for a detection result dict.

    Evaluates:
    - File type detection certainty
    - Delimiter consistency across sampled lines
    - Multiline vs HDR classification ambiguity
    - Header line confidence
    - Trailer detection completeness
    """
    score = 1.0
    file_type = detection_result.get("file_type")

    if file_type is None:
        return 0.0

    if file_type == "fixed":
        score -= 0.3  # fixed-width is the fallback — least confident

    if file_type == "delimited":
        delim = detection_result.get("delimiter")
        scores = detection_result.get("_delimiter_scores", {})
        if delim and scores:
            best_score = scores.get(delim, 0)
            next_best = sorted(scores.values(), reverse=True)
            next_best = next_best[1] if len(next_best) > 1 else 0
            if best_score == 0:
                score -= 0.3
            elif best_score < next_best * 2:
                score -= 0.15  # ambiguous delimiter

    if detection_result.get("is_multiline"):
        if not detection_result.get("header_prefix") and not detection_result.get("ml_record_types"):
            score -= 0.2

    has_trailer = detection_result.get("trailer_prefix") is not None
    is_multiline = detection_result.get("is_multiline", False)
    if is_multiline and not has_trailer:
        score -= 0.1  # possible missing trailer

    header = detection_result.get("has_header", False)
    if file_type == "delimited" and not header:
        score -= 0.1  # no header row makes column naming harder

    return max(0.0, round(score, 2))
