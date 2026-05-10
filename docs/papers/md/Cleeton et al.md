\title{
Competitive $\mathrm{H}_{2} \mathrm{~S}-\mathrm{CO}_{2}$ absorption in reactive aqueous methyldiethanolamine solution: Prediction with ePC-SAFT
}

\author{
Conor Cleeton, Odin Kvam, Riccardo Rea, Lev Sarkisov, Maria Grazia De Angelis* \\ *corresponding author
}

\begin{abstract}
Reactive absorption of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ in aqueous methyldiethanolamine (MDEA) solutions is considered within the ePC-SAFT equation of state. We demonstrate that ePC-SAFT can be employed in a predictive manner without regression of additional temperature-correlated terms. Mixed system predictions are tested using a consistent set experimental data covering a wide range of temperatures ( $313 \mathrm{~K}-413 \mathrm{~K}$ ), partial pressures ( $0.001 \mathrm{kPa}-1000 \mathrm{kPa}$ ), and MDEA mass fractions ( $0.05 w_{\text {MDEA }}- 0.75 w_{\text {MDEA }}$ ). Predicted partial pressures for acid gas absorption show good agreement for low MDEA fractions ( $w_{\text {MDEA }}<0.5$ ). Absorption selectivity in binary $\mathrm{H}_{2} \mathrm{~S}+\mathrm{CO}_{2}$ absorption is correctly predicted, with absolute average deviations of $57.18 \%$ and $79.32 \%$ for partial pressures of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$. We identify a significant deterioration in ePC-SAFT predictive power for the high-MDEA regime ( $w_{\text {MDEA }}>0.5$ ), likely originating from underlying assumptions in the Debye-Hückel electrolyte free energy treatment and representation of ionic species.
\end{abstract}

\section*{1. Introduction}

In processes such as natural gas dehydration [1], $\mathrm{CO}_{2}$ capture from flue gas streams [2], natural gas and biogas upgrading [3], and in the development of renewable energies [4], acid-gas capture and sequestration is of integral importance. While initial investigations into gas sweetening were concerned with the removal of $\mathrm{H}_{2} \mathrm{~S}$ to very low concentrations to avoid catalyst poisoning [5,6] and to reduce sulphur emissions from combustion,[6] removal of $\mathrm{CO}_{2}$ from gas streams has become the focus of much experimental effort in later years. This shift has been prompted by growing concerns over anthropogenic-induced climate change, which necessitates energy efficient acid-gas separating technologies [7].
Gas separations based on the chemical absorption / desorption process with aqueous alkanolamine solvents is currently considered as the state-of-the-art technology [8]. Particularly, monoethanolamine (MEA), diethanolamine (DEA), and methyldiethanolamine (MDEA) have been utilised extensively for acid-gas processing in an industrial context since the 1930's [9]. Relative to MEA and DEA, MDEA has gained a significant share of the market in the past decade due to several advantageous properties: selectivity towards $\mathrm{H}_{2} \mathrm{~S}$ when treating $\mathrm{H}_{2} \mathrm{~S}-\mathrm{CO}_{2}$ multicomponent acid-gas streams; low solvent vapour pressure; low corrosivity; high degradation resistance; and efficient energy utilisation.[1] To mitigate the research, plant, and operating costs associated with developing optimal solvent blends, thermodynamic models that accurately describe the vapour-liquid equilibrium (VLE) and thermodynamics of water-amine-gas systems is a prerequisite[10,11].
A range of thermodynamic frameworks have been proposed for representing solvent-gas mixtures, including activity coefficient models [12], classical cubic equations of state (EoS) [13], and statisticalmechanics based approaches [14]. Good results have been obtained for the VLE behaviour of amine-water-gas systems using activity coefficient models such as the electrolyte Non-Random Two-Liquid (e-NRTL) [15,16] and other local compositions models, which are reviewed elsewhere [14,17]. Recent work on mixed gas absorption using the extended UNIQUAC model [18,19] shows that various chemical theories may be employed to good effect in the characterisation of these systems. However, predictive power is often limited by the need for system-specific composition- and temperature-dependent parameters, typically regressed against ternary experimental data.
An EoS based on Statistical Associating Fluid Theory (SAFT) was first introduced by Chapman et al. [20,21], and was developed by Huang and Radosz [22,23] for engineering calculations in 1990 / 1991. Button and Gubbins [24] applied the SAFT EoS to mixtures containing $\mathrm{CO}_{2}$ and aqueous alkanolamines, obtaining good results for the VLE behaviour while neglecting chemical equilibria.

Nasrifar and Tafazzol [25] further investigated acid-gas - aqueous alkanolamine systems using PCSAFT [26,27] while simultaneously considering the chemical equilibria of reacting species in solution. The authors were able to obtain semi-quantitative agreement between PC-SAFT predictions and experimental data using no binary interaction parameters, however large deviations were observed in the case of MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$. Pahlavanzadeh et al. [28] further pursued the MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ system using PC-SAFT, introducing a temperature-dependent binary interaction parameter between MDEA and $\mathrm{H}_{2} \mathrm{O}$ correlated using experimental excess enthalpy of mixing data. Absolute Average Deviations (AADs) of $<31.65 \%$ were obtained for MDEA weight fractions of $w_{\text {MDEA }}<0.5$, total pressures $<4 \mathrm{MPa}$, in the temperature range of $297 \mathrm{~K}-413 \mathrm{~K}$, and $\mathrm{CO}_{2}$ loadings of $<1.2 \mathrm{~mol} \mathrm{CO}_{2}$ / mol MDEA.
The first attempt at applying an electrolyte SAFT EoS to aqueous MDEA - CO2 systems was undertaken by Uyan et al. [29] using ePC-SAFT, which has been shown to satisfactorily model and predict the phase equilibria of complex electrolyte solutions [30,31]. Through the introduction of temperaturedependent binary interaction parameters between $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ and MDEA - $\mathrm{H}_{2} \mathrm{O}$, good predictions for the solubility of $\mathrm{CO}_{2}$ in MDEA weight fractions of $w_{M D E A}<0.32$ were achieved. Similarly, in a recent work by Wangler et al. [32] solubility and enthalpy of absorption of $\mathrm{CO}_{2}$ in aqueous MDEA was predicted for MDEA weight fractions of $w_{\text {MDEA }}<0.6$ using temperature-dependent binary interaction parameters fitted to osmotic coefficient data. The authors also report predictions for the solubility of $\mathrm{H}_{2} \mathrm{~S}$ in aqueous MDEA weight fractions of $w_{\text {MDEA }}=0.32$ and 0.48 , and further investigate the influence of inert $\mathrm{CH}_{4}$ on $\mathrm{CO}_{2}$ solubility. Acid gas absorption in aqueous MDEA has also been investigated based on nonelectrolyte equations of state, with Alkhatib et al. [33] reporting good performance for simultaneous $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ absorption with soft-SAFT using an implicit reaction model, again resorting to temperaturecorrelated interaction parameters. While the use of temperature-correlated interaction parameters may improve agreement with experimental data, they are ad-hoc extensions of the equation of state which may act to conceal rather than elucidate failings of the underlying model. In this work, we instead aim to model acid gas absorption using the parameter space provided by ePC-SAFT.

\section*{2. Thermodynamic Framework}

\section*{2.1 ePC-SAFT Equation of State}

The ePC-SAFT EoS provides a simplified expansion of the residual Helmholtz energy $a^{\text {res }}$ according to the works by Gross and Sadowski [26,27] and Held et al.[30,31] as:

$$
\begin{equation*}
\frac{a^{\text {res }}}{R T}=\frac{a^{h s}}{R T}+\frac{a^{\text {chain }}}{R T}+\frac{a^{\text {disp }}}{R T}+\frac{a^{\text {assoc }}}{R T}+\frac{a^{\text {ion }}}{R T} \tag{1}
\end{equation*}
$$


Where $a^{h s}$ is the hard-sphere contribution, $a^{\text {chain }}$ is the chain forming contribution, $a^{\text {disp }}$ is the dispersion contribution, $a^{\text {assoc }}$ is the hydrogen-bonding association contribution, $a^{\text {ion }}$ is the Debye-Hückel contribution, $R$ is the molar gas constant, and $T$ is temperature.
The ePC-SAFT EoS accounts for short-range interactions by considering $a^{h s}, a^{\text {chain }}, a^{\text {disp }}$ and $a^{\text {assoc }}$, and long-range Coulombic interactions by considering $a^{\text {ion }}$. Five adjustable PC-SAFT parameters are needed to describe any pure non-ionic component: segment number $m_{i}$, temperature independent segment diameter $\sigma_{i}$, dispersion energy parameter $\varepsilon_{i}$, association energy well depth $\varepsilon^{A_{i} B_{i}}$, and association volume $\kappa^{A_{i} B_{i}}$. For mixtures, conventional Berthelot-Lorentz combining rules [27] were applied for dispersion interactions while Wolbach and Sandler [34] cross-association combining rules were used for mixtures of associating molecules.
lonic species are modelled as spherical non-associating species [35] where $\sigma_{i}^{i o n}$ and $\varepsilon_{i}^{i o n}$ are the temperature independent solvated ion diameter and ionic dispersion energy parameter, respectively, and $m_{i}^{\text {ion }}=1$. The ionic term $a^{\text {ion }}$ describes ion free energy by means of Debye-Hückel theory [30,31], with continuum relative permittivity $\epsilon_{r}$ taken to be an empirically obtained property of the solvent. In principle, $\epsilon_{r}$ and hence the Debye-Hückel contribution varies with system conditions [36]. We follow the approach by Cameretti and Sadowski [35] and Held et al. [30], with the relative permittivity of water $\epsilon_{r}^{w}$ described by:[37]

$$
\begin{equation*}
\epsilon_{r}^{w}=\epsilon_{r}^{0}(T)+a_{0} \ln \left(\frac{a_{1}+P}{a_{1}+10}\right) \tag{2}
\end{equation*}
$$


Where $\epsilon_{r}^{0}(T)$ is the relative permittivity of water at temperature $T$ and 10 MPa , and $a_{0}$ and $a_{1}$ are provided by Floriano and Nascimento [37] as functions of temperature.

In the original formulation of ePC-SAFT [30,35], ions are considered to be fully dissociated and thus short-range dispersive forces between anion-cation are neglected. For systems with high electrolyte concentrations or weak-electrolyte solutions, ions may not be fully solvated and are no longer well described by Debye-Hückel theory alone [31]. For this reason, the 'revised' ePC-SAFT model of Held et al. [31] is employed in this study, where short-range dispersive forces between oppositely charged ions are considered through $a^{\text {disp }}$. No additional molecular parameters are needed as short-range dispersive forces are modelled using $\sigma_{i}^{i o n}, m_{i}$ (set equal to one for all ionic species [30]), and $\varepsilon_{i}^{i o n}$, reflecting the energy of ion hydration.

\subsection*{2.2. Phase Equilibria}

The isofugacity criterion was used to solve the VLE equations [29]:

$$
\begin{gather*}
x_{i} \varphi_{i}^{L}(T, P, x)=y_{i} \varphi_{i}^{V}(T, P, y)  \tag{3}\\
\left\{i=\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}, \mathrm{CH}_{4}, \mathrm{H}_{2} \mathrm{O}, \mathrm{MDEA}\right\}
\end{gather*}
$$


Where $x_{i}$ and $y_{i}$ are the mole fractions of component $i$ in the liquid ( $L$ ) and vapour ( $V$ ) phase, respectively, and $\varphi_{i}$ is the fugacity coefficient of component $i$ at temperature $T$ and pressure $P$, calculated using the ePC-SAFT EoS. Ionic species are assumed to only exist in the liquid phase. The dependence of fugacity coefficients of $\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}, \mathrm{H}_{2} \mathrm{O}$, and MDEA on ionic species is explicitly considered in the ePC-SAFT framework. The fugacity coefficient of species $i$ is related to the mixture residual properties according to [26]:

$$
\begin{equation*}
\ln \varphi_{i}=\left(Z_{m i x}-1\right)-\ln Z_{m i x}+a^{r e s}+\left(\frac{\partial a^{r e s}}{\partial x_{i}}\right)_{T, v, x_{i \neq j}}-\sum_{j}\left[x_{j}\left(\frac{\partial a^{r e s}}{\partial x_{j}}\right)_{T, v, x_{j \neq i}}\right] \tag{4}
\end{equation*}
$$


Where $Z_{\text {mix }}$ is derived using the thermodynamic relationship in Eq. 5.[38] and $a^{\text {res }}$ is obtained by Eq. 1.

$$
\begin{equation*}
Z_{m i x}=1+\eta\left(\frac{\partial a^{r e s}}{\partial \eta}\right)_{T, x_{i}} \tag{5}
\end{equation*}
$$


\subsection*{2.3. Chemical Equilibria}

In addition to the physical solubility of $\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}$, and $\mathrm{CH}_{4}$ in aqueous MDEA, chemical absorption of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ occur by reacting with MDEA in solution through an acid-base mechanism. The following reaction scheme is adopted in this work [25]:

$$
\begin{align*}
2 \mathrm{H}_{2} \mathrm{O} & \stackrel{\mathrm{~K}^{1} \mathrm{eq}, \mathrm{x}}{\Longleftrightarrow} \mathrm{OH}^{-}+\mathrm{H}_{3} \mathrm{O}^{+}  \tag{R.1.}\\
\mathrm{CO}_{2}+2 \mathrm{H}_{2} \mathrm{O} & \stackrel{\mathrm{~K}^{2} \mathrm{eq}, \mathrm{x}}{\Longleftrightarrow} \mathrm{HCO}_{3}^{-}+\mathrm{H}_{3} \mathrm{O}^{+}  \tag{R.2.}\\
\mathrm{HCO}_{3}^{-}+\mathrm{H}_{2} \mathrm{O} & \stackrel{\mathrm{~K}^{3} \mathrm{eq}, \mathrm{x}}{\Longleftrightarrow} \mathrm{CO}_{3}^{2-}+\mathrm{H}_{3} \mathrm{O}^{+}  \tag{R.3.}\\
\mathrm{MDEAH}^{+}+\mathrm{H}_{2} \mathrm{O} & \stackrel{\mathrm{~K}^{4} \mathrm{q}, \mathrm{x}}{\Longleftrightarrow} \mathrm{MDEA}^{\circ}+\mathrm{H}_{3} \mathrm{O}^{+}  \tag{R.4.}\\
\mathrm{H}_{2} \mathrm{~S}+\mathrm{H}_{2} \mathrm{O} & \stackrel{\mathrm{Keq}^{5}, \mathrm{x}}{\Longleftrightarrow} \mathrm{HS}^{-}+\mathrm{H}_{3} \mathrm{O}^{+}  \tag{R.5.}\\
\mathrm{HS}^{-}+\mathrm{H}_{2} \mathrm{O} & \stackrel{\mathrm{~K}_{\mathrm{eq}, \mathrm{x}}}{\Longleftrightarrow} \mathrm{~S}^{2-}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{R.6.}
\end{align*}
$$


The chemical equilibrium constants $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{1}-\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{6}$ for the liquid phase reactions are expressed mathematically by [39]:

$$
\begin{equation*}
\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{\mathrm{j}}=\prod_{i}\left(x_{i} \gamma_{i}\right)^{v_{i, j}} \tag{6}
\end{equation*}
$$


In Eq. 6., $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{\mathrm{j}}$ is the mole-fraction based equilibrium constant for reaction $j, x_{i}$ and $\gamma_{i}$ refer to the mole fraction and activity coefficient of species $i$, and $v_{i, j}$ is the stoichiometric coefficient of species $i$ in reaction $j . \mathrm{K}_{\text {eq,x }}^{\mathrm{j}}$ is calculated using Eq. 7:

$$
\begin{equation*}
\ln \left(\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{\mathrm{j}}\right)=\mathrm{A}+\frac{\mathrm{B}}{\mathrm{~T}}+\mathrm{C} \ln (\mathrm{~T})+\mathrm{DT} \tag{7}
\end{equation*}
$$


Where the constants A, B, C, and D are obtained from reference [40] and are reported in Table 1.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1. Parameters for temperature-dependent mole-fraction reaction equilibrium constants.[40]}
\begin{tabular}{|l|l|l|l|l|l|}
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{\mathrm{j}}$ & A & B / K & C & $\mathrm{D} / \mathrm{K}^{-1}$ & T Range / K \\
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{1}$ & 132.899 & -13445.9 & -22.4773 & 0 & 273-498 \\
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{2}$ & 231.456 & -12092.1 & -36.7816 & 0 & 273-498 \\
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{3}$ & 216.049 & -12431.7 & -35.4819 & 0 & 273-498 \\
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{4}$ & -9.4165 & -4234.98 & 0 & 0 & 298-333 \\
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{5}$ & 214.582 & -12995.4 & -33.5471 & 0 & 273-423 \\
\hline $\mathrm{K}_{\mathrm{eq}, \mathrm{x}}^{6}$ & -32.0 & -3338.0 & 0 & 0 & 287-343 \\
\hline
\end{tabular}
\end{table}

The equilibrium constants in Table 1 are corrected to the infinite dilution activity coefficients of solutes in solvents, where $\mathrm{H}_{2} \mathrm{O}$ and MDEA are treated as solvents. Therefore, the fugacity coefficients obtained from ePC-SAFT that are used in Eq. 6. must be normalised using the correct convention. For $\mathrm{H}_{2} \mathrm{O}$ and MDEA, they were calculated and symmetrically normalised (i.e. related to the pure-component state) using Eq. 8.:[14]

$$
\begin{equation*}
\gamma_{i}=\frac{\varphi_{i}(T, P, x)}{\varphi_{i}^{0}\left(T, P, x_{i}=1\right)} \tag{8}
\end{equation*}
$$


Where $\gamma$ is the activity coefficient, $\varphi$ is the fugacity coefficient, and superscript 0 indicates the pure component reference state. For all other components, an asymmetric normalisation convention (i.e. related to the infinite-diluted state of the component) was used according to Eq. 9. [14]:

$$
\begin{equation*}
\gamma_{i}^{*}=\frac{\varphi_{i}(T, P, x)}{\varphi_{i}^{\infty}\left(T, P, x_{i}=0\right)} \tag{9}
\end{equation*}
$$


In order to fully define the system of independent equations, additional component mole balances are required:

$$
\begin{gather*}
\mathrm{N}_{\mathrm{CO}_{2}}^{\mathrm{o}}=\mathrm{N}_{\mathrm{CO}_{2}}+\mathrm{N}_{\mathrm{HCO}_{3}^{-}}+\mathrm{N}_{\mathrm{CO}_{3}^{2-}}  \tag{10}\\
\mathrm{N}_{\mathrm{MDEA}}^{\mathrm{o}}=\mathrm{N}_{\mathrm{MDEA}}+\mathrm{N}_{\mathrm{MDEAH}^{+}}  \tag{11}\\
\mathrm{N}_{\mathrm{H}_{2} \mathrm{O}}^{\mathrm{o}}=\mathrm{N}_{\mathrm{H}_{2} \mathrm{O}}+\mathrm{N}_{\mathrm{OH}^{-}}+\mathrm{N}_{\mathrm{HCO}_{3}^{-}}+\mathrm{N}_{\mathrm{CO}_{3}^{2-}}  \tag{12}\\
\mathrm{N}_{\mathrm{H}_{2} \mathrm{~S}}^{\mathrm{o}}=\mathrm{N}_{\mathrm{H}_{2} \mathrm{~S}}+\mathrm{N}_{\mathrm{HS}^{-}}+\mathrm{N}_{\mathrm{S}^{2-}}  \tag{13}\\
\mathrm{N}_{\mathrm{MDEAH}^{+}}+\mathrm{N}_{\mathrm{H}_{3} \mathrm{O}^{+}}=\mathrm{N}_{\mathrm{HCO}_{3}^{-}}+2 \mathrm{~N}_{\mathrm{CO}_{3}^{2-}}+\mathrm{N}_{\mathrm{OH}^{-}}+\mathrm{N}_{\mathrm{HS}^{-}}+2 \mathrm{~N}_{\mathrm{S}^{2-}} \tag{14}
\end{gather*}
$$


Eq. 10. -13 . are $\mathrm{CO}_{2}$, MDEA, $\mathrm{H}_{2} \mathrm{O}$, and $\mathrm{H}_{2} \mathrm{~S}$ mole balances, while Eq. 14. accounts for the overall electroneutrality condition.

\subsection*{2.4. Enthalpy of Absorption}

The enthalpy of absorption of acid-gases in aqueous MDEA is an important property to investigate and is relevant in both an industrial and theoretical context. The enthalpy of absorption is directly related to solvent recovery energy requirements[41] in acid-gas separation processes, and such data is necessary for a good thermodynamic description of MDEA - $\mathrm{H}_{2} \mathrm{O}$ - acid-gas systems. Enthalpy of absorption is calculated using the approximate Gibbs-Helmholtz[42] and van't Hoff equations, following Wangler et al.[32]

$$
\begin{equation*}
\Delta h_{i}^{a b s}=-R T^{2}\left(\frac{\partial \ln f_{i}}{\partial T}\right)_{P, x}+\sum_{j} R T^{2} \frac{n_{j}}{n_{i}^{a b s}} \frac{d \ln K_{j}}{d T} \tag{15}
\end{equation*}
$$

where $f_{i}$ is the fugacity and $n_{i}^{a b s}$ the total amount absorbed of species $i$, and $n_{j}$ is the reaction extent of reaction $j$. We disregard the ideal gas enthalpy contribution as data is not available for all species[32].

\section*{3. Results and discussion}

\subsection*{3.1. Molecular Parameters}

An accurate description of multifunctional associating binary mixtures is dependent on the selection of optimal pure component parameters. Preceding this, the choice of association scheme plays an integral role in defining the physics of the components to be modelled.
MDEA comprises two hydroxyl and one tertiary amine functional group. It has been suggested that distinguishing between the amine and hydroxyl functional groups gives an improved description of aqueous alkanolamine mixtures within the SAFT framework [43]. However, this level of molecular detail comes at the cost of additional molecular parameters and risk of overfitting [44]. A simpler approach was taken by Avlund et al.[45], assigning two association sites to each hydroxyl group and ignoring the amine group altogether. Similarly, Button and Gubbins [24] recognised the multifunctional nature of alkanolamines, but did not consider the asymmetric association in their model. The authors used a single association site for each hydrogen connected to oxygen or nitrogen, and a single association site for the two sets of lone pairs on oxygen.
In this work, the association schemes 2 B and 4 C are considered for MDEA, following the classification of Huang and Radosz [22] and shown in Figure 1. The 4C scheme employs the same logic as Avlund et al.[45], while the 2B scheme models MDEA with two association sites: one for the lone-pair sets on the oxygen atoms and one for the hydrogen atoms.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-05.jpg?height=803&width=455&top_left_y=1046&top_left_x=804}
\captionsetup{labelformat=empty}
\caption{Figure 1. MDEA (top) represented in ePC-SAFT using the 4C (middle) and 2B association scheme (bottom). Sites O and $\mathrm{O}_{2}$ correspond to the lone-pair sets on single-oxygen and doubleoxygen, respectively, and sites H and $\mathrm{H}_{2}$ to the single-hydrogen and double-hydrogens in the hydroxyl groups.}
\end{figure}

The molecular parameters for pure MDEA are regressed against pure-component vapour pressure[46] and liquid density[47] data in the temperature range $298 \mathrm{~K}-422 \mathrm{~K}$. These properties are chosen as the vapour pressure is of particular interest in practical chemical engineering applications and depends strongly on the energy parameters, while density data permits the determination of size related parameters.[48] Experimental data for each property is obtained from a single literature source to minimise inconsistencies between data sets. The graphs of vapour pressure and liquid density are presented in Figure 2, and the molecular parameters are provided in Table 2.
For ionic species, ePC-SAFT parameters were taken from Held et al.[31] In their work ion parameters were regressed against solution densities and osmotic coefficients of single-solute aqueous electrolyte solutions, with resulting AADs generally not exceeding 3\%.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-06.jpg?height=522&width=1109&top_left_y=260&top_left_x=475}
\captionsetup{labelformat=empty}
\caption{Figure 2. Saturated vapour pressure (left) and saturated liquid density (right) of pure MDEA as a function of temperature from 298 K to 422 K using the 2 B and 4 C association schemes. Density data obtained from reference [47], vapour pressure data obtained from reference [46].}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2. Summary of pure component ePC-SAFT molecular parameters used in this work}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Species} & \multirow[t]{2}{*}{Association Scheme} & \multirow{2}{*}{$m$ [ - ]} & \multirow{2}{*}{$\sigma$ [Å]} & \multirow{2}{*}{$\varepsilon / k_{B}$ [K]} & \multirow{2}{*}{$\varepsilon^{A B} / k_{B}$ [K]} & \multirow{2}{*}{$\kappa^{A B}$ [ - ]} & \multicolumn{2}{|c|}{\%AAD} & \multirow[t]{2}{*}{$k_{i-\mathrm{H}_{2} \mathrm{O}}^{\mathbf{a}}$} & \multirow[t]{2}{*}{Source} \\
\hline & & & & & & & $P^{\text {sat }}$ & $\rho_{L}^{\text {sat }}$ & & \\
\hline \multirow[t]{2}{*}{MDEA} & 2B & 3.7591 & 3.5372 & 309.26 & 2093.30 & 0.06739 & 3.97 & 0.41 & N/A & This work \\
\hline & 4C & 4.3589 & 3.3474 & 237.19 & 1491.60 & 0.29836 & 6.30 & 0.40 & 0 & This work \\
\hline \multirow[t]{2}{*}{$\mathrm{H}_{2} \mathrm{O}$} & 2B & 1.9599 & 2.3620 & 279.42 & 2059.28 & 0.17500 & 1.19 & 3.08 & 0 & [49] \\
\hline & 4C & 2.1945 & 2.2290 & 141.66 & 1804.17 & 0.20390 & 1.98 & 0.83 & 0 & [49] \\
\hline $\mathrm{CH}_{4}$ & - & 1.0000 & 3.7039 & 150.03 & - & - & 0.36 & 0.67 & $0.098{ }^{\text {a. }}$ & [25] \\
\hline $\mathrm{CO}_{2}$ & - & 2.6037 & 2.5550 & 151.04 & - & - & 0.39 & 0.88 & -0.009 ${ }^{\text {a. }}$ & [50] \\
\hline $\mathrm{H}_{2} \mathrm{~S}$ & - & 1.6686 & 3.0349 & 229.00 & - & - & 0.39 & 0.59 & $0.028{ }^{\text {a. }}$ & [25] \\
\hline $\mathrm{HCO}_{3}{ }^{-}$ & - & 1 & 2.9296 & 70.00 & - & - & - & - & 0 & [29] \\
\hline $\mathrm{CO}_{3}{ }^{2-}$ & - & 1 & 2.4422 & 249.26 & - & - & - & - & -0.250 & [29] \\
\hline $\mathrm{MDEAH}^{+}$ & - & 1 & 3.3474 & 237.19 & - & - & - & - & 0 & b. \\
\hline $\mathrm{H}_{3} \mathrm{O}^{+}$ & - & 1 & 3.4654 & 500.00 & - & - & - & - & 0.250 & [29] \\
\hline $\mathrm{OH}^{-}$ & - & 1 & 2.0177 & 650.00 & - & - & - & - & -0.250 & [29] \\
\hline $\mathrm{HS}^{-}$ & - & 1 & 3.0349 & 229.00 & - & - & - & - & 0 & b. \\
\hline $\mathrm{S}^{2-}$ & - & 1 & 3.0349 & 229.00 & - & - & - & - & 0 & b. \\
\hline
\end{tabular}
\end{table}
a. Determined in this work using $\mathrm{H}_{2} \mathrm{O}(4 \mathrm{C})$ molecular parameters.
b. Transferred from MDEA and $\mathrm{H}_{2} \mathrm{~S}$, respectively.

\subsection*{3.2. Binary Systems}

\subsection*{3.2.1. Water - MDEA}

Similar to MDEA both 2B and 4C association schemes are considered for $\mathrm{H}_{2} \mathrm{O}$, with resulting model
predictions for the binary MDEA - $\mathrm{H}_{2} \mathrm{O}$ mixture compared against VLE data of Kim et al.[51] in Figure 3. No binary interaction parameters were fitted to VLE data. The proposed association schemes show good agreement with experimental binary VLE data over the whole temperature range of consideration. The MDEA - $\mathrm{H}_{2} \mathrm{O} 4 \mathrm{C}-2 \mathrm{~B}$ scheme is outperformed by the $2 \mathrm{~B}-2 \mathrm{~B}$ and $4 \mathrm{C}-4 \mathrm{C}$ schemes, while the $2 \mathrm{~B}-2 \mathrm{~B}$ and $4 \mathrm{C}-4 \mathrm{C}$ scheme perform similarly for VLE predictions. The $4 \mathrm{C}-4 \mathrm{C}$ scheme is adopted in subsequent analysis as a 4C model for water preserves the tetrahedral character of the molecular geometry of the compound, and similarly a 4C association is better representative of the multifunctional nature of MDEA.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-07.jpg?height=1125&width=1726&top_left_y=623&top_left_x=171}
\captionsetup{labelformat=empty}
\caption{Figure 3. Isothermal P-x-y experimental VLE [51] data and modelling results for MDEA - $\mathrm{H}_{2} \mathrm{O}$ at different temperatures and association schemes using molecular parameters reported in Table 2. $k_{\text {MDEA }-\mathrm{H}_{2} \mathrm{O}}=0$ for VLE predictions. (Left Panels) 2B-2B scheme; (Middle Panels) 4C-2B scheme; (Right Panels) 4C -4 C scheme.}
\end{figure}

\subsection*{3.2.2.Aqueous Gas Solubility ( $\mathrm{CH}_{4}-\mathrm{H}_{2} \mathrm{O}, \mathrm{H}_{2} \mathrm{~S}-\mathrm{H}_{2} \mathrm{O}, \mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ )}

Binary systems of $\mathrm{CH}_{4}, \mathrm{CO}_{2}$, and $\mathrm{H}_{2} \mathrm{~S}$ with $\mathrm{H}_{2} \mathrm{O}$ are modelled using pure-component ePC-SAFT molecular parameters from the literature, as detailed in Table 2. To ensure a stronger predictive ability with respect to other correlative approaches, binary interaction parameters were fitted to experimental VLE data of the solute in $\mathrm{H}_{2} \mathrm{O}$ only, with no binary parameter used for MDEA in mixed solvent systems. The objective function used to fit the binary interaction parameter is the same as described by Gross and Sadowski [26].

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-08.jpg?height=969&width=1543&top_left_y=315&top_left_x=242}
\captionsetup{labelformat=empty}
\caption{Figure 4. Isothermal P-x-y experimental VLE data for $\mathrm{CH}_{4}-\mathrm{H}_{2} \mathrm{O}$ (Left Panels) [59], $\mathrm{H}_{2} \mathrm{~S}- \mathrm{H}_{2} \mathrm{O}$ (Middle Panels) [82], and $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ (Right Panels) [83] and modelling results at different temperatures using molecular parameters reported in Table 2. AADs for $\mathrm{CH}_{4}$ $\mathrm{H}_{2} \mathrm{O}, \mathrm{H}_{2} \mathrm{~S}-\mathrm{H}_{2} \mathrm{O}$, and $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ subsystems are $6.67 \%, 7.26 \%$, and $13.72 \%$, respectively.}
\end{figure}

The results of the procedure are given graphically in Figure 4 and $k_{i j}$ values are provided in Table 2. We see good agreement between the model and experimental data for $\mathrm{CH}_{4}$ and $\mathrm{H}_{2} \mathrm{~S}$, with AAD values of $6.67 \%$ and $7.26 \%$ over the respective temperature ranges. Larger deviations between model output and experimental data is observed for $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$, likely due to Lewis acid-base type interactions between the carbon atom on $\mathrm{CO}_{2}$ and the oxygen atom on $\mathrm{H}_{2} \mathrm{O}$ [52]. Such interactions may be modelled using a solvating cross-association scheme similar in principle to the treatment of an MDEA - $\mathrm{H}_{2} \mathrm{O}$ system [50]. However, to reduce the computational complexity the non-solvating scheme was retained. An AAD of $13.72 \%$ was deemed tolerable for a single temperature-independent interaction parameter, noting that the error is not markedly dissimilar to AADs reported in the literature for the temperature and pressure range of consideration, which vary from AAD $=5.26 \%-19.8 \% .[29,53,54]$

\subsection*{3.3. Ternary Systems}

\subsection*{3.3.1. MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CH}_{4}$}

In a first step towards modelling ternary systems, the physical solubility of $\mathrm{CH}_{4}$ in aqueous MDEA was investigated. Modelling results were compared to the experimental data of Jou et al. [55] and Schmidt et al. [56] for weight fraction $w_{\text {MDEA }}=0.347$ and $w_{\text {MDEA }}=0.5$ solutions, respectively. The results are provided in Figure 5.
At low pressures the solubility of $\mathrm{CH}_{4}$ in aqueous MDEA is a weak function of temperature, while more pronounced temperature dependencies are observable in the high-pressure region. The ePC-SAFT model systematically underpredicts the total pressure of the system in both $w_{\text {MDEA }}=0.347$ and $w_{\text {MDEA }} =0.5$, however the model performs better for $w_{\text {MDEA }}=0.347$ with an AAD $=18.43 \%$ as opposed to an $\mathrm{AAD}=20.55 \%$ for $w_{\text {MDEA }}=0.5$.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-09.jpg?height=691&width=1351&top_left_y=310&top_left_x=335}
\captionsetup{labelformat=empty}
\caption{Figure 5. Comparison of experimental data from Jou et al.[55] (empty symbols) and Schmidt et al. [56] (empty symbols) for $w_{\text {MDEA }}=0.347$ and 0.5 , respectively, for $\mathrm{CH}_{4}$ solubility in aqueous MDEA at 298 K , 313K, and 343K. Ternary modelling results given by solid lines, and $\mathrm{H}_{2} \mathrm{O}-\mathrm{CH}_{4}$ modelling results from Figure 4 given by dashed lines. Filled symbols represent the experimental data of YarmAgaev [59]. AAD for $w_{\text {MDEA }}=0.347: 18.43 \%$. AAD for $w_{\text {MDEA }}=0.5: 20.55 \% . k_{\mathrm{H}_{2} \mathrm{O}-\mathrm{CH}_{4}}=0.098$ and

$$
k_{\mathrm{H}_{2} \mathrm{O}-\mathrm{MDEA}}=0
$$}
\end{figure}

\subsection*{3.3.2. MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$}

Absorption of $\mathrm{CO}_{2}$ in aqueous MDEA occurs both by conventional physical absorption and by the chemical equilibrium of reactions between MDEA, $\mathrm{H}_{2} \mathrm{O}$ and $\mathrm{CO}_{2}$. Resulting liquid phase species distribution for $\mathrm{CO}_{2}$ absorption in a $w_{M D E A}=0.23$ solution at 293 K was calculated in ePC-SAFT and compared to the experimental data of Jakobsen et al. [57]. Experimental species distribution data is scarce in the literature, however the data of Jakobsen et al. are in agreement with the experimental work of Derks et al. [58], so a reliable evaluation of model performance may be obtained using the data of Jakobsen et al. as reference. The results are provided in Figure 6.
It is evident that the model gives quantitative agreement for MDEA, MDEAH ${ }^{+}$, and $\mathrm{HCO}_{3}^{-}$over the whole loading range. $\mathrm{CO}_{3}{ }^{2-}$ concentration in solution displays the largest disagreement with experiment; a maximum in modelled mole fraction of $\approx 4 \times 10^{-3}$ occurs at $0.2 \mathrm{~mol} \mathrm{CO} / \mathrm{mol}$ MDEA and subsequently declines with increasing loading of $\mathrm{CO}_{2}$. While the ePC-SAFT modelling result appears in error to the experimental data for $\mathrm{CO}_{3}{ }^{2-}$, it is concordant with the ePC-SAFT modelling results of Uyan et al.[29] and, to a lesser extent, the PC-SAFT modelling results of Pahlavanzadeh et al. [28], suggesting the difference in modelling output is the result of adopting different molecular parameters for non-ionic species (in the case of Uyan et al.[29]) or failing to account for non-ideal solution behaviour (in the case of Pahlavanzadeh et al.[28]). Finally, we note that the model predicts $\mathrm{CO}_{3}{ }^{2-}$ rather than $\mathrm{HCO}_{3}{ }^{-}$as the dominant $\mathrm{CO}_{2}$ reaction product at very low loadings.
For VLE behaviour, ionic species are considered non-volatile such that only MDEA, $\mathrm{H}_{2} \mathrm{O}$, and $\mathrm{CO}_{2}$ partition to the vapour phase. VLE predictions are based on the composition of the liquid phase at isothermal conditions and fixed MDEA weight fraction (solute-free basis).

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-10.jpg?height=696&width=842&top_left_y=294&top_left_x=559}
\captionsetup{labelformat=empty}
\caption{Figure 6. Mole-fraction based liquid phase species distributions in a ternary MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ solution at 293 K for $w_{\text {MDEA }}=0.23$. Symbols represent the experimental data of Jakobsen et al.[57] Modelling results are obtained using the equilibrium constants reported in Table 1 and the molecular and binary parameters reported in Table 2. Solid lines represent results obtained by considering species activity coefficients in solving the chemical equilibrium problem.}
\end{figure}

Many research groups have reported experimental VLE data for ternary MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ systems. In the DETHERM [59] database alone, there are 106 studies reporting solubility data for $\mathrm{CO}_{2}$ in aqueous MDEA. Naturally, some discrepancies between data sets exist, and not all reported experimental data are equally reliable. It is therefore important to establish a thermodynamically consistent database for model comparison, despite the difficulty in defining data acceptability criteria. For acid-gas absorption in aqueous MDEA, a self-consistent dataset will exhibit: (1) a linear relationship between the logarithm of the acid-gas partial pressure and the acid-gas loading; (2) an increase in acid-gas partial pressure with an increase in MDEA concentration at fixed loading and temperature; (3) an increase in acid-gas

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-10.jpg?height=771&width=1573&top_left_y=1653&top_left_x=175}
\captionsetup{labelformat=empty}
\caption{Figure 7. Isothermal VLE of ternary MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ system at different temperatures in a $w_{\text {MDEA }}=0.189$ aqueous solution (Left Panel) and $w_{\text {MDEA }}=0.489$ aqueous solution (Right Panel). ePC-SAFT modelling results obtained using the molecular and binary interaction parameters reported in Table 2. Symbols represent the experimental data of Kuranov et al. [61] $\left(w_{\text {MDEA }}=\right.$ 0.189) $\mathrm{AAD}=20.26 \%$ and Kamps et al. $[62]\left(w_{\text {MDEA }}=0.489\right) \mathrm{AAD}=47.75 \%$.}
\end{figure}
partial pressure with an increase in temperature at fixed loading and MDEA concentration [60]. Datasets which markedly deviate from these trends should be discarded from consideration.
In this work, the total pressure data of Kuranov et al.[61], Kamps et al.[62], and the $\mathrm{CO}_{2}$ partial pressure data of Huang et al.[63], Austgen et al. [40], and Rho et al.[64] are used to assess model performance. Overall, the data comprises MDEA weight fractions of $w_{\text {MDEA }}=0.05-0.75$, pressures of $1 \mathrm{~Pa}-6 \times 10^{6}$ Pa , temperatures of $313 \mathrm{~K}-413 \mathrm{~K}$, and $\mathrm{CO}_{2}$ loadings of $0.00187 \mathrm{~mol} \mathrm{CO}_{2} / \mathrm{mol} \mathrm{MDEA}-1.25 \mathrm{~mol} \mathrm{CO}_{2} / \mathrm{mol}$ MDEA. The data of Kuranov et al.[61], Huang et al.[63], Austgen et al.[40], and Rho et al.[64] have already been validated as thermodynamically self-consistent datasets[60], and the data of Kamps et al.[62] and Kuranov et al.[61] exhibit mutually-consistent thermodynamic behaviour [65] which supports the integrity of the data sources. A similar evaluation of thermodynamic consistency was conducted for ternary MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$ and quaternary MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$ systems. The resulting experimental database is detailed in Table 3.
It is evident that an accurate description of VLE for MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ systems can be obtained over a large temperature range in lower MDEA weight fraction solutions. Considering only pure component experimental data, binary mixture experimental data, and temperature-independent binary interaction parameters fitted to low temperature experimental data were used, the ePC-SAFT model is in excellent agreement with the data of Kuranov et al.;[61] an AAD of only $20.26 \%$ was obtained. For the $w_{M D E A}=$ 0.489 solution, a larger deviation of AAD $=47.75 \%$ was obtained. In particular, the 313 K absorption isotherm demonstrates the largest disagreement with experimental data and increases the AAD from $38.85 \%$ (for 353 K and 393 K isotherms) to $47.75 \%$ (for all isotherms). The system pressure is systematically underestimated for the 353 K and 393 K absorption isotherms with more pronounced deviations being observed at lower $\mathrm{CO}_{2}$ loadings.
The difficulty in simultaneously modelling low and high loading phase behaviours is a commonly encountered problem with acid-gas - aqueous alkanolamine systems, as the driving forces for absorption shift from chemical to physical absorption near saturation. At high loadings, the solvent is saturated with dissolved $\mathrm{CO}_{2}$ and little MDEA is available to react. Most experimental data reported in the literature is exclusive to industrially relevant operating ranges $\left(313 \mathrm{~K}<T<413 \mathrm{~K} ; 0.1<\mathrm{CO}_{2}\right.$ loading $\left.<1.1 ; 0.1<w_{M D E A}<0.4\right)[9,66,67]$, which is in the transitional regime between chemical and physical absorption. For instance, in Figure 6 at loadings $>0.4 \mathrm{~mol} \mathrm{CO}_{2} / \mathrm{mol}$ MDEA, ionic species formation asymptotically approaches a limiting value which corresponds to a chemically saturated state; subsequent loading of $\mathrm{CO}_{2}$ will occur by a physical absorption mechanism. While accurate modelling in this regime is important, and indeed such accuracy is demonstrated in Figure 7 (left panel), evaluation of low loading model performance probes the predictive capacity of ePC-SAFT in a more rigorous manner. To that end, Figure 8 shows the low loading modelling results compared to the experimental data of Huang et al.[63] and Austgen et al.[40].

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-11.jpg?height=753&width=748&top_left_y=1747&top_left_x=577}
\captionsetup{labelformat=empty}
\caption{Figure 8. Isothermal VLE of ternary MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ at 313 K in different MDEA weight fraction solutions. Symbols represent the data of Huang et al.[63] and Austgen et al.[40] Transition regime occurs at $\approx 0.8 \mathrm{~mol} \mathrm{CO} 2 / \mathrm{mol} \mathrm{MDEA}$. AAD $=69.67 \%$.}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3. Description of the experimental database for acid-gas ternary and quaternary systems used in this work to evaluate ePC-SAFT model predictions.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline Reference & Data Type & $N_{P}$ & T (K) & P (Pa) & $W_{\text {MDEA }}$ & Loading (mol solute / mol MDEA) \\
\hline \multicolumn{7}{|c|}{MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$} \\
\hline Kamps et al.[62] & VLE TPx, total pressure & 21 & 313393 & $2 \times 10^{5} -6 \times 10^{6}$ & 0.489 & 0.13-1.15 \\
\hline Kuranov et al.[61] & VLE TPx, total pressure & 26 & 333 413 & $10^{5}-3 \times 10^{6}$ & 0.189 & 0.16-1.25 \\
\hline Huang et al.[63] & VLE TPx, $\mathrm{CO}_{2}$ pressure & 12 & 313 & $1-10^{6}$ & 0.23-0.5 & 0.0025-1.08 \\
\hline Austgen et al.[40] & VLE TPx, $\mathrm{CO}_{2}$ pressure & 15 & 313 & $2-10^{6}$ & 0.23-0.5 & 0.003-1.12 \\
\hline Rho et al.[64] & VLE TPx, $\mathrm{CO}_{2}$ pressure & 101 & 323373 & $9 \times 10^{2} -6 \times 10^{5}$ & 0.05 0.75 & 0.00187-0.8 \\
\hline Jakobsen et al.[57] & Species concentration & 17 & 293 & - & 0.23 & 0.1-0.78 \\
\hline Arcis[68] & Enthalpy of absorption & 14 & 323 & - & 0.3 & 0.3-1.3 \\
\hline Mathonat[69] & Enthalpy of absorption & 55 & 353393 & - & 0.3 & 0.15-1.3 \\
\hline \multicolumn{7}{|c|}{MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$} \\
\hline Kamps et al.[62] & VLE TPx, total pressure & 26 & 313393 & $10^{5}-4 \times 10^{6}$ & 0.489 & 0.15-1.45 \\
\hline Kuranov et al.[61] & VLE TPx, total pressure & 25 & 333413 & $10^{5}-4 \times 10^{6}$ & 0.189 & 0.45-1.8 \\
\hline Oscarson and Izatt[70] & Enthalpy of absorption & 84 & 300400 & - & 0.489 & 0-2 \\
\hline \multicolumn{7}{|c|}{MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$} \\
\hline Dicko et al.[71] & VLE TPx, acid-gas pressure & 30 & 323 & $5 \times 10^{3}-10^{6}$ & 0.5 & \begin{tabular}{l}
0.1-0.7 ( $\mathrm{CO}_{2}$ ) \\
0.1-0.87 ( $\mathrm{H}_{2} \mathrm{~S}$ )
\end{tabular} \\
\hline Haghtalab[72] & VLE TPx, acid-gas pressure & 16 & 343 & $2.3 \times 10^{4}- 1.5 \times 10^{6}$ & 0.4 & \begin{tabular}{l}
0.25-0.6 (CO2) \\
0.1-0.32 ( $\mathrm{H}_{2} \mathrm{~S}$ )
\end{tabular} \\
\hline Jou et al.[73] & VLE TPx, acid-gas pressure & 90 & 313 & $1-3 \times 10^{5}$ & 0.35 & \begin{tabular}{l}
0-1.25 (CO2) \\
$0-0.8\left(\mathrm{H}_{2} \mathrm{~S}\right)$
\end{tabular} \\
\hline Jou et al.[74] & VLE TPx, acid-gas pressure & 104 & 313373 & $10^{2}-10^{6}$ & 0.5 & 0-1.2 ( $\mathrm{CO}_{2}$ ) $0-1.4\left(\mathrm{H}_{2} \mathrm{~S}\right)$ \\
\hline
\end{tabular}
\end{table}

The ePC-SAFT model can predict CO2 absorption well in the limit of low partial pressures. Although the overall AAD was $69.67 \%$, this is likely attributable, in part, to scattering in the experimental data due to the sensitivity required to measure very low loading regimes. Considering the partial pressure of $\mathrm{CO}_{2}$ varies by several orders of magnitude, the results are satisfactory. More importantly, the transition from chemical to physical absorption - represented by the non-power law behaviour at $\mathrm{CO}_{2}$ loadings $>0.8 \mathrm{mol} \mathrm{CO}_{2} / \mathrm{mol}$ MDEA (Figure 8) - is accurately predicted by the model.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-13.jpg?height=1000&width=1412&top_left_y=632&top_left_x=299}
\captionsetup{labelformat=empty}
\caption{Figure 9. Experimental [64] and predicted $\mathrm{CO}_{2}$ partial pressures as a function of $\mathrm{CO}_{2}$ loading for $w_{\text {MDEA }}$ of $0.05,0.205,0.5$, and 0.75 at temperatures of 323 K (circle), 348 K (square), and 373 K (triangle). Overall AAD $=65.47 \%$.}
\end{figure}

Finally, the experimental data of Rho et al.[64] was used to evaluate model performance over a broad range of MDEA mass fractions, presented in Figure 9. Model performance under these conditions reciprocate observations from Figure 7 and Figure 8: (1) ePC-SAFT overestimates the solubility of $\mathrm{CO}_{2}$ in the low loading range; (2) results compare more favourably at higher loadings / partial pressures; and (3) better modelling results are obtained at lower MDEA weight fractions. It is evident that the model output significantly deviates in $w_{\text {MDEA }}=0.75$ solutions, whereby the solubility of $\mathrm{CO}_{2}$ is systematically overestimated for every absorption isotherm. The net effect of such a discrepancy increases the total AAD from $44.89 \%$ (for $w_{M D E A}=0.05,0.205,0.5$ ) to $65.47 \%$ (for $w_{M D E A}=0.05,0.205,0.5,0.75$ ). Nevertheless, for $w_{\text {MDEA }} \leq 0.5$, the total AAD is quantitatively comparable to those reported from Figure 7, and the qualitative trends are corroborated quite reasonably.
Directly comparing the modelling results in Figure 7 to the works of Uyan et al. [29] and Wangler et al. [32] demonstrates that a similar modelling performance can be obtained in the ePC-SAFT framework, even in the absence of several additional temperature-dependent interaction parameters. For the experimental data of Kuranov et al. [61], the AAD of 20.26\% in this work is only marginally less accurate than the results of both Uyan et al. [29] and Wangler et al. [32], who obtain an AAD of $19.22 \%$ and $19.44 \%$, respectively. The results for $w_{\text {MDEA }}=0.489$ solution are somewhat dissimilar to those reported by Wangler et al. [32], who obtain an AAD of $34.96 \%$ for the 313 K and 353 K absorption isotherms compared to an AAD of $43.28 \%$ reported here if only the 313 K and 353 K isotherms are considered. Good agreement between the modelling results obtained in this work and those reported by Uyan et al.
[29] and Wangler et al. [32] is a particularly important outcome of this analysis, as it highlights that accurate modelling of MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ VLE in industrially relevant operating conditions can be achieved in the ePC-SAFT framework, even without incorporating temperature-dependent interaction parameters, so long as the relevant binary subsystems are well described. More generally, there have been many EoS approaches proposed in the literature to model MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ systems outside the SAFT formalism. In most cases reported in the literature [15,65,75-78], model parameters were regressed against ternary experimental data in order to give a reasonable system description. Treatment in this way is considered correlative rather than predictive and emphasises the validity in applying ePC-SAFT as a predictive model while simultaneously achieving comparable (albeit less accurate) modelling results for $\mathrm{CO}_{2}$ absorption in aqueous MDEA.
Enthalpy of absorption in the ePC-SAFT model was compared to the experimental data of Arcis [68] for $w_{\text {MDEA }}=0.3$ at 323 K and Mathonat [69] for $w_{\text {MDEA }}=0.3$ at 353 K and 393 K , shown in Figure 10. There is some disagreement between the model and experimental observation, with an overall AAD of $19.73 \%$ likely due to predicted speciation differing somewhat from real systems. Experimental trends are captured quite well; the model predicts a decrease in $\Delta h^{a b s}$ with acid-gas loading, in a manner comparable with the experimental data.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-14.jpg?height=1128&width=769&top_left_y=995&top_left_x=680}
\captionsetup{labelformat=empty}
\caption{Figure 10. Enthalpy of absorption per mole $\mathrm{CO}_{2}$ in $w_{\text {MDEA }}=0.3$ solution at $323 \mathrm{~K}, 353 \mathrm{~K}$, and 393 K . Differential enthalpy of absorption modelling results given by solid lines. Experimental data of Arcis [68] $(323 \mathrm{~K})$ and Mathonat [69] ( 353 K and 393 K ) given by symbols. AAD $=19.73 \%$.}
\end{figure}

Zhang and Chen [65] and Kim et al. [41] remark that MDEAH ${ }^{+}$dissociation, and to a lesser extent, $\mathrm{CO}_{2}$ dissociation dominate in the overall enthalpy of $\mathrm{CO}_{2}$ absorption. The speciation results in Figure 6 show good agreement for MDEAH ${ }^{+}$over the whole $\mathrm{CO}_{2}$ loading range, suggesting that the deviations in absorption enthalpy are due to $\mathrm{CO}_{2}$ reaction products. Recent works by Wangler et al. [32] with ePCSAFT and Alkhatib et al. [33] with soft-SAFT have shown good agreement with experimental enthalpy of absorption in the same system. However, in both cases temperature dependent correlations were used for $\mathrm{CO}_{2}$ interactions.

\subsection*{3.3.3. MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$}

Absorption of $\mathrm{H}_{2} \mathrm{~S}$ in aqueous MDEA occurs through a combination of physical and chemical processes, analogous to that of $\mathrm{CO}_{2}$. In the absence of reliable speciation data for this system, Figure 11 shows the species distribution in a MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$ system at 313 K in $w_{\text {MDEA }}=0.5$ solution predicted by the ePC-SAFT model. The results are similar to those reported by Posey et al. [79] using an e-NRTL model.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-15.jpg?height=686&width=819&top_left_y=607&top_left_x=584}
\captionsetup{labelformat=empty}
\caption{Figure 11. Liquid phase speciation in a ternary MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$ system at 313 K for $w_{\text {MDEA }}=0.5$. Model results are obtained using equilibrium constants reported in Table 1 and molecular and binary parameters reported in Table 2. Solid lines represent results obtained by considering species activity coefficients in solving the chemical equilibrium problem.}
\end{figure}

Figure 12 compares ePC-SAFT predictions for $\mathrm{H}_{2} \mathrm{~S}$ solubility in $w_{\text {MDEA }}=0.189$ and $w_{\text {MDEA }}=0.489$ aqueous MDEA solutions in the temperature range of $313 \mathrm{~K}-413 \mathrm{~K}$ and up to $\mathrm{H}_{2} \mathrm{~S}$ loadings of 1.8 mol $\mathrm{H}_{2} \mathrm{~S} / \mathrm{mol}$ MDEA based on the experimental data of Kuranov et al.[61] and Kamps et al.[62]. ePC-SAFT predicts $\mathrm{H}_{2} \mathrm{~S}$ solubilities with better accuracy in lower MDEA weight fraction solutions, similar to the performance observed for $\mathrm{CO}_{2}$ absorption. Concomitantly, the model performs better at higher temperatures, aligning with the trends observed in MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ systems. Particularly in the $w_{\text {MDEA }}=0.489$ solution, $\mathrm{H}_{2} \mathrm{~S}$ solubility is underestimated in the low loading regime. Under these conditions, the association behaviour of MDEAH ${ }^{+}$becomes more important [29] and the influence of relative permittivity is more pronounced. Model results could potentially be improved in the low loading regime by considering MDEAH ${ }^{+}$as a cross-associating ion with $\varepsilon^{A B} / k_{B}=0 \mathrm{~K}$ and $\kappa^{A B} \neq 0$.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-16.jpg?height=716&width=1489&top_left_y=246&top_left_x=280}
\captionsetup{labelformat=empty}
\caption{Figure 12. Isothermal VLE of ternary MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$ system at different temperatures in a $w_{\text {MDEA }} =0.189$ aqueous solution (Left Panel) and $w_{\text {MDEA }}=0.489$ aqueous solution (Right Panel). ePC-SAFT modelling results obtained using the molecular and binary interaction parameters reported in Table 2. Symbols represent the experimental data of Kuranov et al. $[61]\left(w_{\text {MDEA }}=0.189\right)$ AAD $=18.61 \%$ and Kamps et al.[62] $\left(w_{\text {MDEA }}=0.489\right)$ AAD $=37.38 \%$.}
\end{figure}

Enthalpies of absorption for $\mathrm{H}_{2} \mathrm{~S}$ in aqueous MDEA are compared against to the experimental data of Oscarson and Izatt [70] in Figure 13.The overall AAD of 75.61\% obtained for $\mathrm{H}_{2} \mathrm{~S}$ absorption is not comparable to the AAD of $27.36 \%$ reported by Wangler et al. [32]. Other models proposed in the literature for MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{H}_{2} \mathrm{~S}$ systems $[15,60,75,78]$ report AADs for $w_{\text {MDEA }}<0.5$ in a similar range as the results in Wangler et al. [32], with Sadegh et al. [18] finding somewhat better agreement (AAD =

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-16.jpg?height=931&width=686&top_left_y=1553&top_left_x=614}
\captionsetup{labelformat=empty}
\caption{Figure 13. Enthalpy of absorption per mole $\mathrm{H}_{2} \mathrm{~S}$ in $w_{\text {MDEA }}=0.489$ solution at $300 \mathrm{~K}, 350 \mathrm{~K}$, and 400 K . Differential enthalpy of absorption modelling results given by solid lines. Experimental data of Oscarson and Izatt [70] given by symbols. AAD = 75.61\%.}
\end{figure}

12\% alebit with a different approach, that requires regression against experimental data for the ternary system.
While $\Delta h^{a b s}$ is overestimated for all three isotherms, the model shows the correct trend as a function of loading. Recent results by Alkhatib et al. [33] using soft-SAFT for $\mathrm{H}_{2} \mathrm{~S}$ absorption in less concentrated aqueous MDEA systems show even better agreement with experimental sources, although a temperature-correlated $\mathrm{H}_{2} \mathrm{~S}$ - MDEA interaction parameter was applied.

\subsection*{3.4. Quaternary Systems}

\subsection*{3.4.1. MDEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{CH}_{4}$}

Mixed gas absorption of $\mathrm{CO}_{2}$ and $\mathrm{CH}_{4}$ is of special interest in the context of gas sweetening operations, with the added objective of minimizing loss of light hydrocarbons. Model predictions for mixed gas solubility are presented in Figure 14, with comparison to the experimental data of Addicks and Owren [80]. Initial system composition was set to that of Addicks and Owren [80] with the two phases subsequently allowed to equilibrate. For $\mathrm{CO}_{2}$ we see similar performance as for unary gas absorption, with ePC-SAFT predictions losing accuracy at high loading. We obtain AADs $32.90 \%$ and $48.63 \%$ for $w_{\text {MDEA }}=0.3$ and $w_{\text {MDEA }}=0.5$ solutions, respectively. Greater discrepancies are observed for $\mathrm{CH}_{4}$ solubility: while the model agrees at least qualitatively with experimental data for $w_{\text {MDEA }}=0.3$ and $w_{\text {MDEA }}=0.5$ at 353 K , we see a strange behaviour in vapour pressure at 313 K in $w_{\text {MDEA }}=0.5$ solution.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-18.jpg?height=1192&width=1218&top_left_y=296&top_left_x=370}
\captionsetup{labelformat=empty}
\caption{Figure 14. Isothermal VLE for a quaternary MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{CH}_{4}$ system at different temperatures and MDEA weight fractions. (Top Left) CO2 partial pressures over $w_{\text {MDEA }}=0.3$ solution; AAD $=32.9 \%$. (Top Right) $\mathrm{CO}_{2}$ partial pressures over $w_{\text {MDEA }}=0.5$ solution; AAD = $48.63 \%$. (Bottom Left) $\mathrm{CH}_{4}$ partial pressures over $w_{\text {MDEA }}=0.3$ solution; AAD $=62.4 \%$. (Bottom Right) $\mathrm{CH}_{4}$ partial pressures over $w_{\text {MDEA }}=0.5$ solution; AAD $=79.72 \%$. ePC-SAFT modelling results given by solid lines. Experimental data of Addicks et al. [80] given by symbols.}
\end{figure}

However, as shown in Figure 15, $\mathrm{CH}_{4}$ solubility is predicted with good accuracy for the binary MDEA $\mathrm{CH}_{4}$ system. We obtain an overall AAD of $45.73 \%$ compared against the experimental data of Jou and Mather [81], with correct prediction of the unusually weak temperature dependence of this system.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-19.jpg?height=739&width=748&top_left_y=283&top_left_x=603}
\captionsetup{labelformat=empty}
\caption{Figure 15. Isothermal P-x-y experimental VLE data from Jou and Mather[81] and modelling results of MDEA - $\mathrm{CH}_{4}$ at different temperatures using molecular parameters reported in Table 2 and $k_{M D E A-C H_{4}}=0 . \mathrm{AAD}=45.73 \%$.}
\end{figure}

\subsection*{3.4.2. MDEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$}

Competitive absorption of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ in aqueous MDEA originates primarily from the limited reactive loading capacity of amines. However, as can be seen from Figure 6 and Figure 13 both physical and reactive absorption mechanisms are significant, particularly at high partial pressures. An accurate model must capture both absorption regimes for each individual species, as well as competitive effects in the quaternary systems. The predictive power of ePC-SAFT is demonstrated for competitive absorption of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ by comparison with experimental data from Dicko et al. [71] in Figure 16. We obtain AADs of $57.18 \%$ and $79.32 \%$ for partial pressures of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$, respectively. This indicates the quaternary case has less predictive power as for ternary subsystems, although the deviation is not markedly dissimilar to e.g. $\mathrm{CO}_{2}$ solvation in $w_{\text {MDEA }} \geq 0.5$ solutions. The model predictions reciprocate the experimental co-dependence of acid-gas partial pressures: since MDEA reacts with both $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$, increasing loading of one concomitantly increases the partial pressure of the other species. However, the model tends to underestimate the solubility of both $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ in solution compared to the experimental data of Dicko et al.[71].

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-20.jpg?height=794&width=1587&top_left_y=278&top_left_x=230}
\captionsetup{labelformat=empty}
\caption{Figure 16. $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ partial pressures in a quaternary MDEA $-\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$ system for $w_{\text {MDEA }}=0.5$ at 323 K and fixed $\mathrm{H}_{2} \mathrm{~S}$ (Left Panel) and $\mathrm{CO}_{2}$ loadings (Right Panel) of 0.1, 0.3, 0.5 , and $0.8 \mathrm{~mol} / \mathrm{mol}$ MDEA. Solid lines represent modelling results, symbols represent data of Dicko et al.[71] AAD $=57.18 \%$ (Left Panel) and AAD $=79.32 \%$ (Right panel).}
\end{figure}

By extending the experimental database beyond the results of Dicko et al.[71], the ePC-SAFT model can be assessed across a wider range of conditions. To this end, we compare against the experimental data of Haghtalab and Izadi,[72] Jou et al.,[73] and Jou et al.[74] using the same approach. The results are compared by means of a parity plot in Figure 17. It is evident that not all experimental VLE data can be closely reproduced. While this may in part be attributed to inconsistency between experimental sources, there is a clear deterioration of ePC-SAFT model performance at high MDEA weight fractions.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/5a092fb5-6a3e-4db1-ae2c-7d3531348544-20.jpg?height=655&width=1671&top_left_y=1596&top_left_x=244}
\captionsetup{labelformat=empty}
\caption{Figure 17. Parity plots for $\mathrm{CO}_{2}$ partial pressures (left) and $\mathrm{H}_{2} \mathrm{~S}$ partial pressures (right) in a quaternary MDEA - $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$ system. ePC-SAFT model predictions plotted against experimental data of Haghtalab and Izadi [72], Jou et al.[73], and Jou et al.[74]. Solid line: $\mathrm{P}_{\mathrm{CO}_{2}}^{\text {calc }}=\mathrm{P}_{\mathrm{CO}_{2}}^{\text {exp }}$, dashed lines: $\mathrm{P}_{\mathrm{CO}_{2}}^{\text {calc }}= \mp 1.5 \mathrm{P}_{\mathrm{CO}_{2}}^{\exp }$}
\end{figure}

\section*{4. Conclusions}

Mixed acid gas absorption in aqueous MDEA has been shown to be well represented by the ePC-SAFT EoS by leveraging the flexibility of the native thermodynamic framework without resorting to temperature-dependent interaction parameters. By carefully considering binary systems in turn, a compatible set of models was developed for solvent, solute, and electrolyte species. Model performance in binary systems readily extended to ternary and quaternary cases, with preferential uptake of $\mathrm{H}_{2} \mathrm{~S}$ correctly predicted for competitive acid gas absorption.
As seen for both $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$, ePC-SAFT performed well for low-MDEA content systems but deteriorated as organic weight fraction increased. There are several likely sources for this behaviour. Firstly, we do not consider binary parameters for physical absorption of acid gases in MDEA, as physical and reactive absorption cannot readily be distinguished experimentally. Secondly, electrolyte reaction products may be poorly represented in terms of their ePC-SAFT parameters: in particular representation of MDEAH ${ }^{+}$as a single-segment species may alter fluid properties in an adverse manner. Third, the electrolyte contribution $a_{i o n}$ is likely incorrectly represented as the liquid composition strays further from aqueous solution, as the assumption of water-like electrostatic continuum worsens for both ion solvation and Debye-Hückel energies.
While the reliance on empirical correlations of solvent permittivity is a shortcoming of ePC-SAFT for mixed solvent systems, results for low organic weight fraction systems compare overall very well to experimental values. Model prediction AADs were often found to be in the range of scattering between experimental sources.

\section*{References}
[1] S. Mitra, A technical report on gas sweetening by amines, 2015. https://doi.org/10.13140/RG.2.1.2061.9360.
[2] G. Pipitone, O. Bolland, Power generation with CO2 capture: Technology for CO2 purification, Int. J. Greenh. Gas Control. 3 (2009) 528-534. https://doi.org/10.1016/j.ijggc.2009.03.001.
[3] A. de C. Reis, J.L. de Medeiros, G.C. Nunes, O. de Q.F. Araújo, Upgrading of natural gas ultra-rich in carbon dioxide: Optimal arrangement of membrane skids and polishing with chemical absorption, J. Clean. Prod. 165 (2017) 1013-1024. https://doi.org/10.1016/j.jclepro.2017.07.198.
[4] C. Azar, K. Lindgren, M. Obersteiner, K. Riahi, D.P. van Vuuren, K.M.G.J. den Elzen, K. Möllersten, E.D. Larson, The feasibility of low CO2concentration targets and the role of bioenergy with carbon capture and storage (BECCS), Clim. Change. 100 (2010) 195-202. https://doi.org/10.1007/s10584-010-9832-7.
[5] C. Song, X. Ma, Desulfurization Technologies, in: K. Liu, C. Song, V. Subramani (Eds.), Hydrog. Syngas Prod. Purif. Technol., John Wiley \& Sons, Inc., Hoboken, NJ, 2009: pp. 219225. https://doi.org/10.1002/9780470561256.
[6] D. Bose, Design parameters for a hydro desulfurization (HDS) unit for petroleum naphtha at 3500 barrels per day, World Sci. News. 9 (2015) 99-111.
[7] X. Fan, Mtigation Technologies, in: A.K. Gupta, J. Yan (Eds.), Handb. Clean Energy Syst., John Wiley \& Sons, Ltd, Chichester, UK, 2015: pp. 1-30. https://doi.org/10.1002/9781118991978.hces024.
[8] U. Desideri, Advanced absorption processes and technology for carbon dioxide (CO2 ) capture in power plants, in: M.M. Maroto Valer (Ed.), Dev. Innov. Carbon Dioxide Capture Storage Technol., Woodhead Publishing Limited, Oxford, UK, Cambidge, UK, New Delhi, IN, 2010: pp. 155-182. https://doi.org/10.1533/9781845699574.2.155.
[9] G.T. Rochelle, Amine scrubbing for CO2 capture, Science. 325 (2009) 1652-1655. https://doi.org/10.1126/science.1176731.
[10] M.W. Arshad, P.L. Fosbøl, N. Von Solms, H.F. Svendsen, K. Thomsen, Equilibrium solubility of CO2in alkanolamines, Energy Procedia. 51 (2014) 217-223. https://doi.org/10.1016/j.egypro.2014.07.025.
[11] D. Tong, J.P.M. Trusler, G.C. Maitland, J. Gibbins, P.S. Fennell, Solubility of carbon dioxide in aqueous solution of monoethanolamine or 2-amino-2-methyl-1-propanol: Experimental measurements and modelling, Int. J. Greenh. Gas Control. 6 (2012) 37-47. https://doi.org/10.1016/j.ijggc.2011.11.005.
[12] J.F.J. Zemaitis, D.M. Clark, M. Rafal, N.C. Scrivner, Handbook of aqueous electrolyte thermodynamics : theory \& application, John Wiley \& Sons, Inc., Hoboken, NJ, 1986.
[13] J.O. Valderrama, The State of the Cubic Equations of State, Ind. Eng. Chem. Res. 42 (2003) 1603-1618. https://doi.org/10.1021/ie020447b.
[14] J.M. Prausnitz, R.N. Lichtenthaler, E. Gomes de Azevedo, Molecular thermodynamics of fluidphase equilibria, 3rd ed., Prentice-Hall PTR, Englewood Cliffs, NJ, 1998.
[15] A. Barreau, E. Blanchon le Bouhelec, K.N. Habchi Tounsi, P. Mougin, F. Lecomte, Absorption of H 2 S and CO 2 in alkanolamine aqueous solution: Experimental data and modelling with the electrolyte-NRTL model, Oil Gas Sci. Technol. - Rev. IFP. 61 (2006) 345-361. https://doi.org/10.2516/ogst:2006038a.
[16] Y. Zhang, C.C. Chen, Thermodynamic modeling for CO 2 absorption in aqueous MEA solution with electrolyte NRTL model, Ind. Eng. Chem. Res. 50 (2011) 163-175. https://doi.org/10.1021/ie1006855.
[17] J.R. Loehe, M.D. Donohue, Recent Advances in Modeling Thermodynamic Properties of Aqueous Strong Electrolyte Systems, AIChE J. 43 (1997) 180-195. https://doi.org/10.1002/aic.690430121.
[18] N. Sadegh, E.H. Stenby, K. Thomsen, Thermodynamic modeling of hydrogen sulfide absorption by aqueous N-methyldiethanolamine using the Extended UNIQUAC model, Fluid Phase Equilib. 392 (2015) 24-32. https://doi.org/10.1016/j.fluid.2015.01.024.
[19] N. Sadegh, E.H. Stenby, K. Thomsen, Thermodynamic modelling of acid gas removal from
natural gas using the Extended UNIQUAC model, Fluid Phase Equilib. 442 (2017) 38-43. https://doi.org/10.1016/j.fluid.2017.02.020.
[20] W.G. Chapman, K.E. Gubbins, G. Jackson, M. Radosz, New reference equation of state for associating liquids, Ind. Eng. Chem. Res. 29 (1990) 1709-1721. https://doi.org/10.1021/ie00104a021.
[21] W.G. Chapman, K.E. Gubbins, G. Jackson, M. Radosz, SAFT: Equation-of-state solution model for associating fluids, Fluid Phase Equilib. 52 (1989) 31-38. https://doi.org/10.1016/0378-3812(89)80308-5.
[22] S.H. Huang, M. Radosz, Equation of state for small, large, polydisperse, and associating molecules: extension to fluid mixtures, Ind. Eng. Chem. Res. 30 (1991) 1994-2005. https://doi.org/10.1021/ie00056a050.
[23] S.H. Huang, M. Radosz, Equation of state for small, large, polydisperse, and associating molecules, Ind. Eng. Chem. Res. 29 (1990) 2284-2294. https://doi.org/10.1021/ie00107a014.
[24] J.. Button, K.. Gubbins, SAFT prediction of vapour-liquid equilibria of mixtures containing carbon dioxide and aqueous monoethanolamine or diethanolamine, Fluid Phase Equilib. 158160 (1999) 175-181. https://doi.org/10.1016/S0378-3812(99)00150-8.
[25] K. Nasrifar, A.H. Tafazzol, Vapor- liquid equilibria of acid gas- aqueous ethanolamine solutions using the PC-SAFT equation of state, Ind. Eng. Chem. Res. 49 (2010) 7620-7630. https://doi.org/10.1021/ie901181n.
[26] J. Gross, G. Sadowski, Perturbed-Chain SAFT: an equation of state based on a perturbation theory for chain molecules, Ind. Eng. Chem. Res. 40 (2001) 1244-1260. https://doi.org/10.1021/ie0003887.
[27] J. Gross, G. Sadowski, Application of the perturbed-chain SAFT equation of state to associating systems, Ind. Eng. Chem. Res. 41 (2002) 5510-5515. https://doi.org/10.1021/ie010954d.
[28] H. Pahlavanzadeh, S. Fakouri Baygi, Modeling CO2 solubility in aqueous methyldiethanolamine solutions by perturbed Chain-SAFT equation of state, J. Chem. Thermodyn. 59 (2013) 214-221. https://doi.org/10.1016/j.jct.2012.12.021.
[29] M. Uyan, G. Sieder, T. Ingram, C. Held, Predicting CO2 solubility in aqueous Nmethyldiethanolamine solutions with ePC-SAFT, Fluid Phase Equilib. 393 (2015) 91-100. https://doi.org/10.1016/j.fluid.2015.02.026.
[30] C. Held, L.F. Cameretti, G. Sadowski, Modeling aqueous electrolyte solutions: Part 1. Fully dissociated electrolytes, Fluid Phase Equilib. 270 (2008) 87-96. https://doi.org/10.1016/J.FLUID.2008.06.010.
[31] C. Held, T. Reschke, S. Mohammad, A. Luza, G. Sadowski, ePC-SAFT revised, Chem. Eng. Res. Des. 92 (2014) 2884-2897. https://doi.org/10.1016/j.cherd.2014.05.017.
[32] A. Wangler, G. Sieder, T. Ingram, M. Heilig, C. Held, Prediction of CO2 and H2S solubility and enthalpy of absorption in reacting N-methyldiethanolamine / water systems with ePC-SAFT, Fluid Phase Equilib. 461 (2018) 15-27. https://doi.org/10.1016/j.fluid.2017.12.033.
[33] I.I.I. Alkhatib, L.M.C. Pereira, L.F. Vega, Accurate Modeling of the Simultaneous Absorption of H2S and CO2 in Aqueous Amine Solvents, Ind. Eng. Chem. Res. 58 (2019) 6870-6886. https://doi.org/10.1021/acs.iecr.9b00862.
[34] J.P. Wolbach, S.I. Sandler, Using molecular orbital calculations to describe the phase behavior of cross-associating mixtures, Ind. Eng. Chem. Res. 37 (1998) 2917-2928. https://doi.org/10.1021/ie970781I.
[35] L.F. Cameretti, G. Sadowski, J.M. Mollerup, Modeling of aqueous electrolyte solutions with perturbed-chain statistical associated fluid theory, Ind. Eng. Chem. Res. 44 (2005) 3355-3362. https://doi.org/10.1021/ie0488142.
[36] G.M. Kontogeorgis, B. Maribo-Mogensen, K. Thomsen, The Debye-Hückel theory and its importance in modeling electrolyte solutions, Fluid Phase Equilib. 462 (2018) 130-152. https://doi.org/10.1016/j.fluid.2018.01.004.
[37] W.B. Floriano, M.A.C. Nascimento, Dielectric constant and density of water as a function of pressure at constant temperature, Brazilian J. Phys. 34 (2004) 38-41.
https://doi.org/10.1590/S0103-97332004000100006.
[38] K.A. Dill, S. Bromberg, Molecular Driving Forces: Statistical Thermodynamics in Biology, Chemistry, Physics, and Nanoscience, 2nd ed., Garland Science, London, UK, New York, NY, 2010.
[39] H. Scott Fogler, Elements of Chemical Reaction Engineering, 4th ed., Prentice Hall PTR, Upper Saddle, NJ, 2005.
[40] D.M. Austgen, G.T. Rochelle, C.C. Chen, Model of vapor-liquid equilibria for aqueous acid gas-alkanolamine systems. 2. Representation of H2S and CO2 solubility in aqueous MDEA and CO2 solubility in aqueous mixtures of MDEA with MEA or DEA, Ind. Eng. Chem. Res. 30 (1991) 543-555. https://doi.org/10.1021/ie00051a016.
[41] I. Kim, K.A. Hoff, E.T. Hessen, T. Haug-Warberg, H.F. Svendsen, Enthalpy of absorption of CO 2 with alkanolamine solutions predicted from reaction equilibrium constants, Chem. Eng. Sci. 64 (2009) 2027-2038. https://doi.org/10.1016/j.ces.2008.12.037.
[42] P.M. Mathias, J.P. O'Connell, The Gibbs-Helmholtz equation and the thermodynamic consistency of chemical absorption data, Ind. Eng. Chem. Res. 51 (2012) 5090-5097. https://doi.org/10.1021/ie202668k.
[43] N. Mac Dowell, F. Llovell, C.S. Adjiman, G. Jackson, A. Galindo, Modeling the fluid phase behavior of carbon dioxide in aqueous solutions of monoethanolamine using transferable parameters with the SAFT-VR approach, Ind. Eng. Chem. Res. 49 (2010) 1883-1899. https://doi.org/10.1021/ie901014t.
[44] R.M. Ojeda, F. Llovell, Soft-SAFT transferable molecular models for the description of gas solubility in eutectic ammonium salt-based solvents, J. Chem. Eng. Data. 63 (2018) 25992612. https://doi.org/10.1021/acs.jced.7b01103.
[45] A.S. Avlund, G.M. Kontogeorgis, M.L. Michelsen, Modeling systems containing alkanolamines with the CPA equation of state, Ind. Eng. Chem. Res. 47 (2008) 7441-7446. https://doi.org/10.1021/ie800040g.
[46] O. Noll, A. Valtz, D. Richon, T. Getachew-Sawaya, I. Mokbel, J. Jose, Vapor pressures and liquid densities of N-methylethanolamine, diethanolamine, and N-methyldiethanolamine, ELDATA Int. Electron. J. Phys. Chem. Data. 4 (1998) 105-120.
[47] J. Manuel Bernal-García, M. Ramos-Estrada, G.A. Iglesias-Silva, K.R. Hall, Densities and excess molar volumes of aqueous solutions of n-methyldiethanolamine (MDEA) at temperatures from (283.15 to 363.15) K, J. Chem. Eng. Data. 48 (2003) 1442-1445. https://doi.org/10.1021/je030120x.
[48] C. McCabe, A. Galindo, SAFT Associating Fluids and Fluid Mixtures, in: A.R. Goodwin, J. Sengers, C.J. Peters (Eds.), Appl. Thermodyn. Fluids, RSC Publishing, Wellington, FL, 2010: pp. 215-279. https://doi.org/10.1039/9781849730983-00215.
[49] N.I. Diamantonis, I.G. Economou, Evaluation of statistical associating fluid theory (SAFT) and perturbed chain-SAFT equations of state for the calculation of thermodynamic derivative properties of fluids related to carbon capture and sequestration, Energy \& Fuels. 25 (2011) 3334-3343. https://doi.org/10.1021/ef200387p.
[50] N.I. Diamantonis, I.G. Economou, Modeling the phase equilibria of a $\mathrm{H} 2 \mathrm{O}-\mathrm{CO} 2$ mixture with PC-SAFT and tPC-PSAFT equations of state, Mol. Phys. 110 (2012) 1205-1212. https://doi.org/10.1080/00268976.2012.656721.
[51] I. Kim, H.F. Svendsen, E. Børresen, Ebulliometric determination of vapor - liquid equilibria for pure water , monoethanolamine, N -methyldiethanolamine, 3-( methylamino)-propylamine, and their binary and ternary solutions, J. Chem. Eng. Data. 53 (2008) 2521-2531. https://doi.org/10.1021/je800290k.
[52] Y. Danten, T. Tassaing, M. Besnard, Ab initio investigation of vibrational spectra of water(CO2)n complexes ( $\mathrm{n}=1,2$ ), 109 (2005) 3250-3256. https://doi.org/10.1021/jp0503819.
[53] A. Valtz, A. Chapoy, C. Coquelet, P. Paricaud, D. Richon, Vapour-liquid equilibria in the carbon dioxide-water system, measurement and modelling from 278.2 to 318.2 K, Fluid Phase Equilib. 226 (2004) 333-344. https://doi.org/10.1016/j.fluid.2004.10.013.
[54] I. Dalmolin, E. Skovroinski, A. Biasi, M.L. Corazza, C. Dariva, J.V. Oliveira, Solubility of carbon dioxide in binary and ternary mixtures with ethanol and water, Fluid Phase Equilib. 245 (2006) 193-200. https://doi.org/10.1016/j.fluid.2006.04.017.
[55] F.-Y. Jou, J.J. Carroll, A.E. Mather, F.D. Otto, Solubility of methane and ethane in aqueous solutions of methyldiethanolamine, J. Chem. Eng. Data. 43 (1998) 781-784. https://doi.org/10.1021/je980003f.
[56] K.A.G. Schmidt, F.Y. Jou, A.E. Mather, Solubility of methane in an aqueous methyldiethanolamine solution (mass fraction 50 \%), J. Chem. Eng. Data. 53 (2008) 17251727. https://doi.org/10.1021/je700734p.
[57] J.P. Jakobsen, J. Krane, H.F. Svendsen, Liquid-phase composition determination in CO2-H2O-alkanolamine systems: an NMR study, Ind. Eng. Chem. Res. 44 (2005) 9894-9903. https://doi.org/10.1021/ie048813+.
[58] P.W.J. Derks, P.J.G. Huttenhuis, C. Van Aken, J. Marsman, G.F. Versteeg, Determination of the liquid-phase speciation in the MDEA-H2O-CO2 system, Energy Procedia. 4 (2011) 599605. https://doi.org/10.1016/j.egypro.2011.01.094.
[59] DECHEMA, Information Systems and Databases, (2019).
[60] L. Chunxi, W. Fürst, Representation of CO2 and H2S solubility in aqueous MDEA solutions using an electrolyte equation of state, Chem. Eng. Sci. 55 (2000) 2975-2988. https://doi.org/10.1016/S0009-2509(99)00550-3.
[61] G. Kuranov, B. Rumpf, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of N -methyldiethanolamine in the temperature range $313-413 \mathrm{~K}$ at pressures up to 5 MPa , Ind. Eng. Chem. Res. 35 (1996) 1959-1966. https://doi.org/10.1021/ie950538r.
[62] Á.P.-S. Kamps, A. Balaban, M. Jödecke, G. Kuranov, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of N methyldiethanolamine at temperatures from 313 to 393 K and pressures up to 7.6 MPa : new experimental data and model extension, Ind. Eng. Chem. Res. 40 (2001) 696-706. https://doi.org/10.1021/ie000441r.
[63] S. Huang, H. Ng, Solubility of H2S and CO2 in alkanolamines, Gas Processor Association, Tulsa, OK, 1998.
[64] S.-W. Rho, K.-P. Yoo, J.S. Lee, S.C. Nam, J.E. Son, B.-M.M. Min, Solubility of CO2 in aqueous methyldiethanolamine solutions, J. Chem. Eng. Data. 2 (1997) 1161-1164. https://doi.org/10.1021/je970097d.
[65] Y. Zhang, C.-C. Chen, Thermodynamic modeling for CO2 absorption in aqueous MDEA solution with electrolyte NRTL model, Ind. Eng. Chem. Res. 50 (2011) 163-175. https://doi.org/10.1021/ie1006855.
[66] R.T.J. Porter, M. Fairweather, C. Kolster, N. Mac Dowell, N. Shah, R.M. Woolley, Cost and performance of some carbon capture technology options for producing different quality CO2 product streams, Int. J. Greenh. Gas Control. 57 (2017) 185-195. https://doi.org/10.1016/j.ijggc.2016.11.020.
[67] J. Kittel, E. Fleury, B. Vuillemin, S. Gonzalez, F. Ropital, R. Oltra, Corrosion in alkanolamine used for acid gas removal: from natural gas processing to CO2 capture, Mater. Corros. 63 (2012) 223-230. https://doi.org/10.1002/maco.201005847.
[68] H. Arcis, Etude thermodynamique de la dissolution du dioxyde de carbone dans des solutions aqueuses d'alcanolamines, U.F.R Sciences et Technologies. PhD Dissertation, 2008.
[69] C. Mathonat, Calorimétrie de mélange, à écoulement, à températures et pressions élevées. Application à l'étude de l'élimination du dioxyde de carbone à l'aide de solutions aqueuses d'alcanolamines, Blaise Pascal University, Cermont-Fernand II. PhD. Dissertation, 1995.
[70] J. Oscarson, R. Izatt, Enthalpies of solution of H2S in aqueous methyldiethanolamine solutions, GPA Researc Report, 1990.
[71] M. Dicko, C. Coquelet, C. Jarne, S. Northrop, D. Richon, Acid gases partial pressures above a $50 \mathrm{wt} \%$ aqueous methyldiethanolamine solution: Experimental work and modeling, Fluid Phase Equilib. 289 (2010) 99-109. https://doi.org/10.1016/j.fluid.2009.11.012.
[72] A. Haghtalab, A. Izadi, Fluid phase equilibria simultaneous measurement solubility of carbon dioxide + hydrogen sulfide into aqueous blends of alkanolamines at high pressure, Fluid Phase Equilib. 375 (2014) 181-190. https://doi.org/10.1016/j.fluid.2014.05.017.
[73] F.Y. Jou, J.J. Carroll, A.E. Mather, F.D. Otto, Solubility of mixtures of hydrogen sulfide and
carbon dioxide in aqueous N-methyldiethanolamine solutions, J. Chem. Eng. Data. 38 (1993) 75-77. https://doi.org/10.1021/je00009a018.
[74] F. Jou, F.D. Otto, A.E. Mather, The solubility of mixtures of H 2 S and CO 2 in an MDEA solution, Can. J. Chem. Eng. 75 (1997) 1-4. https://doi.org/10.1002/cjce.5450750618.
[75] T. Wang, E. El Ahmar, C. Coquelet, G.M. Kontogeorgis, Improvement of the PR-CPA equation of state for modelling of acid gases solubilities in aqueous alkanolamine solutions, Fluid Phase Equilib. 471 (2018) 74-87. https://doi.org/10.1016/j.fluid.2018.04.019.
[76] A.T. Zoghi, F. Feyzi, M.R. Dehghani, Modeling CO2 solubility in aqueous N methyldiethanolamine solution by electrolyte modified Peng - Robinson plus association equation of state, Ind. Eng. Chem. Res. 51 (2012) 9875-9885. https://doi.org/10.1021/ie2026053.
[77] P.J.G. Huttenhuis, N.J. Agrawal, E. Solbraa, G.F. Versteeg, The solubility of carbon dioxide in aqueous N-methyldiethanolamine solutions, Fluid Phase Equilib. 264 (2008) 99-112. https://doi.org/10.1016/j.fluid.2007.10.020.
[78] Y. Zhang, C.C. Chen, Modeling gas solubilities in the aqueous solution of methyldiethanolamine, Ind. Eng. Chem. Res. 50 (2011) 6436-6446. https://doi.org/10.1021/ie102150h.
[79] M.L. Posey, G.T. Rochelle, A thermodynamic model of methyldiethanolamine-CO2-H2 S-Water, Ind. Eng. Chem. Res. 36 (1997) 3944-3953. https://doi.org/10.1021/ie970140q.
[80] J. Addicks, G.A. Owren, A.O. Fredheim, K. Tangvik, Solubility of carbon dioxide and methane in aqueous methyldiethanolamine solutions, J. Chem. Eng. Data. 47 (2002) 855-860. https://doi.org/10.1021/je010292z.
[81] F.Y. Jou, A.E. Mather, Solubility of methane in methyldiethanolamine, J. Chem. Eng. Data. 51 (2006) 1429-1430. https://doi.org/10.1021/je060118g.
[82] J.I. Lee, A.E. Mather, Solubility of hydrogen sulfide in water, Berichte Der Bunsengesellschaft Für Phys. Chemie. 81 (1977) 1020-1023. https://doi.org/10.1002/bbpc.19770811029.
[83] S.X. Hou, G.C. Maitland, J.P.M. Trusler, Measurement and modeling of the phase behavior of the (carbon dioxide + water) mixture at temperatures from 298.15 K to 448.15 K , J. Supercrit. Fluids. 73 (2013) 87-96. https://doi.org/10.1016/j.supflu.2012.11.011.