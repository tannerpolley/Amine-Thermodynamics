from pcsaft import pcsaft_den, pcsaft_fugcoef
from pcsaft_electrolyte import pcsaft_den as pcsaft_den_2, pcsaft_fugcoef as pcsaft_fugcoef_2
import numpy as np

x = np.asarray([1.-1e-5, 1e-5])
m = np.asarray([1.9599, 1])
s = np.asarray([2.363, 2])
e = np.asarray([279.42, 300])
volAB = np.asarray([0.1750, 0])
eAB = np.asarray([2059.28, 0])
dial = 75
z = np.asarray([0., 1.])


t = 40+273.15
p = 101325
# s = np.asarray([2.7927 + 10.11*np.exp(-0.01775*t) - 1.417*np.exp(-0.01146*t)]) # temperature dependent sigma is used for better accuracy
pyargs = {'m':m, 's':s, 'e':e, 'e_assoc':eAB, 'vol_a':volAB,
          'dielc': dial,
          'z': z
          }
#
# pyargs2 = {'e_assoc':eAB, 'vol_a':volAB,
#           # 'dial': dial,
#           # 'z': z
#           }

den = pcsaft_den_2(x, m, s, e, t, p, e_assoc=eAB, vol_a=volAB, dielc=dial, z=z)
print(pcsaft_fugcoef_2(x, m, s, e, t, den, e_assoc=eAB, vol_a=volAB, dielc=dial, z=z))
den = pcsaft_den(t, p, x, pyargs, phase='liq')
print(den)
print(pcsaft_fugcoef(t, den, x, pyargs))
print('Density of water at {} K: {} mol m^-3'.format(t, den))