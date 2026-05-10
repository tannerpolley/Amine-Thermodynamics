\title{
Modeling $\mathrm{CO}_{2}$ solubility in Aqueous Methyldiethanolamine Solutions by Perturbed Chain-SAFT Equation of State
}

\author{
Hassan Pahlavanzadeh *, Sadjad Fakouri Baygi \\ Faculty of Chemical Engineering, Tarbiat Modares University, Tehran, Iran
}

\section*{ARTICLE INFO}

\section*{Article history:}

Received 18 October 2012
Received in revised form 21 December 2012
Accepted 27 December 2012
Available online 10 January 2013

\section*{Keywords:}

PC-SAFT EOS
MDEA
$\mathrm{CO}_{2}$ capture
Smith-Missen algorithm

\begin{abstract}
$\mathrm{CO}_{2}$ capture by aqueous alkanolamines treating is one of the prevalent methods to reduce carbon dioxide emissions and to help environmental problems. For realizing more the thermodynamics of the $\mathrm{CO}_{2}-$ MDEA- $\mathrm{H}_{2} \mathrm{O}$, the PC-SAFT equation of state was used to simulate the absorption of carbon dioxide by MDEA (methyldiethanolamine). A correlation for temperature-dependent binary interaction parameter were calculated by excess enthalpy data for aqueous MDEA at low temperatures (lower than 350 K ), and then this binary interaction parameter used to predict phase equilibria of ternary aqueous mixtures of MDEA with carbon dioxide. Smith-Missen algorithm and PC-SAFT EOS have been used to determine concentration of species in chemical equilibrium and physical equilibrium, respectively. In addition, for determining parameter sets of MDEA, vapor pressure and saturated liquid density data were used and different and probable association schemes were considered in parameter estimations. Results show 4(2:2,0:0) association scheme for MDEA and 4(2:2) association scheme for water have better agreement with binary and ternary VLE experimental data.
\end{abstract}
© 2013 Elsevier Ltd. All rights reserved.

\section*{1. Introduction}

Precise and predictive thermodynamics models are significant in many industries including the oil and gas industries. PC-SAFT Equation of State provides a practical and rigorous thermodynamic framework to model thermodynamic properties of many systems. The PC-SAFT EOS was developed by Gross and Sadowski is one of the most important SAFT various versions, indeed. Gross and Sadowski applied this EOS for associating systems, and a large number of papers about application of PC-SAFT in associating systems have been published, but many issues still remain unsolved about PC-SAFT. These issues are both theoretical and practical. An important practical problem is how to obtain optimal and consistent parameter sets for alkanolamines due to their different functional groups. However, multifunctional associating molecules indicate different challenges. Different association schemes result to different parameter sets with give similar pure component vapor pressure and liquid density results due to fitting by same data, whereas very different mixture results such as heat of mixing and binary VLE are obtained. The performance of the theory therefore depends seriously on the selection of association scheme due its effect on parameter estimation [1].

Some thermodynamics models have been applied for regression and prediction $\mathrm{CO}_{2}$ solubility in aqueous MDEA solution and other aqueous alkanolamines such as electrolyte NRTL by Zhang and

\footnotetext{
* Corresponding author. Tel.: +98 21 82883969; fax: +98 2182883381.

E-mail address: pahlavzh@modares.ac.ir (H. Pahlavanzadeh).
}

Chen [2], Austgen et al. [3] and Posey and Rochelle [4], extended UNIQUAC by Faramarzi et al. [5] and Pitzer by Kuranov et al. [6], Kamps et al. [7] and Arcis et al. [8]. Common features shared by most of the models that were used to model ( $\mathrm{CO}_{2}+$ alkanolamine + water) systems include complex and a large number of adjustable binary interaction parameters which must be fitted to experimental data. Unlike the models which apply the equations of states especially association EOSs do not require these amount of experimental data except for modifying the interaction energies, however these modifications do not need a lot of experimental data. Recently some association models were used to describe ( $\mathrm{CO}_{2}+$ alkanolamine + water $)$ systems such as CPA by Zoghi et al. [9], SAFT-VR by Rodriguez et al. [10] and PC-SAFT by Nasrifar and Tafazzol [11]. PC-SAFT EOS was used by Nasrifar and Tafazzol to model the solubility of acid gases in aqueous solutions of MEA, DEA, and MDEA, but their model shows high errors for ( $\mathrm{CO}_{2}+-$ MDEA + water) system [11].

In this work, the PC-SAFT EOS was implemented for $\mathrm{CO}_{2}$ physical absorption by MDEA, in addition chemical reactions in ( $\mathrm{CO}_{2}+-$ alkanolamine + water) is very important and not considering chemical equilibrium results high errors, therefore Smith-Missen algorithm was used to calculate $\mathrm{CO}_{2}$ chemical absorption.

\section*{2. PC-SAFT EOS}

PC-SAFT EOS was introduced in terms of free energy of Helmholtz by Gross and Sadowski [12] and [13],

\begin{tabular}{|l|l|l|l|}
\hline \multicolumn{4}{|l|}{Nomenclature} \\
\hline $a_{i}$ & activity of species $i$ & \multicolumn{2}{|l|}{Greek symbols} \\
\hline $\tilde{a}^{\text {res }}$ & residual Helmholtz energy & $\alpha$ & $\mathrm{CO}_{2}$ liquid loading (mole $\mathrm{CO}_{2} /$ mole MDEA) \\
\hline $\tilde{a}^{h c}$ & hard-chain Helmholtz energy & $\varepsilon$ & segment dispersion interaction energy \\
\hline $\tilde{a}^{\text {disp }}$ & dispersion interactions Helmholtz energy & $\varepsilon^{A_{i} B_{j}}$ & energy of hydrogen bounding between site $A$ at mole- \\
\hline $\tilde{a}^{a s s o c}$ & association interactions Helmholtz energy & & cule $i$ and site $B$ at molecule $j$ \\
\hline $d$ & average segment diameter & $k^{A_{i} B_{j}}$ & volume of hydrogen bounding between site $A$ at mole- \\
\hline $g_{i j}^{h s}$ & radial pair distribution function for segments of component $i$ in the hard sphere system & $\rho$ & cule $i$ and site $B$ at molecule $j$ \\
\hline $h$ & enthalpy & $\rho_{n}$ & molecular density \\
\hline $k_{B}$ & Boltzmann constant $\left(1.38066 \cdot 10^{-23} \mathrm{~J} \cdot \mathrm{~K}^{-1}\right)$ & $\sigma$ & pure temperature independent segment diameter \\
\hline $K_{x}$ & the chemical equilibrium constants in mole fraction basis & $\Delta^{A_{i} B_{j}}$ & strength of hydrogen bounding between the site $A$ at \\
\hline $m$ & pure number of segments in a molecule & & \\
\hline M & total moles of MDEA & \multicolumn{2}{|l|}{Subscripts and superscripts} \\
\hline $n p$ & number of experimental data points & exp & experimental \\
\hline $x$ & mole fraction & cal & calculated \\
\hline $X^{A_{i}}$ & fraction of molecules of species $i$ that are not bound at site $A$ & E & excess \\
\hline & & L & liquid \\
\hline $p$ & pressure (Pa) & min & minimum \\
\hline T & temperature (K) & max & maximum \\
\hline W & total moles of water in liquid phase & $i, j, k$ sat & indices saturation \\
\hline
\end{tabular}

$$
\begin{equation*}
\tilde{a}^{r e s}=\tilde{a}^{h c}+\tilde{a}^{d i s p}+\tilde{a}^{a s s o c}, \tag{1}
\end{equation*}
$$

where $\tilde{a}^{\text {res }}, \tilde{a}^{h c}, \tilde{a}^{\text {disp }}$, and $\tilde{a}^{\text {assoc }}$ represent the residual Helmholtz energy, the contribution of the hard-chain reference fluid consists of spherical segments Helmholtz energy, the contribution of dispersive attractions to the Helmholtz energy and the contribution due to short-range association interactions (hydrogen bonding) Helmholtz energy, respectively. The contribution of the hard-chain reference fluid Helmholtz energy and the contribution of dispersive attractions to the Helmholtz energy were presented by Gross and Sadowski [12]. The contribution of the association Helmholtz energy is given by following expression [12]:

$$
\begin{equation*}
\tilde{a}^{a s s o c}=\sum_{i} x_{i} \sum_{A_{i}}\left[\ln X^{A_{i}}-\frac{1}{2} X^{A_{i}}+\frac{1}{2}\right], \tag{2}
\end{equation*}
$$

where $x_{i}$ is mole fraction of molecule $i$, and the $X^{A_{i}}$ is fraction of molecules of species $i$ that are not bound at site $A . X^{A_{i}}$ by following equation is expressed:

$$
\begin{equation*}
X^{A_{i}}=\left(1+\rho_{n} \sum_{j} x_{j} \sum_{B_{j}} X^{B_{j}} \Delta^{A_{i} B_{j}}\right)^{-1}, \tag{3}
\end{equation*}
$$

where $\rho_{n}$ is molecular density and $\Delta^{A_{i} B_{j}}$ is strength of hydrogen bounding between the site $A$ at molecule $i$ and the site $B$ at molecule $j$.

Hydrogen bond strength is expressed by following equation:

$$
\begin{equation*}
\Delta^{A_{i} B_{j}}=d_{i j}^{3} g_{i j}^{h s}\left(d_{i j}\right) \kappa^{A_{i} B_{j}}\left[\exp \left(\frac{\varepsilon^{A_{i} B_{j}}}{k_{B} T}\right)-1\right], \tag{4}
\end{equation*}
$$

where $\varepsilon^{A_{i} B_{j}}$ and $\kappa^{A_{i} B_{j}}$ are energy and volume of hydrogen bounding between site $A$ at molecule $i$ and site $B$ at molecule $j$, respectively. $d_{i j}=\left(d_{i}+d_{j}\right) / 2$ is average temperature dependent segment diameter, $g_{i j}^{h s}$ is radial pair distribution function for segments of component $i$ in the hard sphere system which has been presented in reference [12], $k_{B}$ is Boltzmann constant and $T$ represents temperature in Kelvin.

Temperature dependent segment diameter, $d_{i}$, is given by following expression [12]:

$$
\begin{equation*}
d_{i}=\sigma_{i}\left(1-0.12 \exp \left(\frac{-3 \varepsilon_{i}}{k_{B} T}\right)\right), \tag{5}
\end{equation*}
$$

where $\sigma_{i}$ and $\varepsilon_{i}$ are pure temperature independent segment diameter and segment dispersion interaction energy of molecule $i$.

Gross and Sadowski used equations (6) and (7) mixing rules for associating multi-component systems [13]:

$$
\begin{equation*}
\kappa^{A_{i} B_{j}}=\sqrt{\kappa^{A_{i} B_{i}} \kappa^{A_{j} B_{j}}}\left(\frac{\sqrt{\sigma_{i} \sigma_{j}}}{\frac{1}{2}\left(\sigma_{i}+\sigma_{j}\right)}\right)^{3}, \tag{6}
\end{equation*}
$$


$$
\begin{equation*}
\varepsilon^{A_{i} B_{j}}=\frac{\varepsilon^{A_{i} B_{i}}+\varepsilon^{A_{j} B_{j}}}{2} . \tag{7}
\end{equation*}
$$


In this study, an association nomenclature is used which was introduced by Yarrison and Chapman: $x(y: z)$, where $y$ is the number of proton acceptor sites, $z$ is the number of proton donor sites and $x$ is the total number of sites [14]. Also, this nomenclature was used by Avlund for some alkanolamines with different association strength for each functional group [15].

\section*{3. Modeling results}

\subsection*{3.1. Pure parameters calculation}

Different association schemes can be considered for MDEA due to its various functional groups. Alkanolamines include hydroxyl groups and amine group, so sometimes select an exact association scheme is complicated.

MDEA is a tertiary amine; consists of two hydroxyl groups and a tertiary amine group. It can be assumed, the participation of tertiary amine group in association can be ignored respect to hydroxyl group. Therefore, by this assumption, two association scheme were proposed for MDEA: 4(2:2,0:0) and 6(4:2,0:0).

For calculating parameter sets for MDEA, following objective function was applied:

$$
\begin{equation*}
O F=\sum_{i}^{n p} \frac{\left|p_{i}^{\text {sat,exp }}-p_{i}^{\text {sat,cal }}\right|}{p_{i}^{\text {sat,exp }}}+\sum_{i}^{n p} \frac{\left|\rho_{i}^{\text {sat,exp }}-\rho_{i}^{\text {sat,cal }}\right|}{\rho_{i}^{\text {sat,exp }}}, \tag{8}
\end{equation*}
$$


\begin{table}
\captionsetup{labelformat=empty}
\caption{TABLE 1
Correlations constants for the vapor pressure ( $p^{\text {sat }}$ ) and saturated liquid density ( $\rho^{L, \text { sat }}$ ) of MDEA in equations (9) and (10) (from reference [16]).}
\begin{tabular}{|l|l|l|}
\hline & $p^{\text {sat }}(\mathrm{Pa})$ & $\rho^{\text {L,sat }}(\mathrm{mol} / \mathrm{L})$ \\
\hline A & 92.624 & 1.0011 \\
\hline B & -10367 & 0.22523 \\
\hline C & -9.4699 & 678.2 \\
\hline D & $1.9 \times 10^{-18}$ & 0.21515 \\
\hline E & 6 & \\
\hline $\mathrm{T}_{\text {min }}(\mathrm{K})$ & 283.65 & \\
\hline $\mathrm{T}_{\text {max }}(\mathrm{K})$ & 678.2 & \\
\hline maximum deviation & 8.1\% & 0.3\% \\
\hline average deviation & 2.1\% & 0.1\% \\
\hline
\end{tabular}
\end{table}
where $p^{\text {sat }}$ and $\rho^{\text {sat }}$ indicate saturated vapor pressure and saturated liquid density of pure species, respectively. Experimental saturated vapor pressures and saturated liquid densities obtained from DIPPR correlations that Avlund used for determining MDEA parameters set for CPA EOS [16]. Also, Avlund indicated these correlations have good agreement with experimental data [16]. The correlations were expressed by equations (9) and (10) for the vapor pressure ( $p^{\text {sat }}$ ) and saturated liquid density ( $\rho^{L, \text { sat }}$ ) of MDEA, respectively.

$$
\begin{equation*}
p^{\text {sat }}(\mathrm{Pa})=\exp \left(A+\frac{B}{(T / \mathrm{K})}+C \ln (T / \mathrm{K})+D(T / \mathrm{K})^{E}\right), \tag{9}
\end{equation*}
$$


$$
\begin{equation*}
\rho^{L, s a t}\left(\frac{\mathrm{~mol}}{\mathrm{~L}}\right)=A /\left(B^{\left[1+(1-(T / \mathrm{K}) / C]^{D}\right.}\right), \tag{10}
\end{equation*}
$$

where the correlations constants were presented in table 1.
Pure parameter sets for MDEA with 4(2:2,0:0) and 6(4:2, 0:0) association schemes in temperature range $30-170^{\circ} \mathrm{C}$ were determined and the results were presented in table 2 , and the diagram of pressure-density of saturated pure MDEA is presented in figure 1. In addition, 2(1:1) scheme for MDEA which reported by Zhang and Chen [2] were plotted in figure 1. One can see from figures 1 and $2(1: 1)$ scheme for MDEA was resulted relatively high errors.

\subsection*{3.2. Binary systems}

A number of association schemes and parameter sets were reported in literature for water and carbon dioxide. In this work, two parameter sets for $\mathrm{H}_{2} \mathrm{O}$ and one parameter set for $\mathrm{CO}_{2}$ were compared to choose the best parameter sets. These parameters have been presented in table 2. Binary VLE of ( $\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}$ ) and (MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) systems were calculated by two association schemes of $\mathrm{H}_{2} \mathrm{O}$ which were reported by Diamantonis and Economou [17].

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-3.jpg?height=770&width=839&top_left_y=232&top_left_x=1067}
\captionsetup{labelformat=empty}
\caption{FIGURE 1. Saturated vapor pressure versus saturated liquid density for pure MDEA at temperature from $30^{\circ} \mathrm{C}$ to $170^{\circ} \mathrm{C}$. Comparison of $4(2: 2,0: 0), 6(4: 2,0: 0)$ association schemes and 2(1:1) scheme of Zhang and Chen [2] to correlation curve.}
\end{figure}

\subsection*{3.2.1. ( $\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}$ ) system}

Both 4(2:2) and 2(1:1) association schemes for water were applied for calculating VLE ( $\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}$ ) mixture and the results were presented in table 3. In this study, experimental data from Dalmolin et al. [18], Valtz et al. [19] and Chapoy et al. [20] for $\left(\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}\right)$ system were used.

The results of the table 3 and figure 3 show, 4(2:2) association scheme for water includes better results respect to $2(1: 1)$ association scheme in binary VLE of ( $\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}$ ) system. Also the graphical form of the solubility of $\mathrm{CO}_{2}$ in water is presented in figure 2.

\subsection*{3.2.2. (MDEA + $\mathrm{H}_{2} \mathrm{O}$ ) system}

Binary VLE between MDEA and $\mathrm{H}_{2} \mathrm{O}$ was shown in figure 4 with different association schemes for MDEA and water, and the results were compared to experimental data from Voutsas et al. [21]. It was seen from figure $4,4(2: 2,0: 0)$ association scheme shows better result respect to 6(4:2,0:0) association scheme for MDEA. In order to use 4(2:2,0:0) association scheme for MDEA in ternary system, this scheme for MDEA with 4(2:2) association scheme for water (due to its acceptable result for $\left(\mathrm{H}_{2} \mathrm{O}+\mathrm{CO}_{2}\right)$ system) were used to find binary interaction parameter in (MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system at low temperatures (lower than 350 K ). These association schemes have good agreement with experimental binary VLE at high tempera-

\begin{table}
\captionsetup{labelformat=empty}
\caption{TABLE 2
Pure-component parameters used in this work.}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Species} & \multirow[t]{2}{*}{Association scheme} & \multirow[t]{2}{*}{$m$} & \multirow[t]{2}{*}{$\sigma$} & \multirow[t]{2}{*}{$\varepsilon / k_{B}$} & \multirow[t]{2}{*}{$\kappa^{A B}$} & \multirow[t]{2}{*}{$\varepsilon^{A B} / k_{B}$} & \multicolumn{2}{|l|}{\%AAD ${ }^{a}$} & \multirow[t]{2}{*}{Reference} \\
\hline & & & & & & & $p^{\text {sat }}$ & $\rho^{L, \text { sat }}$ & \\
\hline \multirow[t]{3}{*}{MDEA} & 6(4:2,0:0) & 4.874 & 3.211 & 288.87 & 0.016894 & 513.2765 & 1.46 & 0.24 & This work \\
\hline & 4(2:2,0:0) & 3.675 & 3.563 & 228.711 & 0.123858 & 2046.624 & 0.51 & 0.41 & This work \\
\hline & 2(1:1) & 3.3044 & 3.5975 & 237.44 & 0.066454 & 3709.9 & 13.1 & 2.7 & [2] \\
\hline \multirow[t]{2}{*}{$\mathrm{H}_{2} \mathrm{O}$} & 2(1:1) & 1.9599 & 2.362 & 279.42 & 0.1750 & 2059.28 & 1.18 & 3.92 & [17] \\
\hline & 4(2:2) & 2.1945 & 2.229 & 141.66 & 0.2039 & 1804.17 & 1.98 & 0.83 & [17] \\
\hline $\mathrm{CO}_{2}$ & Non-associating & 2.0729 & 2.7852 & 169.21 & & & 2.78 & 2.73 & [12] \\
\hline $\mathrm{CH}_{4}$ & Non-associating & 1 & 3.7039 & 150.03 & & & 0.36 & 0.67 & [12] \\
\hline
\end{tabular}
\end{table}

\footnotetext{
${ }^{a} \% A A D=100 / n p * \Sigma\left|\psi^{\text {exp }}-\psi^{\text {cal }}\right| / \psi^{\text {exp }}, \psi$ is $p^{\text {sat }}$ and $\rho^{\text {L,sat }}$.
}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-4.jpg?height=808&width=839&top_left_y=228&top_left_x=163}
\captionsetup{labelformat=empty}
\caption{FIGURE 2. Isotherm pressure-composition $P-x$ slices of the (vapor + liquid) equilibrium of $\left(\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}\right)$. The symbols correspond to the experimental data from [18] and the solid curves represent the PC-SAFT predictions ( $k_{i j}=0$ ).}
\end{figure}
tures (more than 350 K ), but it does not show good agreement at low temperatures in comparison to experimental excess enthalpy data from Maham et al. [22] and Posey [23]. Therefore a binary interaction parameter between $\mathrm{H}_{2} \mathrm{O}$ and MDEA was fitted to experimental data of enthalpy of mixing at low temperatures with 4(2:2,0:0) association scheme for MDEA and 4(2:2) association scheme for water. For determining this binary interaction parameter between MDEA and $\mathrm{H}_{2} \mathrm{O}$, enthalpy of mixing data and binary VLE were used, these data were fitted to a three terms Gaussian function, so that it incline to a constant value (zero) at high temperatures for satisfying both VLE and excess enthalpy in wide range of temperature (298 to 500 K ).
$k_{\text {MDEA }-\mathrm{H}_{2} \mathrm{O}}=\sum_{i=1}^{3} a_{i} \exp \left(-\left(\frac{T / \mathrm{K}-b_{i}}{c_{i}}\right)^{2}\right)$,
where $a_{i}, b_{i}$, and $c_{i}$ are the constants of equation (11) which were presented in table 4.

The results of effect of applying $k_{i j}$ for calculating excess enthalpy were shown in figure 5.

\subsection*{3.2.3. (MDEA + hydrocarbon) system}

The solubility of methane in the MDEA is shown in figure 6, and the results of model prediction and experimental data from [24] were compared. The parameter set of $4(2: 2,0: 0)$ scheme of MDEA was applied in modeling of this system. The PC-SAFT EOS does not

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-4.jpg?height=806&width=843&top_left_y=230&top_left_x=1095}
\captionsetup{labelformat=empty}
\caption{FIGURE 3. Parity plot for the $\left(\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}\right)$ system total pressure, experiment versus PC-SAFT predictions ( $k_{i j}=0$ ) with 4(2:2) association scheme for water. Experimental data: $(\bullet)$ Dalmolin et al. [18], (■) Valtz et al. [19], and ( $\mathbf{\Lambda}$ ) Chapoy et al. [20].}
\end{figure}
perform this binary system positively acceptable; so a binary interaction parameter was correlated for improving the model results.

\subsection*{3.3. Ternary system ( $\mathrm{CO}_{2}+\mathrm{MDEA}+\mathrm{H}_{2} \mathrm{O}$ )}

In this work, no correlation has been applied for VLE prediction of ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system by PC-SAFT EOS. It means the binary interaction parameters between ( $\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}$ ) and ( $\mathrm{CO}_{2}+$ MDEA) set to zero, and the binary interaction parameter between (MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) sets by equation (11).

This ternary system involves both chemical equilibrium and multi-component phase equilibrium. The liquid phase consists of both molecular species and ionic species. The chemical reactions taking place in the liquid phase for ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system can be expressed as:
$2 \mathrm{H}_{2} \mathrm{O} \leftrightarrow \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{OH}^{-}$,
$\mathrm{CO}_{2}+2 \mathrm{H}_{2} \mathrm{O} \leftrightarrow \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{HCO}_{3}^{-}$,
$\mathrm{HCO}_{3}^{-}+\mathrm{H}_{2} \mathrm{O} \leftrightarrow \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{CO}_{3}^{2-}$,
$\mathrm{MDEAH}^{+}+\mathrm{H}_{2} \mathrm{O} \leftrightarrow \mathrm{H}_{3} \mathrm{O}^{+}+$MDEA.

Charge balance is expressed as:
$\left[\mathrm{H}_{3} \mathrm{O}^{+}\right]+\left[\mathrm{MDEAH}^{+}\right]-\left[\mathrm{HCO}_{3}^{-}\right]-2\left[\mathrm{CO}_{3}^{2-}\right]-\left[\mathrm{OH}^{-}\right]=0$.

\begin{table}
\captionsetup{labelformat=empty}
\caption{TABLE 3
Comparison between experimental data and model predictions ( $k_{i j}=0$ ) for ( $\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O}$ ) equilibrium.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline \multirow[t]{3}{*}{Source} & \multirow[t]{3}{*}{Data points} & \multirow[t]{3}{*}{Temperature, $T / \mathrm{K}$} & \multirow[t]{3}{*}{Total pressure, $P / \mathrm{MPa}$} & \multirow[t]{3}{*}{$\mathrm{CO}_{2}$ mole fraction in water} & \multicolumn{2}{|c|}{\multirow{2}{*}{$\Sigma|\Delta P| / P \% \mathrm{H}_{2} \mathrm{O}$ association scheme}} \\
\hline & & & & & & \\
\hline & & & & & 4(2:2) & 2(1:1) \\
\hline Dalmolin et al. [18] & 49 & 288 to 323 & 0.092 to 0.48 & 0.00038 to 0.00365 & 8.35 & 98.7 \\
\hline Valtz et al. [19] & 47 & 278 to 318 & 0.465 to 7.96 & 0.0018 to 0.028 & 19.80 & 103 \\
\hline Chapoy et al. [20] & 27 & 274 to 351 & 0.19 to 9.33 & 0.00262 to 0.025 & 19.19 & 121 \\
\hline Total & 123 & & & & 15.10 & 105 \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-5.jpg?height=1639&width=1743&top_left_y=217&top_left_x=146}
\captionsetup{labelformat=empty}
\caption{FIGURE 4. Isobaric temperature-composition $T-x$ slices of the (vapor + liquid) equilibrium of (MDEA $+\mathrm{H}_{2} \mathrm{O}$ ). The symbols correspond to the experimental data at $p=40 \mathrm{kPa}$, $p=53.3 \mathrm{kPa}$, and $p=66.7 \mathrm{kPa}$ [21] and the solid curves represent to the PC-SAFT predictions $\left(k_{i j}=0\right)$ : (a) $4(2: 2,0: 0)$ scheme for MDEA and $2(1: 1)$ scheme for water, (b) $4(2: 2$, 0:0) scheme for MDEA and 4(2:2) scheme for water, (c) $6(4: 2,0: 0)$ scheme for MDEA and $2(1: 1)$ scheme for water and (d) $6(4: 2,0: 0)$ scheme for MDEA and $4(2: 2)$ scheme for water.}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{TABLE 4
The constants of equation (11).}
\begin{tabular}{llcc}
\hline & 1 & 2 & 3 \\
\hline$a$ & -80.57 & 80.71 & 0.05445 \\
$b$ & 298.8 & 298.8 & 337.2 \\
$c$ & 23.84 & 23.87 & 10.03 \\
\hline
\end{tabular}
\end{table}

Three mass balances can be expressed as, too:

$$
\begin{equation*}
M=[\mathrm{MDEA}]+\left[\mathrm{MDEAH}^{+}\right], \tag{13}
\end{equation*}
$$


$$
\begin{equation*}
\alpha M=\left[\mathrm{CO}_{2}\right]-\left[\mathrm{HCO}_{3}^{-}\right]+\left[\mathrm{CO}_{3}^{2-}\right], \tag{14}
\end{equation*}
$$


$$
\begin{equation*}
W=\left[\mathrm{H}_{2} \mathrm{O}\right]+\left[\mathrm{HCO}_{3}^{-}\right]+\left[\mathrm{CO}_{3}^{2-}\right]+\left[\mathrm{H}_{3} \mathrm{O}^{+}\right]+\left[\mathrm{OH}^{-}\right] \tag{15}
\end{equation*}
$$

where $\alpha, M$, and $W$ are loading of $\mathrm{CO}_{2}$ in aqueous MDEA, total of MDEA, and amount of $\mathrm{H}_{2} \mathrm{O}$ in liquid phase, respectively.

Equations (12)-(15) were solved by Smith-Missen algorithm [25], which were assumed their activity equal to their mole fraction $\left(a_{i}=x_{i}\right)$ for all species. Also the ion pair effects were neglected in equilibrium. For checking this assumption results with experimental data, concentration of some molecular and ionic species were compared with experimental data from Jakobsen et al. [26], and the results were shown in figure 7.

The chemical equilibrium constants for reactions (I to IV) were calculated by equation (16).

$$
\begin{equation*}
\ln K_{x}=A+\frac{B}{(T / K)}+C \ln (T / K), \tag{16}
\end{equation*}
$$

where the constant of equation (16) were presented in table 5.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-6.jpg?height=796&width=849&top_left_y=232&top_left_x=159}
\captionsetup{labelformat=empty}
\caption{FIGURE 5. Comparison of the experimental data from Posey [23] and Maham et al. [22] for excess enthalpy of the (MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) binary solution and the model results. Dash lines and solid lines represent model predictions ( $k_{i j}=0$ ) and model correlation ( $k_{i j}$ was given by equation (11)), respectively.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-6.jpg?height=809&width=843&top_left_y=1263&top_left_x=163}
\captionsetup{labelformat=empty}
\caption{FIGURE 6. Solubility of methane in the MDEA. The symbols represent the experimental data from [24]. Dotted and solid curves represent the model prediction ( $k_{i j}=0$ ) and model correlation ( $k_{i j}=0.1063$ ), respectively.}
\end{figure}

A comparison of model predictions and experimental VLE data from some sources were exhibited in table 6. The results exhibited the capability and the strength of PC-SAFT EOS for predicting the VLE of ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system. The model predictions were acceptable, with the average relative deviation on partial pressure of $\mathrm{CO}_{2}$ (or total pressure) in the range of $19 \%$ to $31 \%$.

Figure 8 shows total pressure data of Kuranov et al. [6] were predicted excellently, and figure 9 shows the prediction of the total pressure data of Kamps et al. [7]. figure 10 shows the acceptable

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-6.jpg?height=809&width=855&top_left_y=234&top_left_x=1090}
\captionsetup{labelformat=empty}
\caption{FIGURE 7. Comparison of the experimental data for species concentration in $\left(\mathrm{CO}_{2}+\mathrm{MDEA}+\mathrm{H}_{2} \mathrm{O}\right)$ and the ideal Smith-Missen algorithm results at $T=20^{\circ} \mathrm{C}$. MDEA concentration is $23 \mathrm{wt} . \%$. Symbols represent experimental data from Jakobsen et al. [26].}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{TABLE 5
Equilibrium constants correlations used for modeling in equation (16).}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline No. reaction & Equilibrium constant & A & B & $C$ & Temperature range ${ }^{\circ} \mathrm{C}$ & Ref. \\
\hline (I) & $\frac{a_{\mathrm{H}_{3} \mathrm{O}^{+}} a_{\mathrm{OH}^{-}}}{a_{\mathrm{H}_{2} \mathrm{O}}^{2}}$ & 132.899 & -13445.9 & 22.4773 & 0 to 225 & [29] \\
\hline (II) & $\frac{a_{\mathrm{H}_{3} \mathrm{O}^{+}} a_{\mathrm{HCO}_{3}^{-}}}{a_{\mathrm{H}_{2} \mathrm{O}}^{2} a_{\mathrm{CO}_{2}}}$ & 231.465 & -12092.10 & -36.7816 & 0 to 225 & [29] \\
\hline (III) & $\frac{a_{\mathrm{H}_{3} \mathrm{O}^{+}} a_{\mathrm{CO}_{3}^{-2}}}{a_{\mathrm{H}_{2} \mathrm{O}} a_{\mathrm{HCO}_{3}^{-}}}$ & 216.049 & -12431.70 & -35.4819 & 0 to 225 & [29] \\
\hline (IV) & $\frac{a_{\mathrm{H}_{3} \mathrm{o}^{+}} a_{\text {MDEA }}}{a_{\mathrm{H}_{2} \mathrm{O}} a_{\text {MDEAH }}+}$ & -83.4914 & -819.7 & 10.9756 & 0 to 95 & [30] \\
\hline
\end{tabular}
\end{table}
prediction results for the $\mathrm{CO}_{2}$ partial pressure data in $50 \mathrm{wt} . \%$ MDEA concentration, $\mathrm{CO}_{2}$ loading from 0.165 to 0.813 , temperature from $55^{\circ} \mathrm{C}$ to $85^{\circ} \mathrm{C}$, and partial pressure from 65 kPa to 813 kPa of Ma'mun et al. [27], and figure 11 shows the acceptable prediction results for the $\mathrm{CO}_{2}$ partial pressure data in $23 \mathrm{wt} . \%$ MDEA concentration, $\mathrm{CO}_{2}$ loading from 0.017 to 0.262 , at temperature $24^{\circ} \mathrm{C}$, and partial pressure from 0.024 kPa to 1.6 kPa of Lemoine et al. [28].

\section*{4. Conclusion}

4(2:2,0:0) association scheme for MDEA shows more conformity with binary VLE experimental data more than $6(4: 2,0: 0)$ association scheme. 4(2:2) association scheme for water shows better agreement with $\mathrm{CO}_{2}$ respect to $2(1: 1)$ scheme. Therefore 4(2:2,0:0) association scheme for MDEA and 4(2:2) association scheme for water were applied. A correlation for binary interaction between MDEA and $\mathrm{H}_{2} \mathrm{O}$ was fitted to calculate excess enthalpy of MDEA and water system, also this correlation was used to VLE calculation ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system and it resulted to acceptable prediction of this system.

\begin{table}
\captionsetup{labelformat=empty}
\caption{TABLE 6
Comparison between experimental data and model predictions for total pressure or $\mathrm{CO}_{2}$ partial pressure of the ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline Source & Data points & Temperature, $T / \mathrm{K}$ & Pressure, $P / \mathrm{kPa}$ & MDEA mole fraction & $\mathrm{CO}_{2}$ loading & $\Sigma|\Delta P| / P \%$ \\
\hline Kuranov et al. [6] & 82 & 313 to 413 & 70 to 5000 & 0.035 to 0.067 & 0 to 1.32 & 26.42 \\
\hline Kamps et al. [7] & 23 & 313 to 393 & 200 to 6000 & 0.126 & 0.13 to 1.15 & 28.44 \\
\hline Ma'mun et al. [27] & 34 & 328 to 358 & 66 to 813 & 0.13 & 0.165 to 0.813 & 19.83 \\
\hline Lemoine et al. [28] & 13 & 298 & 0.0171 to 0.2625 & 0.04 & 0.02 to 1.64 & 31.65 \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-7.jpg?height=809&width=854&top_left_y=589&top_left_x=124}
\captionsetup{labelformat=empty}
\caption{FIGURE 8. Experimental data from Kuranov et al. [6] in $m_{\text {MDEA }}=4 \mathrm{~mol} / \mathrm{kg}$ and temperatures 393 and 413 K (symbols) and total pressures prediction (solid lines) of ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system. In multicomponent predictions $k_{\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}}$ and $k_{\mathrm{CO}_{2}-\mathrm{MDEA}}$ set to zero and $k_{\text {MDEA }}-\mathrm{H}_{2} \mathrm{O}$ sets by equation (11).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-7.jpg?height=832&width=845&top_left_y=1677&top_left_x=127}
\captionsetup{labelformat=empty}
\caption{FIGURE 9. Experimental data from Kamps et al. [7] (symbols) and total pressures prediction (solid lines) of the ( $\mathrm{CO}_{2}+$ MDEA $+\mathrm{H}_{2} \mathrm{O}$ ) system. In multicomponent predictions $k_{\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}}$ and $k_{\mathrm{CO}_{2}-\text { MDEA }}$ set to zero and $k_{\text {MDEA }}-\mathrm{H}_{2} \mathrm{O}$ sets by equation (11).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-7.jpg?height=821&width=865&top_left_y=581&top_left_x=1052}
\captionsetup{labelformat=empty}
\caption{FIGURE 10. Comparison of the experimental data [6] for $\mathrm{CO}_{2}$ partial pressure of the $\left(\mathrm{CO}_{2}+\mathrm{MDEA}+\mathrm{H}_{2} \mathrm{O}\right)$ system and the model results; the MDEA concentration is $50 \mathrm{wt} . \%$. In multicomponent predictions $k_{\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}}$ and $k_{\mathrm{CO}_{2} \text {-MDEA }}$ set to zero and $k_{\text {MDEA }}-\mathrm{H}_{2} \mathrm{O}$ sets by equation (11).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/eae2b1b2-6e00-4e74-8d1d-bdbeb641f479-7.jpg?height=805&width=853&top_left_y=1672&top_left_x=1057}
\captionsetup{labelformat=empty}
\caption{FIGURE 11. Comparison of the experimental data [28] for $\mathrm{CO}_{2}$ partial pressure of the $\left(\mathrm{CO}_{2}+\right.$ MDEA $\left.+\mathrm{H}_{2} \mathrm{O}\right)$ system and the model results; the MDEA concentration is $23.63 \mathrm{wt} . \%$. In multicomponent predictions $k_{\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}}$ and $k_{\mathrm{CO}_{2} \text {-MDEA }}$ set to zero and $k_{\text {MDEA }}-\mathrm{H}_{2} \mathrm{O}$ sets by equation (11).}
\end{figure}

\section*{Acknowledgments}

This work was supported by the NIGC (National Iranian Gas Company) through M.Sc. fellowship. Authors are thankful to Saeed Hadi for providing binary VLE data set of $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$.

\section*{References}
[1] M. Kleiner, F. Tumakaka, G. Sadowski, Struct. Bond. 131 (2009) 75-104.
[2] Y. Zhang, C.C. Chen, Ind. Eng. Chem. Res. 50 (2011) 163-175.
[3] D.M. Austgen, G.T. Rochelle, C.C. Chen, Ind. Eng. Chem. Res. 30 (1991) 543-555.
[4] M.L. Posey, G.T. Rochelle, Ind. Eng. Chem. Res. 36 (1997) 3944-3953.
[5] L. Faramarzi, G.M. Kontogeorgis, K. Thomsen, E.H. Stenby, Fluid Phase Equilib. 282 (2009) 121-132.
[6] G. Kuranov, B. Rumpf, N.A. Smirnova, G. Maurer, Ind. Eng. Chem. Res. 35 (1996) 1959-1966.
[7] A.P. Kamps, A. Balaban, M. Jodecke, G. Kuranov, N.A. Smirnova, G. Maurer, Ind. Eng. Chem. Res. 40 (2001) 696-706.
[8] H. Arcis, L. Rodier, K. Ballerat-Busserolles, J.Y. Coxam, J. Chem. Thermodyn. 41 (2009) 783-789.
[9] A.T. Zoghi, F. Feyzi, M.R. Dehghani, Ind. Eng. Chem. Res. 51 (2012) 9875-9885.
[10] J. Rodriguez, N. Mac Dowell, F. Llovell, C.S. Adjiman, G. Jackson, A. Galindo, Mol. Phys. 110 (2012) 1325-1348.
[11] K. Nasrifar, A.H. Tafazzol, Ind. Eng. Chem. Res. 49 (2010) 7620-7630.
[12] J. Gross, G. Sadowski, Ind. Eng. Chem. Res. 40 (2001) 1244-1260.
[13] J. Gross, G. Sadowski, Ind. Eng. Chem. Res. 41 (2002) 5510-5515.
[14] M. Yarrison, W.G. Chapman, Fluid Phase Equilib. 226 (2004) 195-205.
[15] A.S. Avlund, D.K. Eriksen, G.M. Kontogeorgis, M.L. Michelsen, Fluid Phase Equilib. 306 (2011) 31-37.
[16] A.S. Avlund, G.M. Kontogeorgis, M.L. Michelsen, Ind. Eng. Chem. Res. 47 (2008) 7441-7446.
[17] N.I. Diamantonis, I.G. Economou, Energy Fuels 25 (2011) 3334-3343.
[18] I. Dalmolin, E. Skovroinski, A. Biasi, M.L. Corazza, C. Dariva, J.V. Oliveira, Fluid Phase Equilib. 245 (2006) 193-200.
[19] A. Valtz, A. Chapoy, C. Coquelet, P. Paricaud, D. Richon, Fluid Phase Equilib. 26 (2004) 333-344.
[20] A. Chapoy, A.H. Mohammadi, A. Chareton, B. Tohidi, D. Richon, Ind. Eng. Chem. Res. 43 (2004) 1794-1802.
[21] E. Voutsas, A. Vrachnos, K. Magoulas, Fluid Phase Equilib. 224 (2004) 193-197.
[22] Y. Maham, A.E. Mather, L.G. Hepler, J. Chem. Eng. Data 42 (1997) 988-992.
[23] M.L. Posey, Thermodynamic Model for Acid Gas Loaded Aqueous Alkanolamine Solutions, The University of Texas, Austin, 1996. p. 37.
[24] F.Y. Jou, A.E. Mather, J. Chem. Eng. Data 51 (2006) 1429-1430.
[25] D.M. Austgen, A Model of (Vapor + Liquid) Equilibria for Acid (Gas + Alkanolamine +Water) Systems, The University of Texas, Austin, 1989. pp. 102-107.
[26] J.P. Jakobsen, J. Krane, H.F. Svendsen, Ind. Eng. Chem. Res. 44 (2005) 98949903.
[27] S. Ma'mun, R. Nilsen, H.F. Svendsen, O. Juliussen, J. Chem. Eng. Data 50 (2005) 630-634.
[28] B. Lemoine, Y. Li, R. Cadours, C. Bouallou, D. Richon, Fluid Phase Equilib. 172 (2000) 261-277.
[29] T.J. Edwards, G. Maurer, J. Newman, J.M. Prausnitz, AIChE J. 24 (1978) 966-976.
[30] A.P. Kamps, G. Maurer, J. Chem. Eng. Data 41 (1996) 1505-1513.

JCT 12-563