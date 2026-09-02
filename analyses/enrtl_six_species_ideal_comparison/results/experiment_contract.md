# Experiment contract

Primary experiment: compare nine and six species at identical temperature, loading, feed, reaction source, and reporting basis. The ideal lane uses the source manifest and exact six-species reaction projection. The activity-aware lane uses the Engine candidate EOS for both species sets, the same source-standard-state transfer, and a temporary SciPy equilibrium solve enforcing material-balance ratios, charge balance, and reaction affinities.

The comparison is diagnostic. The Engine packet remains a provisional candidate, and the temporary SciPy bridge is not production chemistry or a parameter-adoption path. VLE pressure claims require a separate matched bubble calculation and are not inferred from this fixed-T,P lane.
