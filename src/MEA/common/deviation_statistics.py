"""Deviation statistics for paired observations and predictions."""


def deviation_statistics(pairs, unit=None):
    """Relative errors use nonzero observations; absolute errors retain every pair."""
    rel = [(p-o)/o*100 for o,p in pairs if o != 0]
    return dict(rows=len(pairs),relative_rows=len(rel),relative_undefined=len(pairs)-len(rel),
                AARD_percent=sum(map(abs,rel))/len(rel) if rel else None,
                bias_percent=sum(rel)/len(rel) if rel else None,
                mean_abs_error=sum(abs(p-o) for o,p in pairs)/len(pairs),
                mean_signed_error_predicted_minus_observed=sum(p-o for o,p in pairs)/len(pairs),unit=unit)
