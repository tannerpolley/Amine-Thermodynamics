# Disposable Engine/SciPy lane

status: verified_disposable_scipy_eos_lane
state_count: 3 matched fixed-T,P states
pressure_Pa: 100000
temperatures_K: 293.15, 313.15, 323.15
maximum_abs_solver_residual: 2.449951e-11

SciPy solved the material-balance ratios, electroneutrality, and reaction affinities. The installed Engine wheel evaluated each liquid EOS state and the declared source-reference transfer. The Engine reactive declaration/count gate was not used as a scientific stop condition.

The packet is diagnostic/provisional. The only retained claim is matched fixed-T,P liquid composition; this lane does not establish VLE pressure agreement, global equilibrium, or parameter adoption.
