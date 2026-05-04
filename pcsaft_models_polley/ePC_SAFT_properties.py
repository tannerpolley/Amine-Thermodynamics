import numpy as np
import types

pcsaft_prop = {
    'CO2': {
        'MW': 44.01e-3,  # kg/mol
        'm': 2.079, 's': 2.7852, 'e': 169.21,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 1.4122 # Schick 2022
    },
    'MEA-2B': {
        'MW': 61.08e-3,  # kg/mol
        'm': 3.0353, 's': 3.0435, 'e': 277.174,
        'e_assoc': 2586.3, 'vol_a': 0.037470, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 32.
    },
    'MEA-4C': {
        'MW': 61.08e-3,  # kg/mol
        'm': 4.5208, 's': 2.6574, 'e': 237.6864,
        'e_assoc': 989.8984, 'vol_a': 0.187533, 'assoc_scheme': '4C',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 0.
    },
    'H2O-2B-CC': {
        'MW': 18.01528e-3,  # kg/mol
        'm': 1.9599, 's': 2.362, 'e': 279.42,
        'e_assoc': 2059.28, 'vol_a': 0.1750, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0.,
        'dielc': 78.09,
    },
    'H2O-4C-CC': {
        'MW': 18.01528e-3,  # kg/mol
        'm': 2.1945, 's': 2.229, 'e': 141.66,
        'e_assoc': 1804.17, 'vol_a': 0.2039, 'assoc_scheme': '4C',
        'dipm': 0., 'dip_num': 1,
        'z': 0.,
        'dielc': 78.09,
    },
    'MEAH+': {
        'MW': 62.09e-3,  # kg/mol
        'm': 1., 's': 3.0435, 'e': 277.174,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 1., 'dielc': 8.
    },
    'MEACOO-': {
        'MW': 75.07e-3,  # kg/mol
        'm': 1., 's': 3.0435, 'e': 277.174,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1., 'dielc': 8.
    },
    'HCO3-': {
        'MW': 61.0168e-3,  # kg/mol
        'm': 1., 's': 3., 'e': 300.,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1., 'dielc': 8.
    },
    'CO32-': {
        'MW': 60.01e-3,  # kg/mol
        'm': 1., 's': 3., 'e': 300.,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1., 'dielc': 8.
    },
    'H3O+': {
        'MW': 19.02e-3,  # kg/mol
        'm': 1., 's': 3., 'e': 300.,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 1., 'dielc': 8.
    },
    'OH-': {
        'MW': 17.01e-3,  # kg/mol
        'm': 1., 's': 3., 'e': 300.,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1., 'dielc': 8.
    },

    'Hexane': {
        'MW': 86.17848e-3,  # kg/mol
        'm': 3.0576, 's': 3.7983, 'e': 236.77,
        'e_assoc': 0.0, 'vol_a': 0.0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 0.
    },
    'Methane': {
        'MW': 16.04e-3,  # kg/mol
        'm': 1.0, 's': 3.7039, 'e': 150.03,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 0.},
    'Ethane': {
        'MW': 30.07e-3,  # kg/mol
        'm': 1.6069, 's': 3.5206, 'e': 191.42,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 0.},
    'Propane': {
        'MW': 44.10e-3,  # kg/mol
        'm': 2.0020, 's': 3.6184, 'e': 208.11,
        'e_assoc': 0., 'vol_a': 0., 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 0.},
    'Methanol': {
        'MW': 32.04e-3,  # kg/mol
        'm': 1.5255, 's': 3.2300, 'e': 188.90,
        'e_assoc': 2899.5, 'vol_a': 0.03518, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 33.05},
    'Ethanol': {
        'MW': 46.068e-3,  # kg/mol
        'm': 2.3827, 's': 3.1771, 'e': 198.24,
        'e_assoc': 2653.4, 'vol_a': 0.03238, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 24.88},
    'Butanol': {
        'MW': 74.12e-3,  # kg/mol
        'm': 2.7510, 's': 3.6139, 'e': 259.59,
        'e_assoc': 2544.56, 'vol_a': 0.00669, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 20.47},

    'H2O-2B-Li': {
        'MW': 18.01528e-3,  # kg/mol
        'm': 1.2047, 's': lambda T: 2.7927 + (10.11 * np.exp(-.01775 * T) - 1.417 * np.exp(-.01146 * T)), 'e': 353.95,
        'e_assoc': 2425.7, 'vol_a': .04509, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0.,
        # 'dielc': lambda T: -105.2*np.log(T) + 677.480,
        'dielc': 78.09,
    },

    'TOP': {
        'MW': 434.63e-3,  # kg/mol
        'm': 4.2032, 's': 5.4506, 'e': 280.4777,
        'e_assoc': 6393.5, 'vol_a': .0001, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 11
    },
    'IL': {
        'MW': 407.31e-3,  # kg/mol
        'm': 4.073, 's': 4.6432, 'e': 434.6130,
        'e_assoc': 5000, 'vol_a': .1, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 0., 'dielc': 11
    },

    'Li+': {
        'MW': 6.94e-3,  # kg/mol
        'm': 1., 's': 2.8449, 'e': 360.00,
        'e_assoc': 0.0, 'vol_a': 100, 'assoc_scheme': '2B',
        'dipm': 0., 'dip_num': 1,
        'z': 1, 'dielc': 8
    },
    'Na+': {
        'MW': 22.98e-3,  # kg/mol
        'm': 1., 's': 2.8232, 'e': 230.00,
        'e_assoc': 0.0, 'vol_a': 0.0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 1, 'dielc': 8
    },
    'K+': {
        'MW': 39.0983e-3,  # kg/mol
        'm': 1., 's': 3.3417, 'e': 200.00,
        'e_assoc': 0.0, 'vol_a': 0.0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 1, 'dielc': 8
    },
    'Mg2+': {
        'MW': 24.31e-3,  # kg/mol
        'm': 1., 's': 3.1327, 'e': 1500,
        'e_assoc': 0., 'vol_a': 0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': 2, 'dielc': 8
    },
    'F-': {
        'MW': 18.998e-3,  # kg/mol
        'm': 1., 's': 1.7712, 'e': 275.00,
        'e_assoc': 0., 'vol_a': 0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1, 'dielc': 8
    },
    'Cl-': {
        'MW': 35.45e-3,  # kg/mol
        'm': 1., 's': 2.7560, 'e': 170.00,
        'e_assoc': 0., 'vol_a': 0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1, 'dielc': 8
    },
    'Br-': {
        'MW': 79.904e-3,  # kg/mol
        'm': 1., 's': 3.0707, 'e': 190.00,
        'e_assoc': 0., 'vol_a': 0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1, 'dielc': 8
    },
    'I-': {
        'MW': 126.90447e-3,  # kg/mol
        'm': 1., 's': 3.6672, 'e': 200.00,
        'e_assoc': 0., 'vol_a': 0, 'assoc_scheme': None,
        'dipm': 0., 'dip_num': 1,
        'z': -1, 'dielc': 8
    },

}


# Create the binary interaction parameter dictionary for dispersion forces

k_ij_dict = {

    # CO2-MEA-H2O System
    ("CO2", "H2O"): lambda T: -2.2e-2 + 4.2e-4 * (T - 298) - 1.7e-6 * (T - 298),
    ("CO2", "MEA"): 0.0,
    # ("MEA-2B", "H2O-2B-CC"): -0.0420, # Baygi 2015
    ("MEA-2B", "H2O-2B-CC"): 0.250,  # Baygi 2015
    ("MEAH+", "MEACOO-"): 0.0,

    # Example System for hydrocarbons from LearnChemE
    ("Methane", "Ethane"): 3e-4,
    ("Methane", "Propane"): 1.15e-2,
    ("Ethane", "Propane"): 5.10e-3,

    # Lithium Extraction with Ionic Liquids from Yu 2024 10.1016/j.ces.2023.119682
    ("H2O-2B-Li", "IL"): .007,
    ("Li+", "TOP"): .3,
    ("H2O-2B-Li", "TOP"): 1,
    ("TOP", "IL"): 1,
    ("Li+", "IL"): 1,

    # Testing from pubs.acs.org/IECR Article
    # Predicting Thermodynamic Properties of Ions in Single Solvents
    # and in Mixed Solvents Using a Modified Born Term within the ePC-SAFT Framework
    # 10.1021/acs.iecr.5c00475
    # ("Li+", "H2O"): -.2500,
    ("Li+", "H2O-2B-Li"): -.4,
    ("Na+", "H2O-2B-Li"): .0045,
    ("K+", "H2O-2B-Li"): .1997,
    ("F-", "H2O-2B-Li"): 0.000,
    ("Cl-", "H2O-2B-Li"): -.250,
    ("Br-", "H2O-2B-Li"): -.250,
    ("I-", "H2O-2B-Li"): -.250,

    ("Li+", "Ethanol"): -.8,
    ("H2O-2B-Li", "Ethanol"): -.0617,
    ("H2O-2B-Li", "Butanol"): lambda T: 2.94e-4*T - .102,

    ("Li+", "F-"): 0.0,
    ("Na+", "F-"): .665,
    ("K+", "F-"): 1.000,

    # ("Li+", "Cl-"): .669,
    ("Li+", "Cl-"): .8,
    ("Na+", "Cl-"): .317,
    ("K+", "Cl-"): .064,

    ("Li+", "Br-"): .591,
    ("Na+", "Br-"): .290,
    ("K+", "Br-"): -.102,

    ("Li+", "I-"): .002,
    ("Na+", "I-"): .018,
    ("K+", "I-"): -.312,

}

k_ij_dict[("H2O-2B-CC", "MEAH+")] = k_ij_dict[("MEA-2B", "H2O-2B-CC")]
k_ij_dict[("H2O-2B-CC", "MEACOO-")] = k_ij_dict[("MEA-2B", "H2O-2B-CC")]

unique_strings = set()

for key in k_ij_dict:
    unique_strings.update(key)  # key is a tuple, so this adds both elements

# Convert to list if needed
unique_list = list(unique_strings)
for k in unique_list:
    k_ij_dict[(k, k)] = 0.0

for k in k_ij_dict.copy().keys():
    k1, k2 = k
    k_ij_dict[(k2, k1)] = k_ij_dict[(k1, k2)]

# Create the binary interaction parameter dictionary for association forces

k_hb_dict = {
    ("Li+", "TOP"): .3,
    ("Li+", "IL"): 1,
    ("Li+", "H2O"): 1,
    ("Butanol", "H2O"): .026,
}

unique_strings_hb = set()

for key in k_hb_dict:
    unique_strings_hb.update(key)  # key is a tuple, so this adds both elements

# Convert to list if needed
unique_list_hb = list(unique_strings_hb)
for k in unique_list_hb:
    k_hb_dict[(k, k)] = 0.0

for k in k_hb_dict.copy().keys():
    k1, k2 = k
    k_hb_dict[(k2, k1)] = k_hb_dict[(k1, k2)]

l_ij_dict = {
    ("H2O", "Butanol"): -.0044,
}

unique_strings_l_ij = set()

for key in l_ij_dict:
    unique_strings_l_ij.update(key)  # key is a tuple, so this adds both elements

# Convert to list if needed
unique_list_l_ij = list(unique_strings_l_ij)
for k in unique_list_l_ij:
    l_ij_dict[(k, k)] = 0.0

for k in l_ij_dict.copy().keys():
    k1, k2 = k
    l_ij_dict[(k2, k1)] = l_ij_dict[(k1, k2)]



def get_prop_dict(species, T):
    """
    species: list of species names that match dictionary keys in pcsaft_prop
    T: Temperature (K) (often not used, used in calculations of temperature-dependent binary interaction parameters)
    """

    prop_dic = {}

    for prop in pcsaft_prop[species[0]].keys():
        prop_list = []
        for sp in species:
            if isinstance(pcsaft_prop[sp][prop], types.FunctionType):
                prop_list.append(pcsaft_prop[sp][prop](T))
            else:
                prop_list.append(pcsaft_prop[sp][prop])
        if prop == 'assoc_scheme':
            prop_dic[prop] = prop_list
        else:
            prop_dic[prop] = np.array(prop_list)

    n = len(species)

    # Create the binary interaction parameter dictionary and matrix for dispersion forces

    k_ij = np.zeros((n, n))

    for i, sp1 in enumerate(species):
        for j, sp2 in enumerate(species):
            try:
                if isinstance(k_ij_dict[(sp1, sp2)], types.FunctionType):
                    k_ij[i, j] = k_ij_dict[(sp1, sp2)](T)
                else:
                    k_ij[i, j] = k_ij_dict[(sp1, sp2)]
            except KeyError:
                k_ij[i, j] = 0.0

    prop_dic['k_ij'] = k_ij

    # Create the binary interaction parameter dictionary and matrix for assocation forces

    assoc_species = [sp for sp in species if pcsaft_prop[sp]['assoc_scheme'] is not None]
    k_hb = np.zeros((n, n))

    for i, sp1 in enumerate(assoc_species):
        for j, sp2 in enumerate(assoc_species):
            try:
                k_hb[i, j] = k_hb_dict[(sp1, sp2)]
            except KeyError:
                k_hb[i, j] = 0.0

    prop_dic['k_hb'] = k_hb


    l_ij = np.zeros((n, n))

    for i, sp1 in enumerate(species):
        for j, sp2 in enumerate(species):
            try:
                if isinstance(l_ij_dict[(sp1, sp2)], types.FunctionType):
                    l_ij[i, j] = l_ij_dict[(sp1, sp2)](T)
                else:
                    l_ij[i, j] = l_ij_dict[(sp1, sp2)]
            except KeyError:
                l_ij[i, j] = 0.0

    prop_dic['l_ij'] = l_ij

    if np.all(prop_dic['z'] == 0):
        prop_dic['z'] = np.array([])
    #
    # prop_dic['z'] = np.array([])

    return prop_dic
