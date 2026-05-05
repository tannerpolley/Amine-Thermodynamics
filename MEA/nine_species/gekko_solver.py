import os

from gekko import GEKKO
import numpy as np

from MEA.common.config import REPO_ROOT


def _configure_repo_tmp() -> None:
    repo_tmp = REPO_ROOT / "out" / "tmp" / "gekko"
    current_tmp = os.environ.get("TMP") or os.environ.get("TEMP") or ""
    if "MEA-Thermodynamics" in current_tmp and "\\out\\tmp\\" in current_tmp:
        return
    repo_tmp.mkdir(parents=True, exist_ok=True)
    for key in ("TEMP", "TMP", "TMPDIR"):
        os.environ[key] = str(repo_tmp)


_configure_repo_tmp()


def get_x_guess(x_0, log_k_eq, v_ij):
    m = GEKKO(remote=False)
    m.options.IMODE = 3
    m.options.SOLVER = 3

    # variables
    eps = m.Array(m.Var, len(log_k_eq), value=0)
    x = m.Array(m.Var, len(x_0), value=1/len(x_0))  # tiny lb to keep log() safe
    # x[0].value = 1e-9

    # linear mass-balance constraints
    eqs = []
    for j, xj in enumerate(x):
        # build a pure-Gekko linear combination
        eps_sum = 0
        for i, epsi in enumerate(eps):
            eps_sum = eps_sum + float(v_ij[i, j]) * epsi
        eqs.append(xj == float(x_0[j]) + eps_sum)
        m.Equation(xj >= 1e-8)
    m.Equations(eqs)

    # elementwise sum to avoid Python containers
    x_logsum = m.sum([xi * m.log(xi) for xi in x])
    log_k_eq_sum = m.sum([float(log_k_eq[i]) * eps[i] for i in range(len(eps))])

    obj = - log_k_eq_sum + x_logsum - m.sum(x) * m.log(m.sum(x))
    m.Minimize(obj)

    # m.Equation(x_sum == 1.0)
    m.options.MAX_ITER = 5000
    m.options.RTOL = 1e-10
    m.options.OTOL = 1e-10
    m.options.NODES = 3
    # m.options.SCALING = 2
    m.solve(disp=False)

    # print(m.options.OBJFCNVAL)

    eps_sol = [ei.value[0] for ei in eps]
    x_sol   = [xi.value[0] for xi in x]

    # print(x_sol)
    return x_sol, eps_sol


def solve_ChEq(
    x_0,
    x_guess,
    log_k_eq,
    v_ij,
    s_ij,
    scales,
    *,
    lower_bound=1e-12,
    max_iter=5000,
    rtol=1e-2,
    otol=1e-2,
):

    m = GEKKO(remote=False)
    m.options.IMODE = 1
    m.options.SOLVER = 3

    x_scaled = m.Array(m.Var, len(x_guess))  # tiny lb to keep log() safe
    x = []
    for i in range(len(x_guess)):
        x_scaled[i].value = x_guess[i]
        x_scaled[i].lower = lower_bound
        x.append(m.Intermediate(x_scaled[i] * scales[i]))

    # linear mass-balance constraints
    eqs = []
    for i, log_k_eq_i in enumerate(log_k_eq):
        Kee_i = 1
        for j, xj in enumerate(x):
            Kee_i *= x[j] ** v_ij[i, j]
        eqs.append(0.0 == (m.log(Kee_i) - log_k_eq[i]) / m.log(Kee_i))

    for i in range(len(s_ij)):

        sum_i = m.sum([x[j]*s_ij[i, j] for j in range(len(x_0))])
        if i < 3:
            eqs.append(0.0 == (float(x_0[i]) - sum_i) / float(x_0[i]))
        else:
            eqs.append(0.0 == (float(x_0[i]) - sum_i) / (x[3] * s_ij[i, 3]))

    m.Equations(eqs)
    m.options.MAX_ITER = max_iter
    m.options.RTOL = rtol
    m.options.OTOL = otol
    m.options.NODES = 2
    m.solve(disp=False)

    # print(m.options.OBJFCNVAL)

    x_sol = [xi.value[0] for xi in x]

    return np.array(x_sol)


