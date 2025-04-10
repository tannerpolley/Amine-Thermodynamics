# encoding: utf-8
# module pcsaft
# from C:\Users\Tanner\anaconda3\lib\site-packages\pcsaft.cp39-win_amd64.pyd
# by generator 1.147
# no doc

# imports
import builtins as __builtins__ # <module 'builtins' (built-in)>
import numpy as np # C:\Users\Tanner\anaconda3\lib\site-packages\numpy\__init__.py

# functions

def aly_lee(*args, **kwargs): # real signature unknown
    """
    Calculate the ideal gas isobaric heat capacity using the Aly-Lee equation.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        c : ndarray, shape (5,)
            Constants for the Aly-Lee equation
    
        Returns
        -------
        cp_ideal : float
            Ideal gas isobaric heat capacity (J mol\ :sup:`-1` K\ :sup:`-1`)
    
        References
        ----------
        - F. A. Aly and L. L. Lee, “Self-consistent equations for calculating the ideal gas heat capacity, enthalpy, and entropy,” Fluid Phase Equilibria, vol. 6, no. 3–4, pp. 169–179, 1981.
    """
    pass

def check_association(*args, **kwargs): # real signature unknown
    pass

def check_input(*args, **kwargs): # real signature unknown
    pass

def create_assoc_matrix(*args, **kwargs): # real signature unknown
    pass

def create_struct(*args, **kwargs): # real signature unknown
    """ Convert PC-SAFT parameters to a C++ struct. """
    pass

def deepcopy(x, memo=None, _nil='[]'): # reliably restored by inspect
    """
    Deep copy operation on arbitrary Python objects.
    
        See the module's __doc__ string for more info.
    """
    pass

def dielc_water(*args, **kwargs): # real signature unknown
    """
    Return the dielectric constant of water at the given temperature.
    
        This equation was fit to values given in the reference. For temperatures from
        263.15 to 368.15 K values at 1 bar were used. For temperatures from 368.15 to
        443.15 K values at 10 bar were used. Below 263.15 K and above 443.15 K an
        error is raised.
    
        Parameters
        ----------
        t : float
            Temperature (K)
    
        Returns
        -------
        dielc : float
            Dielectric constant of water
    
        References
        ----------
        - D. G. Archer and P. Wang, “The Dielectric Constant of Water and Debye‐Hückel Limiting Law Slopes,” J. Phys. Chem. Ref. Data, vol. 19, no. 2, pp. 371–411, Mar. 1990.
    """
    pass

def ensure_numpy_input(*args, **kwargs): # real signature unknown
    pass

def flashPQ(*args, **kwargs): # real signature unknown
    """
    Calculate the temperature of the system where vapor and liquid phases are in equilibrium.
    
        Parameters
        ----------
        p : float
            Pressure (Pa)
        q : float
            Mole fraction of the fluid in the vapor phase
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        t_guess : float
            Initial guess for the temperature (K) (optional)
    
        Returns
        -------
        t : float
            Temperature (K)
        xl : ndarray, shape (n,)
            Liquid mole fractions after flash
        xv : ndarray, shape (n,)
            Vapor mole fractions after flash
    
        Notes
        -----
        To solve the PQ flash the temperature must be varied. This adds additional complexity
        for water and electrolyte mixtures. For water, a temperature dependent sigma is often
        used. However, there does not appear to be a way to pass a Python function to the C++
        code without requiring the user to compile it using Cython. To avoid this, the `flashPQ`
        function uses the following relationship internally to calculate sigma for water as a
        function of temperature: ::
    
            3.8395 + 1.2828 * exp(-0.0074944 * t) - 1.3939 * exp(-0.00056029 * t);
    
        For electrolyte solutions the dielectric constant is calculated using the `dielc_water`
        function. This means that the sigma value for water and the dielectric constant given by
        the user are not used by the `flashPQ` function.
    
        The code identifies which component is water by the epsilon/k value. Therefore, when
        using `flashPQ` with water `e` must be exactly 353.9449, if you want the temperature
        dependence of sigma to be accounted for.
    
        If you want to use different functions for temperature dependent parameters with `flashPQ`
        then you will need to modify the source code and recompile it.
    """
    pass

def flashTQ(*args, **kwargs): # real signature unknown
    """
    Calculate the pressure of the system where vapor and liquid phases are in equilibrium.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        q : float
            Mole fraction of the fluid in the vapor phase
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        p_guess : float
            Initial guess for the pressure (Pa) (optional)
    
        Returns
        -------
        p : float
            Pressure (Pa)
        xl : ndarray, shape (n,)
            Liquid mole fractions after flash
        xv : ndarray, shape (n,)
            Vapor mole fractions after flash
    """
    pass

def np_to_vector_double(*args, **kwargs): # real signature unknown
    """ Take a numpy array and return a C++ vector. """
    pass

def np_to_vector_int(*args, **kwargs): # real signature unknown
    """ Take a numpy array and return a C++ vector. """
    pass

def pcsaft_ares(*args, **kwargs): # real signature unknown
    """
    Calculate the residual Helmholtz energy.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        ares : float
            Residual Helmholtz energy (J mol\ :sup:`-1`)
    """
    pass

def pcsaft_cp(*args, **kwargs): # real signature unknown
    """
    Calculate the specific molar isobaric heat capacity.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        aly_lee_params : ndarray, shape (5,)
            Constants for the Aly-Lee equation. Can be substituted with parameters for
            another equation if the ideal gas heat capacity is given using a different
            equation.
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each compopynent. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        cp : float
            Specific molar isobaric heat capacity (J mol\ :sup:`-1` K\ :sup:`-1`)
    """
    pass

def pcsaft_dadt(*args, **kwargs): # real signature unknown
    """
    Calculate the temperature derivative of the residual Helmholtz energy.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        dadt : float
            Temperature derivative of the residual Helmholtz energy (J mol\ :sup:`-1`)
    """
    pass

def pcsaft_den(*args, **kwargs): # real signature unknown
    """
    Calculate the molar density.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        p : float
            Pressure (Pa)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        phase : string
            The phase for which the calculation is performed. Options: "liq" (liquid),
            "vap" (vapor).
    
        Returns
        -------
        rho : float
            Molar density (mol m\ :sup:`-3`)
    """
    pass

def pcsaft_fugcoef(*args, **kwargs): # real signature unknown
    """
    Calculate the fugacity coefficients for one phase of the system.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        fugcoef : ndarray, shape (n,)
            Fugacity coefficients of each component.
    """
    pass

def pcsaft_gres(*args, **kwargs): # real signature unknown
    """
    Calculate the residual Gibbs energy for one phase of the system.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        gres : float
            Residual Gibbs energy (J mol\ :sup:`-1`)
    """
    pass

def pcsaft_hres(*args, **kwargs): # real signature unknown
    """
    Calculate the residual enthalpy for one phase of the system.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        hres : float
            Residual enthalpy (J mol\ :sup:`-1`)
    """
    pass

def pcsaft_Hvap(*args, **kwargs): # real signature unknown
    """
    Calculate the enthalpy of vaporization.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        p_guess : float
            Guess for the vapor pressure (Pa) (optional)
    
        Returns
        -------
        output : list
            A list containing the following results:
                0 : enthalpy of vaporization (J/mol), float
                1 : vapor pressure (Pa), float
    """
    pass

def pcsaft_lnfugcoef(*args, **kwargs): # real signature unknown
    """
    Calculate the natural logarithm of the fugacity coefficients for one phase of the system.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        lnfugcoef : ndarray, shape (n,)
            Natural logarithm of the fugacity coefficients for each component.
    """
    pass

def pcsaft_osmoticC(*args, **kwargs): # real signature unknown
    """
    Calculate the osmotic coefficient.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        osmC : float
            Molal osmotic coefficient
    """
    pass

def pcsaft_p(*args, **kwargs): # real signature unknown
    """
    Calculate pressure.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        P : float
            Pressure (Pa)
    """
    pass

def pcsaft_sres(*args, **kwargs): # real signature unknown
    """
    Calculate the residual entropy (constant volume) for one phase of the system.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        sres : float
            Residual entropy (J mol\ :sup:`-1` K\ :sup:`-1`)
    """
    pass

def pcsaft_Z(*args, **kwargs): # real signature unknown
    """
    Calculate the compressibility factor.
    
        Parameters
        ----------
        t : float
            Temperature (K)
        rho : float
            Molar density (mol m\ :sup:`-3`)
        x : ndarray, shape (n,)
            Mole fractions of each component. It has a length of n, where n is
            the number of components in the system.
        params : dict
            A dictionary containing PC-SAFT parameters that can be passed for
            use in PC-SAFT:
    
            m : ndarray, shape (n,)
                Segment number for each component.
            s : ndarray, shape (n,)
                Segment diameter for each component. For ions this is the diameter of
                the hydrated ion. Units of Angstrom.
            e : ndarray, shape (n,)
                Dispersion energy of each component. For ions this is the dispersion
                energy of the hydrated ion. Units of K.
            k_ij : ndarray, shape (n,n)
                Binary interaction parameters between components in the mixture.
                (dimensions: ncomp x ncomp)
            e_assoc : ndarray, shape (n,)
                Association energy of the associating components. For non associating
                compounds this is set to 0. Units of K.
            vol_a : ndarray, shape (n,)
                Effective association volume of the associating components. For non
                associating compounds this is set to 0.
            dipm : ndarray, shape (n,)
                Dipole moment of the polar components. For components where the dipole
                term is not used this is set to 0. Units of Debye.
            dip_num : ndarray, shape (n,)
                The effective number of dipole functional groups on each component
                molecule. Generally this is set to 1, but some implementations use this
                as an adjustable parameter that is fit to data.
            z : ndarray, shape (n,)
                Charge number of the ions
            dielc : float
                Dielectric constant of the medium to be used for electrolyte
                calculations.
            assoc_scheme : list, shape (n,)
                The types of association sites for each component. Use `None` for molecules
                without association sites. If a molecule has multiple association sites,
                use a nested list for that component to specify the association scheme for
                each site. The accepted association schemes are those given by Huang and
                Radosz (1990): 1, 2A, 2B, 3A, 3B, 4A, 4B, 4C. If `e_assoc` and `vol_a` are
                given but `assoc_scheme` is not, the 2B association scheme is assumed (which
                would, for example, correspond to one hydroxyl functional group).
    
        Returns
        -------
        Z : float
            Compressibility factor
    """
    pass

# classes

class InputError(Exception):
    # no doc
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    __weakref__ = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """list of weak references to the object (if defined)"""



class SolutionError(Exception):
    # no doc
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    __weakref__ = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """list of weak references to the object (if defined)"""



# variables with complex values

__loader__ = None # (!) real value is '<_frozen_importlib_external.ExtensionFileLoader object at 0x00000192C5A317F0>'

__spec__ = None # (!) real value is "ModuleSpec(name='pcsaft', loader=<_frozen_importlib_external.ExtensionFileLoader object at 0x00000192C5A317F0>, origin='C:\\\\Users\\\\Tanner\\\\anaconda3\\\\lib\\\\site-packages\\\\pcsaft.cp39-win_amd64.pyd')"

__test__ = {}

