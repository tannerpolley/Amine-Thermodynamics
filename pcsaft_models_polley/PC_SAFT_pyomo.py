from pyomo.environ import (ConcreteModel,
                           Var, Param,
                           Reals,
                           exp, log,
                           value, Constraint, Expression)
# import third party libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class PhyCons(object):
    a_ni = np.array([[0.9105631445, -0.3084016918, -0.0906148351],
                     [0.6361281449, 0.1860531159, 0.4527842806],
                     [2.6861347891, -2.5030047259, 0.5962700728],
                     [-26.547362491, 21.419793629, -1.7241829131],
                     [97.759208784, -65.255885330, -4.1302112531],
                     [-159.59154087, 83.318680481, 13.776631870],
                     [91.297774084, -33.746922930, -8.6728470368]])
    a_ni = a_ni.T

    b_ni = np.array([[0.7240946941, -0.5755498075, 0.0976883116],
                     [2.2382791861, 0.6995095521, -0.2557574982],
                     [-4.0025849485, 3.8925673390, -9.1558561530],
                     [-21.003576815, -17.215471648, 20.642075974],
                     [26.855641363, 192.67226447, -38.804430052],
                     [206.55133841, -161.82646165, 93.626774077],
                     [-355.60235612, -165.20769346, -29.666905585]])
    b_ni = b_ni.T

    kb = 1.380649e-23  # J/K
    N_A = 6.0221e23  # 1/mol
    R = 8.314  # J/mol-K
    π = np.pi


x = np.asarray([1. - 1e-5, 1e-5])
m = np.asarray([1.9599, 1])
s = np.asarray([2.363, 2])
e = np.asarray([279.42, 300])
volAB = np.asarray([0.1750, 0])
eAB = np.asarray([2059.28, 0])
dial = 75
z = np.asarray([0., 1.])

t = 40 + 273.15
p = 101325
# s = np.asarray([2.7927 + 10.11*np.exp(-0.01775*t) - 1.417*np.exp(-0.01146*t)]) # temperature dependent sigma is used for better accuracy
data = {'T': t, 'P': p, 'x': x, 'm': m, 's': s, 'e': e, 'e_assoc': eAB, 'vol_a': volAB,
        'k_ij': np.array([[0, 0], [0, 0]]),
        'dielc': dial,
        }

data = {

}

model = ConcreteModel()

model.T = Param(initialize=float(data['T']), doc='Temperature (K)')
model.P = Param(initialize=float(data['P']), doc='Pressure (Pa)')
model.x = Param(initialize=float(data['x']), doc='Liquid Mole Fraction')
model.m = Param(initialize=float(data['m']), doc='Segment number for each component')
model.s = Param(initialize=float(data['s']), doc='Segment diameter for each component')
model.e = Param(initialize=float(data['e']), doc='Dispersion energy of each component')
model.vol_a = Param(initialize=float(data['vol_a']), doc='Effective association volume of the associating components')
model.e_assoc = Param(initialize=float(data['e_assoc']), doc='Association energy of the associating components')

model.k = Param(initialize=float(len(data['x'])), doc='Number of parameters')


def rule_d(b):
    return b.s * (1 - .12 * exp(-3 * b.e / b.T))


model.d = Expression(rule=rule_d)

def rule_s_ij(b):
    return np.array([[1 / 2 * (b.s[i] + b.s[j]) for j in range(b.k)] for i in range(b.k)])



