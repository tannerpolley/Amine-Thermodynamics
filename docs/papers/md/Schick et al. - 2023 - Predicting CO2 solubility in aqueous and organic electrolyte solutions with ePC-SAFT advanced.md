\title{
Predicting $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions with ePC-SAFT advanced
}

\author{
Daniel Schick, Lena Bierhaus, Alexander Strangmann, Paul Figiel, Gabriele Sadowski, Christoph Held * \\ Laboratory of Thermodynamics, Department of Biochemical and Chemical Engineering, TU Dortmund, Emil-Figge Str. 70, 44277 Dortmund, Germany
}

\section*{A R T I C L E I N F O}

\section*{Keywords:}

CO2 solubility
Reactive vapor-liquid equilibria
Electrolyte thermodynamics
Thermodynamic modeling
Debye-Hückel

\begin{abstract}
Solvent influence and salt influence on $\mathrm{CO}_{2}$ solubility are essential factors toward the development of processes involving $\mathrm{CO}_{2}$ conversion. In this work, the equation of state (EOS) electrolyte Perturbed-Chain Statistical Associating Fluid Theory (ePC-SAFT advanced) was applied to model the $\mathrm{CO}_{2}$ solubility in single organic solvents (methanol, ethanol, $N$-methyl-2-pyrrolidone, dimethyl sulfoxide, tetrahydrofuran, dimethylformamide, $\gamma$-valerolactone, and acetonitrile). Further, $\mathrm{CO}_{2}$ solubility was predicted in aqueous solvent mixtures and in aqueous electrolyte solutions ( $\mathrm{NaCl}, \mathrm{KCl}, \mathrm{CsCl}, \mathrm{MgCl}_{2}, \mathrm{CaCl}_{2}, \mathrm{NaNO}_{3}, \mathrm{KNO}_{3}, \mathrm{Mg}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Ca}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Na}_{2} \mathrm{SO}_{4}, \mathrm{~K}_{2} \mathrm{SO}_{4}$, $\mathrm{MgSO}_{4}, \mathrm{NaHCO}_{3}$, and $\mathrm{K}_{2} \mathrm{CO}_{3}$ ) with water as single solvent as well as in aqueous alcoholic solvent mixtures. $\mathrm{CO}_{2}$ solubility in systems with a lack of data (CsCl) was measured in this work with a high-pressure variable-volume view cell. Broad ranges of temperatures, pressures, and high concentrations of electrolytes were considered, and solvent effects, ion effects, and $p H$ effects were studied. The nature of the considered systems required including dissociation reactions of carbonic acid in the modeling framework, most importantly for the systems containing carbonate salts. The results showed that i) $\mathrm{CO}_{2}$ solubility was the highest in non-polar solvents, ii) all salts caused salting-out effects on the $\mathrm{CO}_{2}$ solubility except carbonates (an apparent salting-in due to a pH shift), and that iii) the strength of salting-out effect was related to the charge density of the ions. The salt influence on $\mathrm{CO}_{2}$ solubility was predicted qualitatively correct with ePC-SAFT advanced; that is, fitting binary interaction parameters between ions and $\mathrm{CO}_{2}$ was not necessary, which is a result found for the first time. Finally, ePC-SAFT advanced allowed predicting the $\mathrm{CO}_{2}$ solubility in multi-component systems containing solvent mixtures, salt mixtures, or a solvent mixture with an additional salt over a broad range of conditions in good agreement with available literature data.
\end{abstract}

\section*{1. Introduction}

Modeling and predicting gas solubility in aqueous and organic electrolyte solutions is of special interest in both, industrial processes and academic research. However, the experimental effort in measuring gas solubility is very expansive considering the huge amount of system conditions, e.g., different temperatures and pressures, kind, and concentration of electrolytes. Therefore, a predictive thermodynamic model is desired that allows for the reduction of experimental effort to a minimum extent. Several equations of state (EOS) were developed in the last decades, providing a robust modeling framework for calculating gas solubility in electrolyte solutions. Moreover, methods were developed to account for the influence of chemical reactions on phase equilibria [1].

Many research groups have already modeled gas solubility in
aqueous electrolyte solutions, in particular $\mathrm{CO}_{2}$ solubilities, in good agreement with literature data [2-9]. For example, Statistical Associating Fluid Theory (SAFT) was used by Jiang et al. [3], Kohns et al. [7] (SAFT-VRE), and Papaioannou et al. [9] (SAFT- $\boldsymbol{\gamma}$ Mie). Sun et al. [4], Carvalho et al. [5], Li et al. [8], and Chabab et al. [6] used electrolyte Cubic-Plus-Association (e-CPA), and Springer et al. [10] used the model Mixed-Solvent Electrolyte (MSE). Moreover, more recent works by Kaur et al. [11] used nonrandom two-liquid (NRTL)- Perturbed-Chain (PC)-SAFT to model the influence of aqueous electrolyte solutions on $\mathrm{CO}_{2}$ solubility. Novak et al. [12] studied the solubility of $\mathrm{CO}_{2}$ and methane in aqueous electrolyte solutions using eSAFT-VR Mie EOS. In addition, several works investigated the $\mathrm{CO}_{2}$ solubility in organic solvents, such as alcohols, acids, and esters. Oliveira et al. [13] evaluated the $\mathrm{CO}_{2}$ solubility in various organic components. Kristanto et al. [14]

\footnotetext{
* Corresponding author.

E-mail address: christoph.held@tu-dortmund.de (C. Held).
}
measured the $\mathrm{CO}_{2}$ solubility in dimethyl esters, and Gao et al. [15] measured and modeled the $\mathrm{CO}_{2}$ solubility in systems containing ethyl acetate at various temperatures using Peng-Robinson (PR) and PC-SAFT.

However, only a few works focused on a wider variety of systems, e. g., modeling the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions, organic solvents, or a combination of both, a solvent mixture with additional electrolytes present in the mixture. For example, the work by Ahmed et al. [16] mentioned a system comprised of a solvent mixture with electrolytes. In addition, the predictive capability of these EOSs is often limited, and pH effects or dissociation reactions are often neglected or assumed to have a minor influence on $\mathrm{CO}_{2}$ solubility. Even more, there is no work in the literature capable of predicting $\mathrm{CO}_{2}$ solubility in electrolyte solutions.

Only the most recent work by Ascani et al. [17] demonstrated the predictive strength of electrolyte PC-SAFT (ePC-SAFT) advanced. Therein, the pH was predicted at $\mathrm{CO}_{2}$ saturated aqueous electrolyte solutions, in which the saturated state was also predicted with ePC-SAFT advanced. In that work, ePC-SAFT, originally developed by Cameretti et al. [18] and revised by Held et al. [19], was used in the most advanced version, in which long-range ion-ion and ion-solvent effects are screened by concentration-dependent dielectric constant [20,21]. The resulting model ePC-SAFT advanced was also successfully applied in previous works to model solid-liquid equilibria (SLE) of electrolytes in organic solvents, cf. Pabsch et al. [22], and the sour-gas absorption, cf. Bülow et al. [23].

Hence, this work focused on modeling and predicting the $\mathrm{CO}_{2}$ solubility in various multi-component systems using ePC-SAFT advanced. Therefore, literature data from different sources for the $\mathrm{CO}_{2}$ solubility in organic solvents, aqueous electrolyte solutions, solvent mixtures, and solvent mixtures with additional salt were summarized and compared to cover a broad range of systems and conditions. For systems with a lack of data, e.g., $\mathrm{CO}_{2}$ solubility in electrolyte solutions containing cesium salts ( CsCl ), new experimental data on $\mathrm{CO}_{2}$ solubility in electrolyte solutions were measured in this work. The investigated systems cover $\mathrm{CO}_{2}+$ organic solvent (methanol, ethanol, $N$-methyl-2-pyrrolidone (NMP), dimethyl sulfoxide (DMSO), tetrahydrofuran (THF), dimethylformamide (DMF), $\gamma$-Valerolactone (GVL), and acetonitrile (MeCN)), $\mathrm{CO}_{2}+$ water + salt ( $\mathrm{NaCl}, \mathrm{KCl}, \mathrm{MgCl}_{2}, \mathrm{CaCl}_{2}, \mathrm{NaNO}_{3}, \mathrm{KNO}_{3}, \mathrm{Mg}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Ca} \left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Na}_{2} \mathrm{SO}_{4}, \mathrm{~K}_{2} \mathrm{SO}_{4}, \mathrm{MgSO}_{4}, \mathrm{NaHCO}_{3}$, and $\left.\mathrm{K}_{2} \mathrm{CO}_{3}\right), \mathrm{CO}_{2}+$ water + salt mixture $(\mathrm{NaCl}+\mathrm{KCl}), \mathrm{CO}_{2}+$ water + organic solvent (methanol or ethanol), and $\mathrm{CO}_{2}+$ water + organic solvent + salt (methanol +NaCl , and ethanol +CsCl ). The focus was to predict solvent effects, ion effects, and pH effects regarding their influence on the $\mathrm{CO}_{2}$ solubility. No binary interaction parameters between $\mathrm{CO}_{2}$ and ions were used to fit the experimental data.

\section*{2. Theory and thermodynamic modeling}

\subsection*{2.1. Dissociation equilibria}

\subsection*{2.1.1. Involved reactions}

Thermodynamic modeling of the $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions requires simultaneously considering phase equilibria and dissociation equilibria. The dissociation reactions that take place in the liquid phase are summarized in Eqs. (R1) - (R3). That is the autoprotolysis of water Eq. (R1), the first dissociation stage of carbonic acid Eq. (R2), and subsequently, the second deprotonation step of bicarbonate $\left(\mathrm{HCO}_{3}^{-}\right)$to carbonate $\left(\mathrm{CO}_{3}^{2-}\right)$ Eq. (R3).

$$
\begin{equation*}
2 \mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{OH}^{-} \tag{R1}
\end{equation*}
$$


$$
\begin{equation*}
2 \mathrm{H}_{2} \mathrm{O}+\mathrm{CO}_{2} \rightleftharpoons \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{HCO}_{3}^{-} \tag{R2}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{H}_{2} \mathrm{O}+\mathrm{HCO}_{3}^{-} \rightleftharpoons \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{CO}_{3}^{2-} \tag{R3}
\end{equation*}
$$


The considered dissociation reactions (R1) - (R3) are connected via the present $p H$ in the liquid phase. Therefore, knowledge of $p H$ is crucial
in order to determine the degree of dissociation of carbonic acid and whether only physical effects or, in addition, chemical reactions need to be considered when modeling $\mathrm{CO}_{2}$ solubility.

In this work, reactions (R1) - (R3) were not considered when modeling $\mathrm{CO}_{2}$ solubility in single organic systems without the presence of water. Further, previous works by Pabsch et al. [24] and Ascani et al. [17] showed that chloride salts only marginally influence $p H$. However, for salts containing $\mathrm{CO}_{3}^{2-}$ the dissociation reactions (R2) and (R3) were considered in aqueous solutions.

\subsection*{2.1.2. Thermodynamic modeling of dissociation equilibria}

Thermodynamic modeling of the different dissociation equilibria of water and carbonic acid requires accurate thermodynamic equilibrium constants ( $K_{\text {th, } R 1}-K_{\text {th, } R 3}$ ) for each reaction (R1) - (R3). Please note that these constants do NOT depend on the present solvent or composition of the mixture and ONLY on temperature and pressure. The general definition of the thermodynamic equilibrium constant is given in Eq. (4):

$$
\begin{equation*}
K_{t h, R i}(T, p)=K_{\widetilde{m}}(T, p, \widetilde{m}) \cdot K_{\gamma}(T, p, \widetilde{m})=\prod_{i}\left(\widetilde{m}_{i} \gamma_{i}^{{ }^{*}, m}\right)^{\nu_{i}} \tag{4}
\end{equation*}
$$


In Eq. (4), $K_{\widetilde{m}}$ is the ratio of the molalities of all involved reactants at equilibrium and $K_{\gamma}$ is the ratio of the corresponding molality-based activity coefficients at equilibrium.

In this work, thermodynamic equilibrium constants were chosen that were already available from the literature and validated against available equilibrium data from the literature, cf. ref. [25] for detailed information, according to Eqs. (5) - (7).

$$
\begin{equation*}
K_{t h, R 1}(T, p)=\frac{\left(m_{\mathrm{H}_{3} \mathrm{O}^{+}} \gamma_{\mathrm{H}_{3} \mathrm{O}^{+}}^{*}\right)\left(m_{\mathrm{OH}^{-}}^{*} \gamma_{\mathrm{OH}^{-}}^{*, \bar{m}}\right)}{a_{\mathrm{H}_{2} \mathrm{O}^{2}}} \tag{5}
\end{equation*}
$$


$$
\begin{equation*}
K_{t h, R 2}(T, p)=\frac{\left(m_{\mathrm{H}_{3} \mathrm{O}^{+}} \gamma_{\mathrm{H}_{3} \mathrm{O}^{+}}^{*}{ }^{*}\right.}{a_{\mathrm{CO}_{2}} a_{\mathrm{H}_{2} \mathrm{O}^{2}}}\left(m_{\mathrm{HCO}_{3}^{-}}{ }^{*}{ }_{\mathrm{HCO}_{3}^{-}}^{*}\right) \tag{6}
\end{equation*}
$$


$$
\begin{equation*}
K_{t h, R 3}(T, p)=\frac{\left(m_{\mathrm{H}_{3} \mathrm{O}^{+}} \gamma_{\mathrm{H}_{3} \mathrm{O}^{+}}^{*}\right)\left(m_{\mathrm{CO}_{3}^{2-}} \gamma_{\mathrm{CO}_{3}^{2-}}^{*}\right)}{\left(m_{\mathrm{HCO}_{3}^{-}} \gamma_{\mathrm{HCO}_{3}^{-}}^{*, \widetilde{m}}\right)} \tag{7}
\end{equation*}
$$


In Eqs. (5) - (7), $\widetilde{m}_{\mathrm{H}_{3} \mathrm{O}^{+}}, \widetilde{m}_{\mathrm{OH}^{-}}, \widetilde{m}_{\mathrm{HCO}_{3}^{-}}$, and $\widetilde{m}_{\mathrm{CO}_{3}^{2-}}$ are the molality of the hydronium ion ( $\mathrm{H}_{3} \mathrm{O}^{+}$), the hydroxide ion ( $\mathrm{OH}^{-}$), the $\mathrm{HCO}_{3}^{-}$, and the $\mathrm{CO}_{3}^{2-}$ in the mixture, respectively. In addition, the corresponding molality-based activity coefficients $\gamma_{\mathrm{H}_{3} \mathrm{O}^{+}}^{*}, \gamma_{\mathrm{OH}^{-}}^{*}, \gamma_{\mathrm{HCO}_{3}^{-}}^{*}$, and $\gamma_{\mathrm{CO}_{3}^{2-}}^{*}$ are required, cf. Section 2.3. Since both, water and $\mathrm{CO}_{2}$ are non-charged components, the activity $a$ of water ( $a_{\mathrm{H}_{2} \mathrm{O}}$ ) and $\mathrm{CO}_{2}\left(a_{\mathrm{CO}_{2}}\right)$ were calculated via $a_{i}=x_{i} \gamma_{i}$ in Eq. (5) and Eq. (6). Please refer to Section 2.3 for detailed information about the calculation of activity coefficients within ePC-SAFT advanced.
$K_{\text {th, } R 2}$ and $K_{\text {th, } R 3}$ are expressed as functions of pressure and temperature by Eq. (8).
$\ln K_{t h, R i}=a_{1}+a_{2} T+a_{3} T^{-1}+a_{4} T^{-2}+a_{5} \ln T$

$$
\begin{align*}
& +\left(a_{6} T^{-1}+a_{7} T^{-2}+a_{8} T^{-1} \ln T\right)\left(p-p_{0, \text { water }}^{L V}\right) \\
& +\left(a_{9} T^{-1}+a_{10} T^{-2}+a_{11} T^{-1} \ln T\right)\left(p-p_{0, \text { water }}^{L V}\right)^{2} \tag{8}
\end{align*}
$$


Therein, $T$ is the temperature in K and $p$ is the system pressure in bar. $p_{0, \text { water }}^{L V}$ denotes the vapor pressure of water in bar. $a_{1}-a_{11}$ are constants that were fitted to equilibrium data of the species distribution of carbonic acid at various temperatures and pressures, cf. ref. [25]. $a_{1}-a_{11}$ are listed in the Supporting information (SI) in Table S1. The used parameters to calculate $p_{0, \text { water }}^{L V}$ are listed in the SI in Table S2.

\subsection*{2.2. Thermodynamic modeling of the pH}
$p H$ definition has recently been revised by IUPAC, cf. ref. [26], and it is a single ion quantity that accounts for the proton ( $\mathrm{H}^{+}$) activity on a molality scale, cf. Eq. (10). From a practical point of view, the dissociation reaction between $\mathrm{H}_{3} \mathrm{O}^{+}$and $\mathrm{H}^{+}$has to be considered, as shown in Eq. (R9):

$$
\begin{equation*}
\mathrm{H}_{2} \mathrm{O}+\mathrm{H}^{+} \rightleftharpoons \mathrm{H}_{3} \mathrm{O}^{+} \tag{R9}
\end{equation*}
$$


In Eq. (R9), the dissociation equilibrium between $\mathrm{H}^{+}$and $\mathrm{H}_{3} \mathrm{O}^{+}$is far on the right-hand side ( $\mathrm{H}_{3} \mathrm{O}^{+}$) in water solvent. Thus, in this work, all $\mathrm{H}^{+}$ ions were considered to be $\mathrm{H}_{3} \mathrm{O}^{+}$ions in the liquid phase ( $m_{\mathrm{H}_{3} \mathrm{O}^{+}} \gg m_{\mathrm{H}^{+}}$), as done in previous work, cf. ref. [17]. Therefore, the official IUPAC definition of the $p H$ is rewritten as follows:

$$
\begin{equation*}
p H=-\log _{10}\left(a_{H_{3} O^{+}}^{*}\right)=-\log _{10}\left(\frac{m_{H_{3} O^{+}} \gamma_{H_{3} O^{+}}^{*}}{\widetilde{m}^{0}}\right) \tag{10}
\end{equation*}
$$


In Eq. (10), the quantity $a_{\mathrm{H}_{3} \mathrm{O}^{+}}^{*}{ }^{*}$ is the molality-based activity of the $\mathrm{H}_{3} \mathrm{O}^{+}$ions, which is calculated from the molality-based activity coeffi$\operatorname{cient} \gamma_{\mathrm{H}_{3} \mathrm{O}^{+}}^{*}$, cf. Section 2.3, via ePC-SAFT advanced at the given molality $\widetilde{m}_{\mathrm{H}_{3} \mathrm{O}^{+}}$of the $\mathrm{H}_{3} \mathrm{O}^{+}$in the investigated system. $\widetilde{m}^{0}$ denotes the reference molality of $1 \mathrm{~mol} \mathrm{~kg}^{-1}$. The different dissociation steps of the carbonic acid ((R2) and (R3)) are directly affected by the present pH in the liquid phase.

\subsection*{2.3. Activity coefficients}

Modeling phase equilibria require activity coefficients of all species present in the mixture. Thus, the generic activity coefficient $\gamma_{i}$ of each component $i$ in the mixture was calculated from the ratio of the ePCSAFT advanced modeled fugacity coefficients in the mixture ( $\varphi_{i}$ ) referred to the pure-component state ( $\varphi_{0 \mathrm{i}}$ ) (Eq. (11)).

$$
\begin{equation*}
\gamma_{\mathrm{i}}=\frac{\varphi_{\mathrm{i}}(T, p, \vec{x})}{\varphi_{0 i}\left(T, p, x_{i}=1\right)} \tag{11}
\end{equation*}
$$


$$
\begin{equation*}
\gamma_{i}^{*}{ }^{*}=\gamma_{i}^{*}{ }^{*} x_{w}=\frac{\varphi_{i}(T, p, \bar{x})}{\varphi_{i}^{\infty, w}\left(T, p, x_{w} \rightarrow 1\right)} x_{w} \tag{12}
\end{equation*}
$$


In addition, the molality-based activity coefficient at infinite dilution of component $i\left(\gamma_{i}^{*}{ }^{*, \tilde{m}}\right)$ is necessary, cf. Eq. (12). Here $\varphi_{\mathrm{i}}^{\infty, w}$ denotes the fugacity coefficient of component $i$ at infinite dilution and $x_{w}$ is the corresponding mole fraction of water in the mixture.

\section*{2.4. ePC-SAFT modeling framework}

\subsection*{2.4.1. The model}

The ePC-SAFT framework applied in this work accesses the residual Helmholtz energy $a^{\text {res }}$ using different Helmholtz-energy contributions. It is based on the classical PC-SAFT (ref. [27]), which describes dispersive perturbations (accounted for by the contribution $a^{\text {disp }}$ ) and associating forces (accounted for by the contribution $a^{\text {assoc }}$ (ref. [28])) of a hard-chain reference fluid (described by $a^{h c}$ ). Additional contributions to $a^{\text {res }}$ that were developed in previous works, especially dipole forces ( $a^{\text {dipole }}$ (ref. [29])), are included in the ePC-SAFT framework used in this work. For electrostatic interactions, theories from Debye-Hückel and Born are used, namely the Helmholtz-energy contributions $a^{D H}$ (ref. [30]) and $a^{\text {Born }}$ (ref. [31]). Both $a^{D H}$ and $a^{\text {Born }}$ might be expressed as a function of the permittivity of the medium.

$$
\begin{equation*}
a^{\text {res }}=a^{h c}+a^{\text {disp }}+a^{\text {assoc }}+a^{\text {dipole }}+a^{D H}(\varepsilon(\bar{x}))+a^{\text {Born }}(\varepsilon(\bar{x})) \tag{13}
\end{equation*}
$$


Five pure-component parameters are assigned to associating compounds like water. The pure-component parameters are the segment number $m_{i}^{\text {seg }}$, the segment diameter $\sigma_{i}$, the dispersion-energy parameter
$u_{i} / k_{B}$ and additionally, the association-energy parameter $\varepsilon^{A i B i}$ and the association-volume parameter $\kappa^{A i B i}$. For very dipolar components, the dipole moment $\mu_{i}$ is required for improved modeling of mixtures. This was applied to NMP in this work, as proposed by Gross and Vrabec [29]. Considering modeling of the ions, two pure-component parameters for the ions were used to characterize ions, $\sigma_{i}$ and $u_{i} / k_{B}$. Within the ePC-SAFT framework, dispersion is allowed between solvents and ions and among cations and anions, while dispersion among equal ions is switched off. A detailed overview about the used pure-component parameters is given in Table 1.

More importantly, the effect of long-range ion solvation is considered in this work by the altered Born contribution in Eq. (13), which is screened by a concentration-dependent dielectric constant $\varepsilon_{r}(\bar{x}) ; \varepsilon_{r}(\bar{x})$ was also used in $a^{D H}$. The altered Born contribution was derived by Bülow et al. [20]. The respective molar Helmholtz-energy contribution $a^{\text {Born }}$ is calculated according to Eq. (14).

$$
\begin{equation*}
a^{\text {Born }}=-\frac{e^{2}}{4 \pi \varepsilon_{0} k_{B} T}\left(1-\frac{1}{\varepsilon_{r}(\bar{x})}\right) \sum_{i} \frac{x_{i} z_{i}^{2}}{\sigma_{i}} \tag{14}
\end{equation*}
$$

$\varepsilon_{0}$ and $k_{B}$ are the dielectric constant of vacuum, the Boltzmann constant, while $e$ and $z_{i}$ are elementary charge and valence of an ion, respectively. As suggested by Bülow et al. [20], the distance of the closest approach $a_{i}$ was set to the respective diameter of the ion $\sigma_{i}$. Modeling mixtures requires the combining rules of Berthelot-Lorentz (Eq. (15) and Eq. (16)).

$$
\begin{equation*}
\sigma_{i j}=\frac{1}{2}\left(\sigma_{i}+\sigma_{j}\right) \tag{15}
\end{equation*}
$$


$$
\begin{equation*}
u_{i j}=\sqrt{u_{i} u_{j}}\left(1-k_{i j}\right) \tag{16}
\end{equation*}
$$


Eq. (16) introduces the binary interaction parameter $k_{i j}$ that might be used to alter the dispersion energy $u_{i j}$ in the mixture. In this work, the binary interaction parameter $k_{i j}$ introduced in Eq. (16) was treated as a linear function of the temperature (Eq. (17)).

$$
\begin{equation*}
k_{i j}(T)=k_{i j, a}+k_{i j, T} \cdot\left(T-T^{+}\right) \tag{17}
\end{equation*}
$$


Therein, $T^{+}$donates the reference temperature of 298.15 K . An overview of the binary interaction parameters $k_{i j}$ used in this work is given in Table 3 (ion - ion), Table 4 (solvent - solvent and ion - solvent), and Table 6 ( $\mathrm{CO}_{2}$ - organic solvent). In this work, all vapor-liquid equilibria (VLE) were calculated with the iso-fugacity criterion, according to previous works by Ascani et al. [38] and Pabsch et al. [24]. Therein, ions were defined as non-volatile components and thus, were excluded from the vapor phase. However, the present ions in the liquid phase influence the fugacity coefficients of the other components.

\subsection*{2.4.2. Pure-component parameters and pure-components parameters for the ions}

For modeling purposes, pure-component parameters are necessary. Table 1 lists all pure-component parameters of the components used in this work. Water was modeled with a 2 B association scheme, as proposed by Cameretti and Sadowski [39], as this water parameter set was used to parameterize the ions; thus, the ion parameters are best performing with the 2 B water parameters. The association schemes for all associating fluids was set to 2 B and induced association was applied as proposed by Kleiner and Sadowski [40]; all pure-component parameters were inherited from the literature. NMP was modeled as a non-associating fluid but with a dipole moment with available parameters from the literature. The temperature-dependent segment diameter $d(T)$ for the ions was set to $\sigma_{i}$ as suggested in ePC-SAFT revised, which is a consequence of setting the dispersion energy between two equal ions to zero [19].

As shown in Table 1, CO2 was modeled with induced association with parameters available from the literature [24]. Recent works by Park et al. [41] showed that the modeling accuracy significantly increased by

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1
ePC-SAFT pure-component parameters and pure-component parameters for the ions used in this work. All parameters were inherited from literature. Associating fluids were assigned with the 2 B associating scheme.}
\begin{tabular}{|l|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Component} & \multirow[t]{2}{*}{$m_{i}^{\text {seg }}$} & \multirow{2}{*}{$\sigma_{i} / \AA$} & $u_{i} / k_{B}$ & $\varepsilon^{A i B i}$ & \multirow[t]{2}{*}{$\kappa^{A i B i}$} & \multirow{2}{*}{$\mu_{i}$ / D} & \multirow[t]{2}{*}{Ref.} \\
\hline & & & / K & / K & & & \\
\hline $\mathrm{CO}_{2}{ }^{\mathrm{b}}$ & 2.0729 & 2.7852 & 169.21 & - & 0.04509 & - & [24] \\
\hline Water & 1.2047 & a & 353.95 & 2425.7 & 0.04509 & - & [32] \\
\hline methanol & 1.5255 & 3.2300 & 188.90 & 2899.5 & 0.03518 & - & [28] \\
\hline ethanol & 2.3827 & 3.1771 & 198.24 & 2653.4 & 0.03238 & - & [28] \\
\hline NMP & 3.2417 & 3.4907 & 310.79 & - & - & 4.09 & [33] \\
\hline DMSO ${ }^{\mathrm{b}}$ & 2.922 & 3.278 & 355.69 & - & 0.04509 & - & [34] \\
\hline THF & 2.425 & 3.497 & 280.41 & - & - & - & [35] \\
\hline DMF & 2.388 & 3.658 & 363.77 & - & - & - & [36] \\
\hline GVL & 2.8892 & 3.6208 & 362.6 & - & - & - & [37] \\
\hline MeCN & 2.329 & 3.1898 & 311.31 & - & - & - & [36] \\
\hline $\mathrm{Na}^{+}$ & 1 & 2.8232 & 230.00 & - & - & - & [19] \\
\hline $\mathrm{K}^{+}$ & 1 & 3.3417 & 200.00 & - & - & - & [19] \\
\hline $\mathrm{Cs}^{+}$ & 1 & 3.9246 & 180.00 & - & - & - & [19] \\
\hline $\mathrm{Mg}^{2+}$ & 1 & 3.1327 & 1500.00 & - & - & - & [19] \\
\hline $\mathrm{Ca}^{2+}$ & 1 & 3.2648 & 1060.00 & - & - & - & [19] \\
\hline $\mathrm{Cl}^{-}$ & 1 & 2.7560 & 170.00 & - & - & - & [19] \\
\hline $\mathrm{HCO}_{3}^{-}$ & 1 & 2.9296 & 70.00 & - & - & - & [19] \\
\hline $\mathrm{CO}_{3}^{2-}$ & 1 & 2.4422 & 249.26 & - & - & - & [19] \\
\hline $\mathrm{NO}_{3}^{-}$ & 1 & 3.2988 & 130.00 & - & - & - & [19] \\
\hline $\mathrm{SO}_{4}^{2-}$ & 1 & 2.6491 & 80.00 & - & - & - & [19] \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}} \sigma=2.7927+\left(10.11 \cdot \mathrm{e}^{-0.01775 T}-1.417 \cdot \mathrm{e}^{-0.01146 T}\right)$ with $T$ in K
${ }^{\mathrm{b}}$ Modeled with induced association as proposed by Kleiner and Sadowski ${ }^{34}$.
considering association of the $\mathrm{CO}_{2}$ molecules, especially at higher temperatures and pressures, cf. ref. [41] for more details.

It is essential to state that all the pure-component parameters for the ions listed in Table 1 were regressed from experimental data of aqueous electrolyte solutions. The transferability of the pure-component parameters for the ions to non-aqueous systems was already proven in the work of Bülow et al. [20] by predicting MIACs in organic solvents using pure-component parameters for the ions that were originally fitted to experimental MIACs in aqueous solutions.

The $a^{D H}$ and $a^{\text {Born }}$ contributions in Eq. (13) require the dielectric constants $\varepsilon_{r}(\bar{x})$ of the investigated mixtures. The pure-component values for solvents and ions are summarized in Table 2. Please note that CO2 is also defined as a solvent in Eq. (18). All ions were assumed to have the same value of $\varepsilon_{r}=8$; this value is an average value, and it is hardly affected by temperature and pressure [42]. From previous works by Ascani and Held [43] it is known that the dielectric constant of a mixture

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2
Dielectric constants for all components applied in this work.}
\begin{tabular}{|l|l|l|}
\hline Component & Dielectric constant ${ }^{\mathrm{a}} / C \cdot V m^{-1}$ & Ref. \\
\hline $\mathrm{CO}_{2}$ water & \begin{tabular}{l}
$-0.0036 T+2.467$ \\
$-105.2 \ln T+$ 677.480
\end{tabular} & Correlation from this work using ref. [44-46] [47] \\
\hline methanol & $-0.192 T+90.09$ & [48] \\
\hline ethanol & $-0.146 T+68.47$ & [49] \\
\hline NMP & $-0.153 T+77.73$ & [50] \\
\hline DMSO & - 0.1214T+ 85.848 & Correlation from this work using ref. [51-56] \\
\hline THF & - 0.0337T+ 17.687 & Correlation from this work using ref. [55-64] \\
\hline DMF & - 0.1699T+ 89.245 & Correlation from this work using ref. [55,56, 65-67] \\
\hline GVL & - 0.0813T+ 60.653 & [68,69] \\
\hline MeCN & $-0.1729 T+$ 88.066 & Correlation from this work using ref. [53,55, 56,70-73] \\
\hline Ions & 8 & ${ }^{\mathrm{b}}$ \\
\hline
\end{tabular}
\end{table}

\footnotetext{
${ }^{\mathrm{a}}$ with $T$ in K
${ }^{\mathrm{b}}$ All ions were modeled with the same dielectric constant as the mean of available experimental data [74].
}
can be approximated by a linear concentration dependence in the solvent mass fraction and in ion mole fraction, see Eq. (18).

$$
\begin{equation*}
\varepsilon_{r}=\left(\sum_{j=1}^{N^{\text {solv }}} \varepsilon_{r, j} w_{j}^{\text {solv }}\right) x_{\text {sol }}+\sum_{j=1}^{N^{\text {ion }}} \varepsilon_{r, j} x_{j}^{\text {ion }} \tag{18}
\end{equation*}
$$


Here, $x_{j}$ and $w_{j}$ represent the mole fraction and the mass fraction of component $j$, respectively. $N^{\text {solv }}$ denotes the total number of components in the salt-free solvent mixture and $N^{i o n}$ denotes the total number of charged components, i.e., ions. $w_{j}^{\text {solv }}$ is the mass fraction of solvent $j$ in the salt-free solvent mixture, while $x_{\text {sol }}$ represents the sum of the mole fraction of all solvents present in the overall mixture. $\varepsilon_{r, j}$ is the dielectric constant of component $j$.

The dielectric constants of the solvents were assumed to depend linearly on temperature, according to Table 2. This was also assumed in previous works to model MIACs [20], liquid-liquid equilibria [75], and solid-liquid equilibria [21,22].

\subsection*{2.4.3. Binary interaction parameters}

Most of the binary interaction parameters were inherited from literature. Due to unavailability, some binary interaction parameters between $\mathrm{CO}_{2}$ - organic solvent were determined in this work by fitting to equilibrium data from the literature. In general, a minimum number of binary interaction parameters was used. However, essential binary interaction parameters, e.g., between $\mathrm{CO}_{2}$ - solvent and solvent - solvent, were necessary for high modeling accuracy. For that purpose, the objective function $(O F)$ in Eq. (19) was minimized.

$$
\begin{equation*}
O F=\sum_{m}^{N P}\left(1-\frac{x_{\mathrm{CO}_{2}}^{L, e P C-S A F T}}{x_{\mathrm{CO}_{2}}^{L, e x p}}\right)^{2} \tag{19}
\end{equation*}
$$


Therein, $x_{\mathrm{CO}_{2}}^{L, \text { ePC-SAFT }}$ and $x_{\mathrm{CO}_{2}}^{L, \text { exp }}$ are the ePC-SAFT advanced calculated and the experimentally determined $\mathrm{CO}_{2}$ solubility in mole fraction in the liquid phase $L$ at constant pressure and temperature, respectively. $m$ is the total number of considered data points NP. For detailed information about the fitted binary interaction parameters in this work, see Table S3 and Figs. S1-S9 in the SI. Table 3 shows all binary interaction parameters between ion - ion used in this work. These parameters were all inherited from the literature by fitting to osmotic-coefficient data and liquid-density data [19,22]. In addition, binary interaction parameters

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3
Binary interaction parameters $k_{i j}$ between anions and cations used in this work for Eq. (17).}
\begin{tabular}{|l|l|l|l|l|l|}
\hline & $\mathrm{Na}^{+}$ & $\mathrm{K}^{+}$ & $\mathrm{Cs}^{+}$ & $\mathrm{Mg}^{2+}$ & $\mathrm{Ca}^{2+}$ \\
\hline $\mathrm{Cl}^{-}$ & $0.317{ }^{\text {a }}$ & $0.064{ }^{\text {a }}$ & -0.417 ${ }^{\text {a }}$ & $0.817{ }^{\text {a }}$ & $1{ }^{\text {a }}$ \\
\hline $\mathrm{HCO}_{3}^{-}$ & -0.514 ${ }^{\text {a }}$ & $-0.476{ }^{\text {a }}$ & $-0.7^{\mathrm{b}}$ & - & - \\
\hline $\mathrm{CO}_{3}^{2-}$ & $-1^{\mathrm{a}}$ & $1{ }^{\text {a }}$ & $0.7{ }^{\text {b }}$ & - & - \\
\hline $\mathrm{NO}_{3}^{-}$ & $-0.3{ }^{\mathrm{a}}$ & $-0.585{ }^{\mathrm{a}}$ & $-0.855{ }^{\mathrm{a}}$ & $0.285{ }^{\mathrm{a}}$ & -0.101 ${ }^{\text {a }}$ \\
\hline $\mathrm{SO}_{4}^{2-}$ & $-1^{\mathrm{a}}$ & $1{ }^{\text {a }}$ & $-1^{\mathrm{a}}$ & -1 ${ }^{\text {a }}$ & -0.908 ${ }^{\text {a }}$ \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}}$ Held et al. ${ }^{19}$
${ }^{\mathrm{b}}$ Pabsch et al. ${ }^{22}$
between solvent - solvent, fitted to VLE data, and ion - solvent (Table 4), fitted to SLE data, and $\mathrm{CO}_{2}$ - solvent (Table 6), fitted to VLE data in this work, were required. In contrast, binary interaction parameters between $\mathrm{CO}_{2}$ - ion and water - ion were not required.

\section*{3. Materials and methods}

\subsection*{3.1. Materials}

Literature data on the $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions containing cesium salts were not available in the literature. Thus, new experimental data for the $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions containing cesium salts were measured in this work. All chemicals used in this work are provided in Table 5.

Water was freshly prepared by the ultra-pure Millipore water device (Milli-Q Integral system, Merck, Darmstadt, Germany). Prior to any experiment, the salts were dried for at least seven days in a vacuum chamber ( $p=0.02$ bar) at $T=298.15 \mathrm{~K}$.

\subsection*{3.2. Experimental methods}

\subsection*{3.2.1. Determination of $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions containing cesium}

In this work, the VLEs were measured visually in order to determine the $\mathrm{CO}_{2}$ solubility in the liquid phase. Hence, a high-pressure variablevolume view cell (HPVVV) apparatus by New Ways of Analytics analytische Messgeräte GmbH (Lörrach, Germany) was used for gas-solubility determination, as described in previous works, cf. ref. [78-81]. The phase transition from the VLE was monitored through two sapphire windows (front and back). Here, the back sapphire was movable to vary the volume of the cell between 30 mL and 60 mL . Therefore, a manual hydraulic-press $\mathrm{M}(\mathrm{O}) 189$ by Maximator (Zorge, Germany) was connected to the back sapphire. In order to ensure homogeneity of the phases, a magnetically coupled stirrer was attached to the HPVVV, and two heating jackets adjusted the temperature with an accuracy of $\pm 1 \mathrm{~K}$. Moreover, the temperature (Pt100, uncertainty 0.1 K ) and pressure (WIKA S11, Klingenberg, Germany) were measured directly inside the HPVVV. Before pressurizing the HPVVV, a defined composition of aqueous or organic electrolyte solutions was added to the cell, and the temperature was set to the desired condition. Next, compressed CO2 ( $p =250$ bar and $T=308.15 \mathrm{~K}$ ) was pumped into the HPVVV using a syringe pump of the type 260D from ISCO (Lincoln, USA). The mass of

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4
Binary interaction parameters $k_{i j}$ between solvent - solvent and ion - solvent used in this work for Eq. (17).}
\begin{tabular}{|l|l|l|l|}
\hline Binary system & $k_{i j, T} / \mathrm{K}^{-1}$ & $k_{i j, a}$ & Ref. \\
\hline water- methanol & 0.00058 & -0.0878 & [76] \\
\hline water - ethanol & 0.00069 & -0.0617 & [77] \\
\hline $\mathrm{Na}^{+}$- methanol & - & -0.31 & [21] \\
\hline $\mathrm{Cl}^{-}$- methanol & - & -0.21 & [21] \\
\hline $\mathrm{Cs}^{+}$- ethanol & - & -0.345 & [22] \\
\hline $\mathrm{Cl}^{-}$- ethanol & - & -0.15 & [21] \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5
CAS Registry Number, supplier, and mass fraction purity of the chemicals used in this work.}
\begin{tabular}{|l|l|l|l|}
\hline Component & CAS Reg. NO. & Suppliers & Purity / mass $\%^{\text {b }}$ \\
\hline $\mathrm{CO}_{2}$ & 124-38-9 & Messer & >99.5 \\
\hline ethanol ${ }^{\mathrm{a}}$ & 64-17-5 & Merck & >99.9 \\
\hline CsCl & 7647-17-8 & VWR & >99.5 ${ }^{\mathrm{c}}$ \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}}$ Anhydrous.
${ }^{\mathrm{b}}$ Purity from datasheet; water content verified by Karl-Fischer titration for the organic solvents
${ }^{\mathrm{c}}$ Additionally dried in a vacuum chamber.
added $\mathrm{CO}_{2}$ to the HPVVV was calculated from the injected volume and the known density at $p=250$ bar and $T=308.15 \mathrm{~K}$. Thus, the composition of the mixture inside the HPVVV was well known. Finally, the phase transition was investigated optically by varying the volume inside the HPVVV. From that, the $\mathrm{CO}_{2}$ solubility was obtained. Please note that no precipitation of the salt and no liquid-liquid demixing due to the added $\mathrm{CO}_{2}$ into the liquid phase were observed during the measurements. Thus, a homogeneous liquid phase was ensured during all the experiments. In addition, pictures of the HPVVV during the experiments with salts were taken, cf. Fig. S10 in the SI. Prior to measuring the $\mathrm{CO}_{2}$-solubility in electrolyte systems containing CsCl , validation experiments with well-known systems from the literature (e.g., $\mathrm{CO}_{2}+$ ethanol $(+\mathrm{NaCl}))$ were carried out in order to verify the experimental setup and method.

\subsection*{3.3. Comparison of experimental data from different sources and modeling results}

\subsection*{3.3.1. Average relative standard deviation (ARSD)}

In order to address the uncertainty of experimental data and to compare the modeling accuracy, the literature data were evaluated in terms of the relative standard deviation (RSD) and ARSD related to the mean of the experimental data as given in Eqs. $(20,21)$.

$$
\begin{equation*}
R S D_{j}=\frac{\sqrt{\frac{1}{N-1} \sum_{i}^{N}\left(x_{i}^{\text {exp }}-x^{\text {exp,mean }}\right)^{2}}}{x^{\text {exp,mean }}} \tag{20}
\end{equation*}
$$


$$
\begin{equation*}
A R S D=\frac{100}{N P} \cdot \sum_{i}^{N P} R S D_{j} \tag{21}
\end{equation*}
$$

$x_{i}^{\exp }$ denotes the experimental $\mathrm{CO}_{2}$ solubility at a given pressure and temperature and $x^{\text {exp,mean }}$ denotes the mean value from different sources but for the same conditions. $N$ is the number of compared data points at the same condition, and NP represents the total number of data points for a specific system $j$, e.g., $\mathrm{CO}_{2}+$ solvent. Finally, $A R S D$ represents the averaged $R S D$ values for a specific system $j$.

\subsection*{3.3.2. Average absolute standard deviation (AARD)}

Further, the accuracy of ePC-SAFT advanced modeling results compared to the experimental data was addressed by the $A R D$ value, which is related to the mean value of experimental data (Eq. (22)).

$$
\begin{equation*}
A R D_{j}=\frac{100}{N P} \cdot \sum_{i}^{N P}\left|1-\frac{x_{i}^{e P C-S A F T}}{x^{e x p, m e a n}}\right| \tag{22}
\end{equation*}
$$


$$
\begin{equation*}
A A R D=\frac{100}{N P} \cdot \sum_{i}^{N P} A R D_{j} \tag{23}
\end{equation*}
$$

$x_{i}^{e P C-S A F T}$ denotes the $\mathrm{CO}_{2}$ solubility modeled with ePC-SAFT advanced while $x^{\text {exp,mean }}$ denotes the corresponding mean of experimental data from the literature for a specific system $j$. NP represents the total amount of compared data points. The $A A R D$ value in Eq. (23) represents the averaged ARD values for a specific system $j$. In sum, the ARDs and AARDs are listed together with the RSDs and ARSDs in Tables

S4 and S5 in the SI.

\section*{4. Results and discussion}

The ePC-SAFT advanced modeling framework was applied to model and predict the $\mathrm{CO}_{2}$ solubility in various aqueous and organic electrolyte solutions. In addition, solvent effects, ion effects, and $p H$ effects were investigated. Prior to studying the $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions, the binary systems $\mathrm{CO}_{2}+$ solvent (water, methanol, ethanol, NMP, DMSO, THF, DMF, GVL, or MeCN) were evaluated.

\section*{4.1. $\mathrm{CO}_{2}+$ organic solvent}

Quantitatively modeling the $\mathrm{CO}_{2}$ solubility in single organic solvents required binary interaction parameters $k_{i j}$ between $\mathrm{CO}_{2}$ - organic solvent. Table 6 lists all binary interaction parameters $k_{i j}$ which were inherited from the literature or determined in this work by fitting to available equilibrium data from the literature.

From Table 6, it is shown that, in general, small $k_{i j}$ values were necessary to model the $\mathrm{CO}_{2}$ solubility in organic solvents, and for some binary systems, temperature-dependent $k_{i j}$ values were required. In conclusion, these $k_{i j}$ values allowed accurately modeling of the $\mathrm{CO}_{2}$ solubility in organic solvents. The equilibrium data used to fit the parameters are listed in detail from Tables S6-S13 in the SI, and the corresponding ARSD and AARD for each binary system are also given. Fig. 1 shows the $\mathrm{CO}_{2}$ solubility in eight different organic solvents and in water.

It is clear to elaborate that the solvent has a significant influence on $\mathrm{CO}_{2}$ solubility. At the conditions in Fig. $1(T=313.15 \mathrm{~K})$ the $\mathrm{CO}_{2}$ solubility increases in the order water < GVL < methanol < DMSO < ethanol < MeCN < NMP < DMF < THF. Thus, non-self-associating solvents are favorable for high $\mathrm{CO}_{2}$ solubilities, and $\mathrm{CO}_{2}$ solubility is high in solvents of high dipole moment, e.g., NMP. Thus, among all investigated solvents, the $\mathrm{CO}_{2}$ solubility is the highest in THF and the lowest in water. Further, it can be observed that the ePC-SAFT advanced modeling results obtained by correlation of a binary interaction parameter between $\mathrm{CO}_{2}$ and each solvent are in quantitative agreement with the given literature data.

\section*{4.2. $\mathrm{CO}_{2}+$ water + salt}

Next, the influence of the electrolytes $\mathrm{NaCl}, \mathrm{KCl}, \mathrm{MgCl}_{2}, \mathrm{CaCl}_{2}$, $\mathrm{NaNO}_{3}, \mathrm{KNO}_{3}, \mathrm{Mg}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Ca}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Na}_{2} \mathrm{SO}_{4}, \mathrm{~K}_{2} \mathrm{SO}_{4}, \mathrm{MgSO}_{4}, \mathrm{NaHCO}_{3}$, and $\mathrm{K}_{2} \mathrm{CO}_{3}$ on $\mathrm{CO}_{2}$ solubility in water is studied. These systems were partly modeled in previous work $\left(\mathrm{NaCl}, \mathrm{KCl}, \mathrm{MgCl}_{2}, \mathrm{CaCl}_{2}, \mathrm{NaNO}_{3}\right.$, $\mathrm{KNO}_{3}, \mathrm{Mg}\left(\mathrm{NO}_{3}\right)_{2}$, and $\mathrm{NaHCO}_{3}$ ) by Pabsch et al. [24]. However, the previous work did not account for the modified Born term in the ePC-SAFT framework. Thus, ion-dipolar solvation was not considered, and large values for $k_{i j}$ between $\mathrm{CO}_{2}-$ ion were necessary to correlate the literature data. In contrast, the ePC-SAFT modeling framework in the present work considered the altered Born term. As an outstanding result, NO binary interaction parameters between CO2 - ions were necessary.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 6
Binary interaction parameters $k_{i j}$ between $\mathrm{CO}_{2}$ and solvents used in this work inherited from literature or determined in this work.}
\begin{tabular}{|l|l|l|l|l|}
\hline Binary system & $k_{i j, T} / \mathrm{K}^{-1}$ & $k_{i j, a}$ & $T$-range / K & Ref. \\
\hline $\mathrm{CO}_{2}$ - water & 0.0003016 & 0.0122 & cf. ref. [24] & [24] \\
\hline $\mathrm{CO}_{2}$ - methanol & - & 0.08 & 298-395 & This work [82-85] \\
\hline $\mathrm{CO}_{2}$ - ethanol & -0.0017 & 0.11534 & 308-344 & This work [82,85,86] \\
\hline $\mathrm{CO}_{2}$ - NMP & -0.0002 & 0.02487 & 293-348 & This work [87-90] \\
\hline $\mathrm{CO}_{2}$ - DMSO & - & 0.0367 & 298-318 & This work [88] \\
\hline $\mathrm{CO}_{2}$ - THF & - & 0.04 & 313-353 & This work [91] \\
\hline $\mathrm{CO}_{2}$ - DMF & - & 0.05 & 313-395 & This work [92] \\
\hline $\mathrm{CO}_{2}$ - GVL & 0.0009 & 0.20083 & 283-323 & This work [93] \\
\hline $\mathrm{CO}_{2}-\mathrm{MeCN}$ & - & 0.02 & 308-348 & This work [94] \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-06.jpg?height=684&width=858&top_left_y=193&top_left_x=1076}
\captionsetup{labelformat=empty}
\caption{Fig. 1. $\mathrm{CO}_{2}$ solubility in mole fraction in different solvents plotted against the pressure at constant temperature $\mathrm{T}=313.15 \mathrm{~K}$. Symbols represent experimental data from the literature (solid circles: water from Kiepe et al. [95], solid hexagons: GVL from Deng et al. [93], solid squares: methanol from Chang et al. [82], solid up-triangles: ethanol from Chang et al. [82], solid stars: NMP from Bohloul et al. [89], solid diamonds: DMF from Jödecke et al. [92], and solid down-triangles: THF from Knez et al. [91]). For DMSO and MeCN, no literature data were available at these conditions. Lines are modeling results (solid line: water, long-dashed line: GVL, dotted line: methanol, long-dash-dotted line: DMSO, short-dashed line: ethanol, empty-dashed line: MeCN, short-dash-dotted line: NMP, empty-dotted line: DMF, and empty-long-dash-dotted line: THF) obtained with ePC-SAFT advanced using parameters from Tables 1, 2 and 6.}
\end{figure}

Thus, in contrast to all other literature works on correlating CO2 solubility, the following modeling results represent predictions since no additional model parameters were fitted to the studied multi-component systems.

\subsection*{4.2.1. Prediction of $\mathrm{CO}_{2}$ solubility}

In the following, predictions of the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions with ePC-SAFT advanced are compared with available literature data. Fig. 2 illustrates predictions obtained with ePC-SAFT advanced for the system $\mathrm{CO}_{2}+$ water +NaCl for different molalities of NaCl at $T=323 \mathrm{~K}$.

Fig. 2 shows that predictions obtained with ePC-SAFT advanced qualitatively agree with the given literature data. ePC-SAFT advanced was able to predict the salting-out effect of NaCl on $\mathrm{CO}_{2}$ solubility correctly. Even more, ePC-SAFT advanced is able to predict the saltingout effect of the other salts on the $\mathrm{CO}_{2}$ solubility in all investigated aqueous electrolyte solutions ( $\mathrm{NaCl}, \mathrm{KCl}, \mathrm{MgCl}_{2}, \mathrm{CaCl}_{2}, \mathrm{NaNO}_{3}, \mathrm{KNO}_{3}$, $\mathrm{Mg}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Ca}\left(\mathrm{NO}_{3}\right)_{2}, \mathrm{Na}_{2} \mathrm{SO}_{4}, \mathrm{~K}_{2} \mathrm{SO}_{4}, \mathrm{MgSO}_{4}, \mathrm{NaHCO}_{3}$, and $\mathrm{K}_{2} \mathrm{CO}_{3}$ ) over a large range of conditions, i.e., temperature, pressure, and high salt concentrations. The complete comparison between the predicted modeling results obtained in this work and the modeling results obtained in a previous work [24] is given in the SI in Table S4. In addition, each system is separately listed in the SI in Tables S14 - S24 with the corresponding ARSD and AARD. Moreover, ePC-SAFT advanced allows for predicting the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions containing sulfates, i.e., $\mathrm{Na}_{2} \mathrm{SO}_{4}, \mathrm{~K}_{2} \mathrm{SO}_{4}$, and $\mathrm{MgSO}_{4}$. Fig. 3 shows the system $\mathrm{CO}_{2}+$ water $+\mathrm{K}_{2} \mathrm{SO}_{4}$. The predictions obtained with ePC-SAFT advanced for $\mathrm{CO}_{2}+$ water $+\mathrm{Na}_{2} \mathrm{SO}_{4}$ and $\mathrm{CO}_{2}+$ water $+\mathrm{MgSO}_{4}$ are compared in Tables S25 and S26 in the SI with the corresponding ARSD and $A A R D$ values.

Fig. 3 illustrates that ePC-SAFT advanced is able to predict the $\mathrm{CO}_{2}$ solubility in aqueous $\mathrm{K}_{2} \mathrm{SO}_{4}$ solutions. In general, the modeling accuracy is very high at $T>298 \mathrm{~K}$ while slight deviations to experiments can be found below 298 K . A further discussion of the ions' salting-out effect on

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-07.jpg?height=684&width=860&top_left_y=191&top_left_x=146}
\captionsetup{labelformat=empty}
\caption{Fig. 2. $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the pressure at constant temperature $\mathrm{T}=323 \mathrm{~K}$ for different NaCl molalities. Symbols represent experimental data from the literature (solid circles: salt-free from Peng et al. [96], empty squares: $1 \mathrm{~mol} \mathrm{~kg}^{-1}$ and solid down-triangles: $5 \mathrm{~mol} \mathrm{~kg}^{-1}$ from Yan et al. [97], solid up-triangles: 2.5 mol $\mathrm{kg}^{-1}$ and empty diamonds: $4 \mathrm{~mol} \mathrm{~kg}^{-1}$ from Hou et al. [98]). Lines represent predictions (solid line: salt-free, dash-double-dotted line: $1 \mathrm{~mol} \mathrm{~kg}^{-1}$, dotted line: $2.5 \mathrm{~mol} \mathrm{~kg}^{-1}$, dash-dotted line: $4 \mathrm{~mol} \mathrm{~kg}^{-1}$, dashed line: $5 \mathrm{~mol} \mathrm{~kg}^{-1}$ ) obtained with ePC-SAFT advanced using parameters from Tables 1, 2, 3 and 6.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-07.jpg?height=655&width=871&top_left_y=1253&top_left_x=139}
\captionsetup{labelformat=empty}
\caption{Fig. 3. $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the molality of $\mathrm{K}_{2} \mathrm{SO}_{4}$ at $\mathrm{p}=1.01325$ bar. Symbols represent experimental data from He et al. [99] (solid circles: 298 K , solid down-triangles: 323 K , solid diamonds: 348 K , and solid hexagons: 363 K ). Lines represent predictions (solid line: 298 K , dotted line: 323 K , dash-dotted line: 348 K , and dash-double-dotted line: 363 K ) obtained with ePC-SAFT advanced using parameters from Tables 1-3 and 6.}
\end{figure}
$\mathrm{CO}_{2}$ solubility can be found in Section 4.2.3. It is essential to mention that ePC-SAFT revised was not able to model the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions containing sulfates, and ePC-SAFT revised
(and any other literature model) required binary interaction parameters between $\mathrm{CO}_{2}$ - ion to model the $\mathrm{CO}_{2}$ solubilities correctly. Within ePCSAFT revised, the value of the dielectric constant in the mixture is set constant ( $\varepsilon_{r}=\varepsilon_{\mathrm{H}_{2} \mathrm{O}}=$ const.), cf. Pabsch et al. [22,24] and Held et al. [19]. Obviously, the key behind these outstanding results is the modified Born term that considers solvation of ions by the surrounding medium.

\subsection*{4.2.2. Prediction of the pH in equilibrated phases}

Previous work already modeled the $p H$ in various multiphase aqueous electrolyte solutions in excellent agreement with the given literature data, cf. ref. [17] In this work, a closer investigation was carried out, and the pH effect on the $\mathrm{CO}_{2}$ solubility was discussed in more detail.

Fig. 4 shows both, the $\mathrm{CO}_{2}$ solubility as a function of NaCl molality (Fig. 4i)) and the corresponding $p H$ of the equilibrated liquid phase (Fig. 4ii)). Both, the ePC-SAFT advanced predicted $\mathrm{CO}_{2}$ solubility and the corresponding $p H$ in the liquid phase match the experimental data. Since only binary interaction parameters between ion - ion (Table 3) and $\mathrm{CO}_{2}$ - water (Table 6) were used, this is an impressive proof of the predictive power of the ePC-SAFT advanced modeling framework.

\subsection*{4.2.3. Discussion}
4.2.3.1. Influence of pH on $\mathrm{CO}_{2}$ solubility. Fig. 4i) illustrates the saltingout effect of NaCl . Compared to the salt-free system, the $\mathrm{CO}_{2}$ solubility is almost halved upon adding $5 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{NaCl}$. Thus, strong salting-out effects of the electrolytes on $\mathrm{CO}_{2}$ solubility are present. Also, the pH is only slightly decreasing with an increasing NaCl molality. Further, modeling the $\mathrm{CO}_{2}$ solubility (Fig. 4i) was not influenced by the dissociation reactions (R2) and (R3) since the pH was not strongly affected by the added NaCl (Fig. 4ii)). This was observed for all salts studied in this work except for carbonate salts. Although the $\mathrm{CO}_{2}$ solubility is decreasing (Fig. 4i), and thus, less carbonic acid should be present in the liquid phase, the pH is decreasing (Fig. 4ii). This behavior is counterintuitive since less amount of acid should result in a higher $p H$ value. That behavior can only be explained by the activity coefficient of $\mathrm{H}_{3} \mathrm{O}^{+} \left(\gamma_{\mathrm{H}_{3} \mathrm{O}^{+}}^{* / \widetilde{m}}\right)$ instead of only by the acid concentration. Further, the experimentally determined pH from the literature was used in this work to verify the consistent use of $p H$.

In contrast to the shown examples in Fig. 4, aqueous electrolyte solutions containing a carbonate salt, e.g., $\mathrm{K}_{2} \mathrm{CO}_{3}$, highly influence pH due to the basic characteristics of the $\mathrm{CO}_{3}^{2-}$ ion and, consequently, the corresponding dissociation reactions (R2) and (R3). Thus, in contrast to all other salts considered here, the dissociation reactions strongly influence $\mathrm{CO}_{2}$ solubility. Since a carbonate salt intrinsically contains a carbonic acid species, a distinction was introduced between the $\mathrm{CO}_{2}$, which was added in the solubility experiment through pressurizing the system with $\mathrm{CO}_{2}$, and the $\mathrm{CO}_{2}$ species that was introduced into the system by the carbonate salt. Please note that this distinction is not required for bicarbonate salts as these do not critically shift pH , and dissociation reactions (R2) and (R3) did not play crucial roles. For carbonate salts, an element balance regarding carbon (C), oxygen (O), and hydrogen (H) was applied. Consequently, the mole fraction of the additionally dissolved $\mathrm{CO}_{2}$ in the aqueous carbonate solution, due to pressurizing the system with $\mathrm{CO}_{2}$ until equilibrium was reached, was calculated according to Eq. (24).

$$
\begin{equation*}
x_{\mathrm{CO}_{2}}^{\text {inserted }}=\frac{n_{\mathrm{CO}_{2}}}{n_{\mathrm{CO}_{2}}+n_{\mathrm{H}_{2} \mathrm{O}}+n_{\mathrm{Cat}_{2}^{+} \mathrm{CO}_{3}}}=\frac{x_{\mathrm{CO}_{2}}+x_{\mathrm{CO}_{3}^{2-}}+x_{\mathrm{HCO}_{3}^{-}}-0.5 x_{\mathrm{Cat}^{+}}}{x_{\mathrm{CO}_{2}}+x_{\mathrm{CO}_{3}^{2-}}+1.5 x_{\mathrm{HCO}_{3}^{-}}+x_{\mathrm{H}_{2} \mathrm{O}}+0.5\left(x_{\mathrm{H}^{+}}+x_{\mathrm{OH}^{-}}\right)} \tag{24}
\end{equation*}
$$


\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-08.jpg?height=686&width=1489&top_left_y=180&top_left_x=292}
\captionsetup{labelformat=empty}
\caption{Fig. 4. i) $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the NaCl molality at $\mathrm{T}=323 \mathrm{~K}$ and $\mathrm{p}=62.4$ bar. Symbols represent experimental data from Hou et al. [98]. ii) pH plotted against the NaCl molality at $\mathrm{T}=323 \mathrm{~K}$ and $\mathrm{p}=62.4$ bar. Symbols represent experimental data from Peng et al. [96]. Lines represent predictions obtained with ePC-SAFT advanced using parameters from Tables 1-3 and 6.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-08.jpg?height=666&width=830&top_left_y=1104&top_left_x=176}
\captionsetup{labelformat=empty}
\caption{Fig. 5. $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the pressure at constant temperature $\mathrm{T}=313.15 \mathrm{~K}$. Symbols represent experimental data from the literature (solid squares: salt-free system from Kiepe et al. [95], solid stars: $0.42 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{~K}_{2} \mathrm{CO}_{3}$ from Kamps et al. [100], and solid circles: $1.71 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{~K}_{2} \mathrm{CO}_{3}$ from Kamps et al. [100]). Lines represent predictions (solid line: salt-free system, dash-dotted line: $0.42 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{~K}_{2} \mathrm{CO}_{3}$ neglecting the dissociation reactions (R2) and (R3), dash-double-dotted line: $1.71 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{~K}_{2} \mathrm{CO}_{3}$ neglecting the dissociation reactions (R2) and (R3), dashed line: $0.42 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{~K}_{2} \mathrm{CO}_{3}$ including the dissociation reactions (R2) and (R3) by applying Eq. (24), and dotted line: $1.71 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{~K}_{2} \mathrm{CO}_{3}$ including the dissociation reactions (R2) and (R3) by applying Eq. (24)) obtained with ePC-SAFT advanced using parameters from Tables 1, 2, 3 and 6.}
\end{figure}

In Eq. (24), $x_{\mathrm{CO}_{2}}^{\text {inserted }}$ denotes the mole fraction of dissolved $\mathrm{CO}_{2}$, which was added due to pressurizing the aqueous carbonate solution with $\mathrm{CO}_{2}$. $n_{\mathrm{CO}_{2}}$ denotes the molar number of $\mathrm{CO}_{2}$ molecules while subtracting the moles of $\mathrm{CO}_{2}$ which were already intrinsically inside the carbonate salt as $\mathrm{CO}_{3}^{2-}$ species ( $0.5 x_{\mathrm{Cat}^{+}}$). $n_{\mathrm{H}_{2} \mathrm{O}}$ and $n_{\mathrm{Cat}_{2}^{+} \mathrm{CO}_{3}}$ are the molar number of water and carbonate salt that were present in the liquid phase after equilibration, respectively. The stoichiometric coefficients for $x_{\mathrm{HCO} 3}^{-}$, $x_{\mathrm{H}^{+}}$, and $x_{\mathrm{OH}^{-}}$result from the corresponding element balance while simultaneously accounting for the dissociation reactions (R1) - (R3).

Fig. 5 shows the predictions calculated with ePC-SAFT advanced for the $\mathrm{CO}_{2}$ solubility in aqueous $\mathrm{K}_{2} \mathrm{CO}_{3}$ solutions.

In Fig. 5, the influence of carbonate salt on $\mathrm{CO}_{2}$ solubility is illustrated. The experimental data show that the $\mathrm{CO}_{2}$ solubility increases with the carbonate molality. This observation is entirely different from the salting-out behavior of all other salts studied in this work. This is due to the dissociation reactions (R2) and (R3) that influence the $\mathrm{CO}_{2}$ solubility caused by the $p H$ shift induced upon carbonate addition. Further, it is possible to differentiate between the $\mathrm{CO}_{2}$ solubility that is induced physically by carbonate and the $\mathrm{CO}_{2}$ solubility that is induced by the pH shift. Without dissociation reactions in the liquid phase, $\mathrm{K}_{2} \mathrm{CO}_{3}$ causes a salting-out effect on the $\mathrm{CO}_{2}$ solubility, which is illustrated in Fig. 5. This does not describe the experimental data at all. Thus, only accounting for the dissociation reactions (R2) and (R3) allows counterbalancing the salting-out effect of the carbonate, shifts pH due to the $\mathrm{CO}_{3}^{2-}$ present in the liquid phase, and finally increases the $\mathrm{CO}_{2}$ solubility to an extent that correctly matched the experimental data (Fig. 5). This effect is well known in carbon-capture processes and sour-gas absorption, cf. ref. [23], where an amine is added to the solvent mixture to increase the capability to dissolve more sour-gas/ $\mathrm{CO}_{2}$ (salting-in).
4.2.3.2. Cation-specific influence on $\mathrm{CO}_{2}$ solubility. The strength of the salting-out effect on $\mathrm{CO}_{2}$ solubility depends on the nature of both, cations and anions. Fig. 6 shows an overview of all $\mathrm{CO}_{2}+$ water + chloride salt ( $\mathrm{NaCl}, \mathrm{KCl}, \mathrm{CsCl}, \mathrm{MgCl}_{2}$, and $\mathrm{CaCl}_{2}$ ) systems investigated in this work.

Fig. 6 shows the $\mathrm{CO}_{2}$ solubility in different aqueous chloride solutions, which allows studying the cation-specific effect ( $\mathrm{Na}^{+} / \mathrm{K}^{+} / \mathrm{Cs}^{+} / \mathrm{Mg}^{2+} / \mathrm{Ca}^{2+}$ ) on $\mathrm{CO}_{2}$ solubility. The salting-out effect increases in the order $\mathrm{Cs}^{+}<\mathrm{K}^{+}<\mathrm{Na}^{+}<\mathrm{Ca}^{2+} \approx \mathrm{Mg}^{2+}$, as previously discussed [24]. This order perfectly coincides with the charge densities of the investigated ions. The $\mathrm{Cs}^{+}$ion has the lowest charge density, and the $\mathrm{Mg}^{2+}$ ion has the highest charged density among all investigated cations. Thus, $\mathrm{Cs}^{+}$ showed the lowest salting-out effect, while $\mathrm{Mg}^{2+}$ showed the highest salting-out effect on $\mathrm{CO}_{2}$ solubility.
4.2.3.3. Anion-specific influence on $\mathrm{CO}_{2}$ solubility. Next, the anionspecific influence on $\mathrm{CO}_{2}$ solubility is discussed. Fig. 7 shows an overview of all $\mathrm{CO}_{2}+$ water + sodium salt $\left(\mathrm{NaCl}, \mathrm{NaNO}_{3}, \mathrm{NaHCO}_{3}\right.$, and $\mathrm{Na}_{2} \mathrm{SO}_{4}$ ) systems investigated in this work. The salting-out effect increases in the order $\mathrm{HCO}_{3}^{-} \approx \mathrm{NO}_{3}^{-}<\mathrm{Cl}^{-}<\mathrm{SO}_{4}^{2-}$, and the results are also correlated with charge density, which is highest for the sulfate among

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-09.jpg?height=686&width=866&top_left_y=189&top_left_x=144}
\captionsetup{labelformat=empty}
\caption{Fig. 6. $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the pressure at constant temperature $\mathrm{T}=373.15 \mathrm{~K}$ and constant salt molality of $5 \mathrm{~mol} \mathrm{~kg}^{-1}$, except for KCl (solid stars), where only data at $4 \mathrm{~mol} \mathrm{~kg}^{-} { }^{1}$ were available. Symbols represent experimental data from the literature (solid circles: salt-free system from Yan et al. [97], solid stars: KCl from Hou et al. [98], solid diamonds: NaCl from Yan et al. [97], solid down-triangles: $\mathrm{CaCl}_{2}$ from Tong et al. [101], and solid squares: $\mathrm{MgCl}_{2}$ from Tong et al. [101]). Lines represent predictions at constant salt molality of $5 \mathrm{~mol} \mathrm{~kg}^{-1}$ (solid line: salt-free system, dashed line: CsCl , short-dash-dotted line: KCl , long-dash-dotted line: NaCl , dotted line: $\mathrm{CaCl}_{2}$, and dash-double dotted line: $\mathrm{MgCl}_{2}$ ) obtained with ePC-SAFT advanced using parameters from Tables 1-3 and 6.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-09.jpg?height=658&width=869&top_left_y=1330&top_left_x=139}
\captionsetup{labelformat=empty}
\caption{Fig. 7. $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the pressure at constant temperature $\mathrm{T}=313.15 \mathrm{~K}$ and constant salt molality of $1 \mathrm{~mol} \mathrm{~kg}^{-1}$. Symbols represent experimental data from the literature (solid squares: salt-free system from Kiepe et al. [95], solid diamonds: $\mathrm{NaNO}_{3}$ from Kiepe et al. [102], solid circles: $\mathrm{NaHCO}_{3}$ from Han et al. [103], and solid hexagons: $\mathrm{Na}_{2} \mathrm{SO}_{4}$ from Rumpf et al. [104]). Lines represent predictions at constant salt molality of $1 \mathrm{~mol} \mathrm{~kg}^{-1}$ (dash-dotted line: salt-free system, solid line: $\mathrm{NaNO}_{3}$, dashed line: $\mathrm{NaHCO}_{3}$, dotted line: NaCl , and dash-double-dotted line: $\mathrm{Na}_{2} \mathrm{SO}_{4}$ ) obtained with ePC-SAFT advanced using parameters from Tables 1-3 and 6.}
\end{figure}
the studied anions. $\mathrm{CO}_{3}^{2-}$ itself would theoretically fit in the salting-out series; however, due to the above-discussed pH shift of the carbonates, $\mathrm{CO}_{3}^{2-}$ apparently acts as a salting-in agent.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-09.jpg?height=674&width=868&top_left_y=183&top_left_x=1070}
\captionsetup{labelformat=empty}
\caption{Fig. 8. $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions in mole fraction plotted against the pressure for varying temperatures from $\mathrm{T}=309 \mathrm{~K}$ to $\mathrm{T}=424 \mathrm{~K}$. The molalities of NaCl ( $0.910 \mathrm{~mol} \mathrm{~kg}^{-1}$ ) and KCl ( $0.143 \mathrm{~mol} \mathrm{~kg}^{-1}$ ) were kept constant for all shown data points. Symbols represent experimental data from Tong et al. [101] (solid circles: 309 K , solid squares: 324 K ; solid up-triangles: 343 K , solid diamonds: 374 K , and solid hexagons: 424 K ). Lines represent predictions (solid line: 309 K , dash-dotted line: 324 K , dotted line: 343 K , dashed line: 374 K , and dash-double-dotted line: 424 K ) obtained with ePC-SAFT advanced using parameters from Tables 1-3 and 6.}
\end{figure}

\section*{4.3. $\mathrm{CO}_{2}+$ water + salt mixture}
$\mathrm{CO}_{2}$ solubility data are available in aqueous electrolyte solutions containing two salts $(\mathrm{NaCl}+\mathrm{KCl})$. Fig. 8 shows the predictions obtained with ePC-SAFT advanced compared to literature data for the system CO2 + water $+\mathrm{NaCl}+\mathrm{KCl}$ with a total ionic strength of $1.053 \mathrm{~mol} \mathrm{~kg}^{-1}$.

It can be observed that predictions obtained with ePC-SAFT advanced are in excellent agreement with the given literature data over a broad temperature range up to 424 K . This demonstrates the strength of the ion-based modeling approach with ePC-SAFT advanced. The corresponding ARSD and AARD values are listed in Table S27 in the SI.

\section*{4.4. $\mathrm{CO}_{2}+$ water + organic solvent}

The previous section showed that ePC-SAFT advanced was able to model the $\mathrm{CO}_{2}$ solubility in both, organic solvents and in aqueous electrolyte solutions. Hence, ePC-SAFT advanced was applied further to systems containing solvent mixtures, namely $\mathrm{CO}_{2}+$ water + methanol/ ethanol, cf. Tables S28 and S29 in the SI for ARSD and AARD values. Fig. 9 shows the $\mathrm{CO}_{2}$ solubility in a solvent mixture of water + methanol with different $\mathrm{CO}_{2}$-free molar ratios between the two solvents.

It is vivid to see that predictions obtained with ePC-SAFT advanced are in excellent agreement with the given literature data. The influence of methanol-water solvent mixtures on the $\mathrm{CO}_{2}$ solubility is clearly visible, as already described in the previous section. With an increasing mole fraction of methanol, the $\mathrm{CO}_{2}$ solubility is highly increased. At a mole fraction of $x_{\text {methanol }}=0.5$, the $\mathrm{CO}_{2}$ solubility is up to six times higher than in pure water (depending on pressure and temperature). The predictions for the system $\mathrm{CO}_{2}+$ water + ethanol are shown in Fig. S11 in the SI.

\section*{4.5. $\mathrm{CO}_{2}+$ water + organic solvent + salt}

The mixtures considered in the previous sections were further enhanced to even more complex systems. Here, CO2 solubilities are shown in a solvent mixture with additional salt: $\mathrm{CO}_{2}+$ water +

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-10.jpg?height=701&width=858&top_left_y=193&top_left_x=146}
\captionsetup{labelformat=empty}
\caption{Fig. 9. $\mathrm{CO}_{2}$ solubility in mole fraction plotted against the pressure in varying $\mathrm{CO}_{2}$-free mole fractions of methanol and water at constant temperature $\mathrm{T}=395$ K. Symbols represent literature data from Xia et al. [84], and lines represent predictions (solid circles and upper-solid line: $x_{\text {methanol }}=1$, solid stars and short-dotted line: $x_{\text {methanol }}=0.95$, solid hexagons and short-dashed line: $x_{\text {methanol }} =0.9$, solid diamonds and dash-double-dotted line: $x_{\text {methanol }}=0.75$, solid down-triangles and dash-dotted line: $x_{\text {methanol }}=0.5$, solid up-triangles and dotted line: $x_{\text {methanol }}=0.25$, solid squares and dashed line: $x_{\text {methanol }}=0.1$, and lower-solid line: $x_{\text {methanol }}=0$ ) obtained with ePC-SAFT advanced using parameters from Tables 1, 2, 4 and 6.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-10.jpg?height=723&width=866&top_left_y=1319&top_left_x=142}
\captionsetup{labelformat=empty}
\caption{Fig. 10. $\mathrm{CO}_{2}$ solubility in mole fraction plotted against the pressure at given $\mathrm{CO}_{2}$-free methanol mole fractions in solvent mixture (methanol and water) and at varying salt molalities ( NaCl ) at $\mathrm{T}=393.15 \mathrm{~K}$. Symbols represent experimental data from the literature, and lines represent predictions (solid line: saltfree system with $x_{\text {methanol }}=1$, solid down-triangles from Xia et al. [84] and dashed line: salt-free system with $x_{\text {methanol }}=0.75$, solid squares from Kamps et al. [105] and short-dashed line: $x_{\text {methanol }}=0.75$ with $0.25 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{NaCl}$, solid hexagons from Xia et al. [84] and dash-double-dotted line: salt-free system with $x_{\text {methanol }}=0.5$, solid diamonds from Kamps et al. [105] and dotted line: $x_{\text {methanol }}=0.5$ with $0.7 \mathrm{~mol} \mathrm{~kg}^{-1} \mathrm{NaCl}$, and dash-dotted line: salt-free system with $x_{\text {methanol }}=0$ ) obtained with ePC-SAFT advanced using parameters from Tables 1-4 and 6.}
\end{figure}
methanol +NaCl , and $\mathrm{CO}_{2}+$ water + ethanol +CsCl . Fig. 10 compares experimental $\mathrm{CO}_{2}$ solubilities in the mixture water + methanol +NaCl with ePC-SAFT advanced predictions.

Fig. 10 shows that predictions obtained with ePC-SAFT advanced satisfactorily match the literature data. Thus, the model correctly predicts the combined influence of solvent mixtures and the salting-out effect of the ions on the $\mathrm{CO}_{2}$ solubility. Increasing the mole fraction of methanol increases the $\mathrm{CO}_{2}$ solubility, while the addition of NaCl decreases the $\mathrm{CO}_{2}$ solubility in the solvent mixture.

More modeling results with varying solvent compositions and salt molalities up to $2 \mathrm{~mol} \mathrm{~kg}^{-1}$ are listed in Table S30 in the SI.

Further, new experimental data for $\mathrm{CO}_{2}$ solubility in aqueous and organic electrolyte solutions containing $\mathrm{Cs}^{+}$were measured in this work. The new experimental data are listed in Table S31 in the SI together with validation experiments with well-known systems, the corresponding standard uncertainties $(u)$ of the measurements, the ARSD and the $A A R D$. Fig. 11 shows the new experimental data and the according ePCSAFT advanced predictions.

The ePC-SAFT advanced predicted CO2 solubility coincides very well with the experimentally obtained values. Moreover, the salting-out effect of the $\mathrm{Cs}^{+}$ion in comparison to the $\mathrm{Na}^{+}$ions becomes obvious for the first time. Due to the lower charge density of the $\mathrm{Cs}^{+}$ion, the saltingout effect of CsCl is expected to be lower compared to NaCl , and this is what has also been measured and modeled as shown in Fig. 11. This observation corroborates the findings from cation-specific influence on $\mathrm{CO}_{2}$ solubility, where $\mathrm{Cs}^{+}$showed the lowest salting-out effect.

In the following, all the findings are summed up:
\# solvent influence on $\mathrm{CO}_{2}$ solubility: $\mathrm{CO}_{2}$ solubility is very high in non-polar solvents (e.g., THF), while the $\mathrm{CO}_{2}$ solubility is relatively poor in water among all investigated solvents.
\# ion-specific influence on $\mathrm{CO}_{2}$ solubility: The charge density of the ions crucially dictates the salting-out behavior on $\mathrm{CO}_{2}$ solubility. $\mathrm{Cs}^{+}$ showed the lowest salting-out effect compared to all investigated cations, while divalent cations, e.g., $\mathrm{Mg}^{2+}$, showed the highest salting-out

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/346f0c05-f525-4cee-972c-53818bbdc83c-10.jpg?height=675&width=864&top_left_y=1485&top_left_x=1074}
\captionsetup{labelformat=empty}
\caption{Fig. 11. $\mathrm{CO}_{2}$ solubility in mole fraction plotted against the pressure in varying $\mathrm{CO}_{2}$-free solvent mole fractions (ethanol and water) and varying salt molalities $(\mathrm{NaCl}$ or CsCl$)$ at constant temperature $\mathrm{T}=323.15 \mathrm{~K}$. Symbols represent experimental data measured in this work, and lines represent predictions (solid circle and solid line: salt-free system $x_{\text {ethanol }}=1$; solid pentagons and dotted line: salt-free system $x_{\text {ethanol }}=0.75$; solid squares and short-dashed line: $x_{\text {ethanol }} =0.75$ with $0.3 \mathrm{~mol} \mathrm{~kg}{ }^{-1} \mathrm{CsCl}$; solid diamonds and dashed line: salt-free system $x_{\text {ethanol }}=0.5$; solid triangles and dash-double-dotted line: $x_{\text {ethanol }}=0.5$ with 0.8 $\mathrm{mol} \mathrm{kg}{ }^{-1} \mathrm{CsCl}$; solid hexagons and dash-dotted line: $x_{\text {ethanol }}=0.5$ with 0.8 mol $\mathrm{kg}^{-1} \mathrm{NaCl}$; and short-dotted line: salt-free system $x_{\text {ethanol }}=0$ ) obtained with ePC-SAFT advanced using parameters from Tables 1-4 and 6. Standard uncertainties $u$ of the experimental data can be found in Table S31 in the SI.}
\end{figure}
effect. This was also observed for the anions, i.e., $\mathrm{NO}_{3}^{-}$showed the lowest salting-out effect, while $\mathrm{SO}_{4}^{2-}$ showed the highest salting-out effect among all investigated anions.
\# ePC-SAFT advanced was able to predict the $\mathrm{CO}_{2}$ solubility in various aqueous electrolyte solutions, and no additional adjustable model parameters were necessary to match the experimental data satisfactorily. In comparison to previous works, this is the first time that an electrolyte model was applied in a fully predictive mode to $\mathrm{CO}_{2}$ solubility in aqueous solutions.
\# pH effects on CO2 solubility were investigated in detail. A previous work by Ascani et al. [17] served as the starting point for this investigation. As a result, both, the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions and the corresponding pH in the equilibrated liquid phase were predicted in excellent agreement with the literature data. Again, these results showed the soundness of the modeling approach and the applied thermodynamic equilibrium constants for the dissociation reactions of carbonic acid. Among all investigated salts, carbonate salts are the only salts that increased the $\mathrm{CO}_{2}$ solubility, while all other salts decreased the $\mathrm{CO}_{2}$ solubility due to salting-out effects. Although the $\mathrm{CO}_{3}^{2-}$ ion itself shows salting-out behavior, this effect is counterbalanced by the dissociation equilibrium and the subsequent $p H$ shift due to the basic characteristics of carbonate salts.
\# Multi-component mixtures: Apart from these fundamental studies, the gained knowledge was finally applied to predict $\mathrm{CO}_{2}$ solubility in complex mixtures, i.e., mixtures comprised of either a salt mixture, a solvent mixture, or a combination of a solvent mixture with additional salt. In all mixtures under study, ePC-SAFT advanced was able to predict the $\mathrm{CO}_{2}$ solubility with outstanding accuracy. This proves the predictive capability of the model. ePC-SAFT advanced significantly allows reducing the experimental effort regarding solvent selection and salt selection or a combination of both. In sum, the experimental effort to screen for suitable combinations of solvent + salt and high $\mathrm{CO}_{2}$ solubilities regarding an involved reaction or chemical process, e.g., carboncapture processes, is significantly reduced.

\section*{5. Conclusion}

In the present work, the thermodynamic electrolyte model ePC-SAFT advanced was applied to model the $\mathrm{CO}_{2}$ solubility in organic solvents and predict the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions. In addition, more complex systems comprised of salt mixtures, solvent mixtures, or a combination of both, a solvent mixture with additional salt, were studied.

As a remarkable result, ePC-SAFT advanced was able to predict the $\mathrm{CO}_{2}$ solubility in aqueous electrolyte solutions over a broad range of conditions, i.e., high temperatures, high pressures, and high salt concentrations, without fitting any new model parameters to experimental data. In general, the modeling accuracy is within an $A A R D$ of about $10 \%$ with respect to the experimental data. This is more than acceptable concerning the fact that the modeling results are predictions in a sense that non $\mathrm{CO}_{2}$-ion interactions were fitted at all to experimental data, which is remarkable since no other known work predicted the $\mathrm{CO}_{2}$ solubility in these systems and needed additional fitting parameters, cf. Pabsch et al. [24]. All pure-component parameters and the pure-component parameters of the ions were inherited from the literature. Further, binary interaction parameters between ion - ion, solvent solvent, and ion - solvent were already available from the literature, and only binary interaction parameters between $\mathrm{CO}_{2}$ - solvent were determined in this work by fitting to binary data from the literature.That is, this is the first work that shows fully predictive capability, as ion- $\mathrm{CO}_{2}$ binary interaction corrections were not used at all $\left(k_{i j}\left(\right.\right.$ ion- $\left.\left.\mathrm{CO}_{2}\right)=0\right)$. Further, $p H$ effects were studied in more detail based on a previous work by Ascani et al. [17]. Therein, the $p H$ was correctly predicted by ePC-SAFT advanced, which again proves the modeling accuracy and the accurate description of the involved dissociation reaction of the carbonic acid. In this work, carbonate salts were found to be a special case since
carbonate salts are of basic character, and the pH was strongly shifted to high $p H$ values. Thus, the $\mathrm{CO}_{2}$ solubility increased with increasing molality of the carbonate salt due to shift in pH . This was observed for carbonate salts only. All other salts investigated in this work showed salting-out behavior and consequently decreased the $\mathrm{CO}_{2}$ solubility with increasing salt molality, and usually, a decreasing pH is observed as well. However, the $\mathrm{CO}_{3}^{2-}$ ion itself also showed a salting-out effect on the $\mathrm{CO}_{2}$ solubility, but the $p H$ shift completely counterbalanced this effect, resulting in an effective salting-in on $\mathrm{CO}_{2}$.

Finally, more complex systems comprised of either salt mixtures, solvent mixtures, or a combination of both, a solvent mixture with additional salt, were investigated. Therein, ePC-SAFT advanced proved its predictive behavior, as all investigated systems were predicted without fitting any new model parameters. In conclusion, ePC-SAFT advanced provides a robust modeling framework that significantly reduces the experimental effort towards solvent selection and salt selection for high $\mathrm{CO}_{2}$ solubilities in a specific reaction mixture or a desired chemical process.

\section*{CRediT authorship contribution statement}

Daniel Schick: Investigation, Validation, Formal analysis, Writing original draft, Conceptualization, Methodology. Lena Bierhaus: Methodology, Formal analysis. Alexander Strangmann: Methodology, Formal analysis. Paul Figiel: Methodology, Software. Gabriele Sadowski: Conceptualization, Methodology, Project administration, Writing - review \& editing, Supervision. Christoph Held: Conceptualization, Methodology, Project administration, Writing - review \& editing, Supervision.

\section*{Declaration of Competing Interest}

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

\section*{Data availability}
the data is in the article and in the supplement

\section*{Acknowledgment}

The authors acknowledge funding from the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany's Excellence Strategy - EXC 2033 - project number 390677874. Translation into German required:" Gefördert durch die Deutsche Forschungsgemeinschaft (DFG) im Rahmen der Exzellenzstrategie des Bundes und der Länder - EXC 2033 - Projektnummer 390677874 RESOLV.

\section*{Supplementary materials}

Supplementary material associated with this article can be found, in the online version, at doi:10.1016/j.fluid.2022.113714.

\section*{References}
[1] M. Ascani, G. Sadowski, C. Held, Calculation of multiphase equilibria containing mixed solvents and mixed electrolytes: general formulation and case studies, J. Chem. Eng. Data (2022).
[2] A. Fukumoto, P. Paricaud, D. Dalmazzone, W. Bouchafaa, T.T.-S. Ho, W. Fürst, Modeling the dissociation conditions of carbon dioxide + TBAB, TBAC, TBAF, and TBPB semiclathrate hydrates, J. Chem. Eng. Data 59 (2014) 3193-3204.
[3] H. Jiang, A.Z. Panagiotopoulos, I.G. Economou, Modeling of CO2 solubility in single and mixed electrolyte solutions using statistical associating fluid theory, Geochimica et Cosmochimica Acta 176 (2016) 185-197.
[4] L. Sun, X. Liang, N. Solms von, G.M. Kontogeorgis, Thermodynamic modeling of gas solubility in aqueous solutions of quaternary ammonium salts with the e-CPA equation of state, Fluid Phase Equilibria. 507 (2020), 112423.
[5] P.J. Carvalho, L.M. Pereira, N.P. Gonçalves, A.J. Queimada, J.A. Coutinho, Carbon dioxide solubility in aqueous solutions of NaCl: Measurements and modeling with electrolyte equations of state, Fluid Phase Equilibria. 388 (2015) 100-106.
[6] S. Chabab, P. Théveneau, J. Corvisier, C. Coquelet, P. Paricaud, C. Houriez, E. E. Ahmar, Thermodynamic study of the $\mathrm{CO} 2-\mathrm{H} 2 \mathrm{O}-\mathrm{NaCl}$ system: measurements of CO2 solubility and modeling of phase equilibria using Soreide and Whitson, electrolyte CPA and SIT models, Int. J. Greenhouse Gas Contr. 91 (2019), 102825.
[7] M. Kohns, G. Lazarou, S. Kournopoulos, E. Forte, F.A. Perdomo, G. Jackson, C. S. Adjiman, A. Galindo, Predictive models for the phase behaviour and solution properties of weak electrolytes: nitric, sulphuric, and carbonic acids, Phys. Chem. Chem. Phys.: PCCP 22 (2020) 15248-15269.
[8] Y. Li, Z. Qiao, S. Sun, T. Zhang, Thermodynamic modeling of CO2 solubility in saline water using NVT flash with the cubic-Plus-association equation of state, Fluid Phase Equilibria. 520 (2020), 112657.
[9] V. Papaioannou, F. Calado, T. Lafitte, S. Dufal, M. Sadeqzadeh, G. Jackson, C. S. Adjiman, A. Galindo, Application of the SAFT- $\gamma$ Mie group contribution equation of state to fluids of relevance to the oil and gas industry, Fluid Phase Equilibria. 416 (2016) 104-119.
[10] R.D. Springer, Z. Wang, A. Anderko, P. Wang, A.R. Felmy, A thermodynamic model for predicting mineral reactivity in supercritical carbon dioxide: I. Phase behavior of carbon dioxide-water-chloride salt systems across the H 2 O -rich to the CO2-rich regions, Chem. Geol. 322-323 (2012) 151-171.
[11] Kaur, H.; Abedi, S.; Chen, C.-C. Estimating CO 2 solubility in aqueous $\mathrm{Na}+-\mathrm{K}+$ -Mg 2+-Ca 2+-Cl--SO 42- solutions with electrolyte NRTL-PC-SAFT model. J. Chem. Eng. Data [Online early access]. DOI: 10.1021/acs.jced.1c00950.
[12] N. Novak, G.M. Kontogeorgis, M. Castier, I.G. Economou, Modeling of gas solubility in aqueous electrolyte solutions with the eSAFT-VR Mie equation of state, Ind. Eng. Chem. Res. 60 (2021) 15327-15342.
[13] M.B. Oliveira, A.J. Queimada, G.M. Kontogeorgis, J.A. Coutinho, Evaluation of the CO2 behavior in binary mixtures with alkanes, alcohols, acids and esters using the Cubic-Plus-Association Equation of State, J. Supercriti. Fluid. 55 (2011) 876-892.
[14] T. Kristanto, P.-S. Tsai, A.H. Tiwikrama, M.-J. Lee, Vapor-liquid equilibrium phase behavior of binary systems of carbon dioxide with dimethyl succinate or dimethyl glutarate, J. Taiwan Instit. Chem. Eng. 136 (2022), 104402.
[15] Y. Gao, Q. Shang, S. Xia, Experiment and model for solubility of CO2 in alkanes with ethyl acetate as cosolvent, J. Chem. Thermodyn. 168 (2022), 106741.
[16] S. Ahmed, N. Ferrando, J.-C. Hemptinne, J.-P. de; Simonin, O. Bernard, O. Baudouin, Modeling of mixed-solvent electrolyte systems, Fluid Phase Equilibria. 459 (2018) 138-157.
[17] M. Ascani, D. Pabsch, M. Klinksiek, N. Gajardo-Parra, G. Sadowski, C. Held, Prediction of pH in multiphase multicomponent systems with ePC-SAFT advanced, Chem. Commun. 58 (2022) 8436.
[18] L.F. Cameretti, G. Sadowski, J.M. Mollerup, Modeling of aqueous electrolyte solutions with perturbed-chain statistical associated fluid theory, Ind. Eng. Chem. Res. 44 (2005) 3355-3362.
[19] C. Held, T. Reschke, S. Mohammad, A. Luza, G. Sadowski, ePC-SAFT revised, Chem. Eng. Res. Des. 92 (2014) 2884-2897.
[20] M. Bülow, M. Ascani, C. Held, ePC-SAFT advanced - Part I: Physical meaning of including a concentration-dependent dielectric constant in the born term and in the Debye-Hückel theory, Fluid Phase Equilibria. 535 (2021), 112967.
[21] M. Bülow, M. Ascani, C. Held, ePC-SAFT advanced - Part II: application to salt solubility in ionic and organic solvents and the impact of ion pairing, Fluid Phase Equilibria. 537 (2021), 112989.
[22] D. Pabsch, P. Figiel, G. Sadowski, C. Held, Solubility of electrolytes in organic solvents: solvent-specific effects and ion-specific effects, J. Chem. Eng. Data 67 (2022) 2706-2718.
[23] M. Bülow, N. Gerek Ince, S. Hirohama, G. Sadowski, C. Held, Predicting vapor-liquid equilibria for sour-gas absorption in aqueous mixtures of chemical and physical solvents or ionic liquids with ePC-SAFT, Ind. Eng. Chem. Res. 60 (2021) 6327-6336.
[24] D. Pabsch, C. Held, G. Sadowski, Modeling the CO2 solubility in aqueous electrolyte solutions using ePC-SAFT, J. Chem. Eng. Data 65 (2020) 5768-5777.
[25] D. Li, Z. Duan, The speciation equilibrium coupling with phase equilibrium in the $\mathrm{H} 2 \mathrm{O}-\mathrm{CO} 2-\mathrm{NaCl}$ system from 0 to $250^{\circ} \mathrm{C}$, from 0 to 1000 bar, and from 0 to 5 molality of NaCl, Chem. Geol. 244 (2007) 730-751.
[26] V. Gold, The IUPAC Compendium of Chemical Terminology, International Union of Pure and Applied Chemistry (IUPAC): Research Triangle Park, NC, 2019.
[27] J. Gross, G. Sadowski, Perturbed-Chain SAFT: an equation of state based on a perturbation theory for chain molecules, Ind. Eng. Chem. Res. 40 (2001) 1244-1260.
[28] J. Gross, G. Sadowski, Application of the perturbed-chain SAFT equation of state to associating systems, Ind. Eng. Chem. Res. 41 (2002) 5510-5515.
[29] J. Gross, J. Vrabec, An equation-of-state contribution for polar components: dipolar molecules, AIChE J 52 (2006) 1194-1204.
[30] P. Debye, E. Hückel, Zur Theorie der Elektrolyte: I. Gefrierpunktserniedrigung und verwandte Erscheinungen, Physikalische Zeitschrift 24 (1923) 185-206.
[31] M. Born, Volumen und Hydratationswärme der Ionen, Z. Physik 1 (1920) 45-48.
[32] D. Fuchs, J. Fischer, F. Tumakaka, G. Sadowski, Solubility of amino acids: influence of the pH value and the addition of alcoholic cosolvents on aqueous solubility, Ind. Eng. Chem. Res. 45 (2006) 6578-6584.
[33] Vogelpohl, C. Measuring and Modeling High-Pressure Gas Solubility in Temperature Modulated Solvent Systems. Dissertation, Technische Universität Dortmund; Verlag Dr. Hut.
[34] A. Wangler, M. Jonathan Bunse, G. Sadowski, C. Held, Thermodynamic activitybased Michaelis constants, in: C. Fernandez, L., Rajendran (Eds.), Kinetics of Enzymatic Synthesis, IntechOpen: Erscheinungsort nicht ermittelbar, 2019.
[35] O. Riechert, M. Husham, G. Sadowski, T. Zeiner, Solvent effects on esterification equilibria, AIChE J. 61 (2015) 3000-3011.
[36] M. Kleiner, J. Gross, An equation of state contribution for polar components: polarizable dipoles, AIChE J. 52 (2006) 1951-1961.
[37] M. Klajmon, K. Rehák, P. Morávek, M. Matoušová, Binary liquid-liquid equilibria of $\gamma$-valerolactone with some hydrocarbons, J. Chem. Eng. Data 60 (2015) 1362-1370.
[38] Ascani, M.; Sadowski, G.; Held, C. Calculation of multiphase equilibria containing mixed solvents and mixed electrolytes: general formulation and case studies. J. Chem. Eng. Data [Online early access]. DOI: 10.1021/acs.jced.1c00866.
[39] L.F. Cameretti, G. Sadowski, Modeling of aqueous amino acid and polypeptide solutions with PC-SAFT, Chem. Eng. Process.: Process Intensificat. 47 (2008) 1018-1025.
[40] M. Kleiner, G. Sadowski, Modeling of polar systems using PCP-SAFT: an approach to account for induced-association interactions †, J. Phys. Chem. C 111 (2007) 15544-15553.
[41] B.H. Park, H.Y. Shin, B.-S. Lee, Effect of Lewis acid-base complexes between CO2 and alkanols on phase behavior at high pressure, J. CO2 Utiliz. 52 (2021), 101680.
[42] R.P. Lowndes, D.H. Martin, Dielectric constants of ionic crystals and their variations with temperature and pressure, Proc. R. Soc. Lond. A 316 (1970) 351-375.
[43] M. Ascani, C. Held, Prediction of salting-out in liquid-liquid two-phase systems with ePC-SAFT: Effect of the Born term and of a concentration-dependent dielectric constant, Z. Anorg. Allg. Chem. 647 (2021) 1305-1314.
[44] G. Leeke, R. Santos, B. Al-Duri, J. Seville, C. Smith, A.B. Holmes, Solubilities of 4phenyltoluene, phenylboric acid, biphenyl, and iodobenzene in carbon dioxide from measurements of the relative permittivity, J. Chem. Eng. Data 50 (2005) 1370-1374.
[45] JF Ely, WM Haynes, JW Magee. Thermophysical properties for special high CO2 content mixtures, 1987.
[46] H.H. Uhlig, F.G. Keyes, The dependence of the dielectric constants of gases on temperature and density, J. Chem. Phys. 1 (1933) 155-159.
[47] W.B. Floriano, M.A.C. Nascimento, Dielectric constant and density of water as a function of pressure at constant temperature, Braz. J. Phys. 34 (2004) 38-41.
[48] MT Khimenko, VV Aleksandrov, NN Gritsenko, Polarizability and radii of molecules of some pure liquids, Zh. Fiz. Khim (1973).
[49] R.M. Shirke, A. Chaudhari, N.M. More, P.B. Patil, Temperature dependent dielectric relaxation study of ethyl acetate - alcohol mixtures using time domain technique, J. Molecul. Liq. 94 (2001) 27-36.
[50] J. George, N.V. Sastry, Densities, viscosities, speeds of sound, and relative permittivities for water + cyclic amides (2-Pyrrolidinone, 1-Methyl-2-pyrrolidinone, and 1-Vinyl-2-pyrrolidinone) at different temperatures, J. Chem. Eng. Data 49 (2004) 235-242.
[51] J.F. Casteel, P.G. Sears, Dielectric constants, viscosities, and related physical properties of 10 liquid sulfoxides and sulfones at several temperatures, J. Chem. Eng. Data 19 (1974) 196-200.
[52] G. Ritzoulis, Excess properties of the binary liquid systems dimethylsulfoxide + isopropanol and propylene carbonate + isopropanol, Can. J. Chem. 67 (1989) 1105-1108.
[53] L. Jannelli, M. Pansini, Solid-liquid phase diagram and excess properties at 303.16 K and 313.16 K of dimethylsulfoxide (1) + sulfolane (2) binary system, J. Chem. Eng. Data 30 (1985) 428-431.
[54] H.L. Schläfer, W. Schaffernicht, Dimethylsulfoxyd als Lösungsmittel für anorganische Verbindungen, Angew. Chem. 72 (1960) 618-626.
[55] K. Izutsu, Electrochemistry in Nonaqueous Solutions, 2nd ed., John Wiley \& Sons Incorporated, Hoboken, 2009.
[56] C.J. Luo, E. Stride, M. Edirisinghe, Mapping the influence of solubility and dielectric constant on electrospinning polycaprolactone solutions, Macromolecules 45 (2012) 4669-4680.
[57] E.A.S. Cavell, P.C. Knight, M.A. Sheikh, Dielectric relaxation in non aqueous solutions. Part 2.-Solutions of tri(n-butyl)ammonium picrate and iodide in polar solvents, Trans. Faraday Soc. 67 (1971) 2225-2233.
[58] M. Nicolas, M. Malineau, R. Reich, The eyring significant structure theory applied to methanol-tetrahydrofuran mixtures, Phys. Chem. Liq. 10 (1980) 11-22.
[59] G.C. Greenacre, R.N. Young, Extrathermodynamic relationships for ion-pair equilibria in media of low dielectric constant, J. Chem. Soc., Perkin Trans 2 (1976) 874.
[60] L.G. Schornack, C.A. Eckert, Effect of pressure on the density and dielectric constant of polar solvents, J. Phys. Chem. 74 (1970) 3014-3020.
[61] N.M. Alpatova, Y.M. Kessler, Complex compounds of silicon, J. Struct. Chem. 5 (1965) 310-331.
[62] C. Carvajal, K.J. Tölle, J. Smid, M. Szwarc, Studies of solvation phenomena of ions and ion pairs in dimethoxyethane and tetrahydrofuran, J. Am. Chem. Soc. 87 (1965) 5548-5553.
[63] R.S. Holland, C.P. Smyth, Microwave adsorption and molecular structure in liquids. X. The relaxation times of nine heterocyclic molecules, J. Phys. Chem. 59 (1955) 1088-1092.
[64] F.E. Critchfield, J.A. Gibson, J.L. Hall, Dielectric constant and refractive index from 20 to $35^{\circ}$ and density at $25^{\circ}$ for the system tetrahydrofuran-water 1, J. Am. Chem. Soc. 75 (1953) 6044-6045.
[65] Y.M. Kessler, V.P. Emelin, A.I. Mishustin, P.S. Yastremskii, E.S. Verstakov, N. M. Alpatova, M.G. Fomicheva, K.V. Kireev, v.d. Gruba, R.K. Bratishko, Properties and structure of water and hexamethylphosphortriamide mixtures, J. Struct. Chem. 16 (1976) 739-747.
[66] S.J. Bass, W.I. Nathan, R.M. Meighan, R.H. Cole, Dielectric properties of alkyl amides. II. Liquid dielectric constant and loss, J. Phys. Chem. 68 (1964) 509-515.
[67] G.R. Leader, J.F. Gormley, The dielectric constant of N-methylamides, J. Am. Chem. Soc. 73 (1951) 5731-5733.
[68] U.M. Fornefeld-Schwarz, P. Svejda, Refractive indices and relative permittivities of liquid mixtures of $\gamma$-Butyrolactone, $\gamma$-Valerolactone, $\delta$-Valerolactone, or $\varepsilon$-Caprolactone + Benzene, + Toluene, or + Ethylbenzene at 293.15 K and 313.15 K and atmospheric pressure, J. Chem. Eng. Data 44 (1999) 597-604.
[69] S. Aparicio, R. Alcalde, Characterization of two lactones in liquid phase: an experimental and computational approach, Phys. Chem. Chem. Phys. 11 (2009) 6455-6467.
[70] A. Würflinger, Dielectric measurements at high pressures and low temperatures. II. The dielectric constant of acetonitrile, Berichte der Bunsengesellschaft für physikalische Chemie 84 (1980) 653-657.
[71] K.R. Srinivasan, R.L. Kay, The pressure dependence of the dielectric constant and density of acetonitrile at three temperatures, J. Solut. Chem. 6 (1977) 357-367.
[72] C. Moreau, G. Douhéret, Thermodynamic and physical behaviour of water + acetonitrile mixtures. Dielectric properties, J. Chem. Thermodyn. 8 (1976) 403-410.
[73] R. Philippe, A.M Piette, Recherches de Stoechiométrie VII(1) Contribution à l'étude de la constante diélectrique des composés organiques purs, Bull. Soc. Chim. Belges 64 (1955) 600-627.
[74] C. Andeen, J. Fontanella, D. Schuele, Low-frequency dielectric constant of LiF, NaF, NaCl, NaBr, KCl, and KBr by the method of substitution, Phys. Rev. B (1970) 5068-5073.
[75] M. Bülow, X. Ji, C. Held, Incorporating a concentration-dependent dielectric constant into ePC-SAFT. An application to binary mixtures containing ionic liquids, Fluid Phase Equilibria. 492 (2019) 26-33.
[76] C. Held, G. Sadowski, Manual 'ePC-SAFT 1.0', TU Dortmund: TU Dortmund, 2017.
[77] S. Dohrn, P. Reimer, C. Luebbert, K. Lehmkemper, S.O. Kyeremateng, M. Degenhardt, G. Sadowski, Thermodynamic modeling of solvent-impact on phase separation in amorphous solid dispersions during drying, Molecul. Pharmaceut. 17 (2020) 2721-2733.
[78] M. Görnert, G. Sadowski, Phase-equilibrium measurement and modeling of the PMMA/MMA/carbon dioxide ternary system, J. Supercriti. Fluid. 46 (2008) 218-225.
[79] C. Vogelpohl, C. Brandenbusch, G. Sadowski, High-pressure gas solubility in multicomponent solvent systems for hydroformylation. Part I: carbon monoxide solubility, J. Supercriti. Fluid. 81 (2013) 23-32.
[80] C. Brandenbusch, G. Sadowski, Supercritical phase behavior for biotransformation processing, J. Supercriti. Fluid. 55 (2010) 635-642.
[81] M. Lemberg, G. Sadowski, Phase equilibria for the hydroesterification of 10undecenoic acid methyl ester, J. Chem. Eng. Data 61 (2016) 3317-3325.
[82] C.J. Chang, C.-Y. Day, C.-M. Ko, K.-L. Chiu, Densities and P-x-y diagrams for carbon dioxide dissolution in methanol, ethanol, and acetone mixtures, Fluid Phase Equilibria. 131 (1997) 243-258.
[83] J.H. Hong, R. Kobayashi, Vapor-liquid equilibrium studies for the carbon dioxide-methanol system, Fluid Phase Equilibria. 41 (1988) 269-276.
[84] J. Xia, M. Jödecke, Á. Pérez-Salado Kamps, G. Maurer, Solubility of CO 2 in (CH 3 OH + H 2 O), J. Chem. Eng. Data 49 (2004) 1756-1759.
[85] S.N. Joung, C.W. Yoo, H.Y. Shin, S.Y. Kim, K.-P. Yoo, C.S. Lee, W.S. Huh, Measurements and correlation of high-pressure VLE of binary CO2-alcohol systems (methanol, ethanol, 2-methoxyethanol and 2-ethoxyethanol), Fluid Phase Equilibria. 185 (2001) 219-230.
[86] K. Suzuki, H. Sue, M. Itou, R.L. Smith, H. Inomata, K. Arai, S. Saito, Isothermal vapor-liquid equilibrium data for binary systems at high pressures: carbon dioxide-methanol, carbon dioxide-ethanol, carbon dioxide-1-propanol, methaneethanol, methane-1-propanol, ethane-ethanol, and ethane-1-propanol systems, J. Chem. Eng. Data 35 (1990) 63-66.
[87] F. Murrieta-Guevara, A. Trejo Rodriguez, Solubility of carbon dioxide, hydrogen sulfide, and methane in pure and mixed solvents, J. Chem. Eng. Data 29 (1984) 456-460.
[88] R. Rajasingam, L. Lioe, Q. Pham, F.P. Lucien, Solubility of carbon dioxide in dimethylsulfoxide and N-methyl-2-pyrrolidone at elevated pressure, J. Supercriti. Fluid. 31 (2004) 227-234.
[89] M.R. Bohloul, A. Vatani, S.M. Peyghambarzadeh, Experimental and theoretical study of CO2 solubility in N-methyl-2-pyrrolidone (NMP), Fluid Phase Equilibria. 365 (2014) 106-111.
[90] M. Ebrahiminejadhasanabadi, Solubility Studies of Carbon Dioxide in Novel Hybrid Solvents using a New Static Synthetic Apparatus. Dissertation, University of Kwazulu-Natal, 2019.
[91] Ž. Knez, M. Škerget, L. Ilič, C. Lütge, Vapor-liquid equilibrium of binary CO2-organic solvent systems (ethanol, tetrahydrofuran, ortho-xylene, metaxylene, para-xylene), J. Supercriti. Fluid. 43 (2008) 383-389.
[92] M. Jödecke, A. Pérez-Salado Kamps, G. Maurer, An Experimental Investigation of the Solubility of CO 2 in (N, N -Dimethylmethanamide + Water), J. Chem. Eng. Data 57 (2012) 1249-1266.
[93] D. Deng, G. Han, Y. Jiang, N. Ai, Solubilities of carbon dioxide in five biobased solvents, J. Chem. Eng. Data 60 (2015) 104-111.
[94] HS Byun; BM Hasch; MA McHugh. Phase behavior and modeling of the systems CO2acetonitrile and CO2-acrylic acid, 1996.
[95] J. Kiepe, S. Horstmann, K. Fischer, J. Gmehling, Experimental determination and prediction of gas solubility data for $\mathrm{CO} 2+\mathrm{H} 2 \mathrm{O}$ mixtures containing NaCl or KCl at temperatures between 313 and 393 K and pressures up to 10 MPa , Ind. Eng. Chem. Res. 41 (2002) 4393-4398.
[96] C. Peng, J.P. Crawshaw, G.C. Maitland, J.P. Martin Trusler, D. Vega-Maza, The pH of CO2-saturated water at temperatures between 308 K and 423 K at pressures up to 15 MPa , J. Supercriti. Fluid. 82 (2013) 129-137.
[97] W. Yan, S. Huang, E.H. Stenby, Measurement and modeling of CO2 solubility in NaCl brine and CO 2 -saturated NaCl brine density, Int. J. Greenhouse Gas Contr. 5 (2011) 1460-1477.
[98] S.-X. Hou, G.C. Maitland, J.M. Trusler, Phase equilibria of $(\mathrm{CO} 2+\mathrm{H} 2 \mathrm{O}+\mathrm{NaCl})$ and ( $\mathrm{CO} 2+\mathrm{H} 2 \mathrm{O}+\mathrm{KCl}$ ): measurements and modeling, J. Supercriti. Fluid. 78 (2013) 78-88.
[99] S. He, J.W. Morse, The carbonic acid system and calcite solubility in aqueous Na-K-Ca-Mg-Cl-SO4 solutions from 0 to $90^{\circ} \mathrm{C}$, Geochimica et Cosmochimica Acta 57 (1993) 3533-3554.
[100] Á. Pérez-Salado Kamps, E. Meyer, B. Rumpf, G Maurer, Solubility of CO 2 in aqueous solutions of KCl and in aqueous solutions of K 2 CO 3, J. Chem. Eng. Data 52 (2007) 817-832.
[101] D. Tong, J.P.M. Trusler, D. Vega-Maza, Solubility of CO 2 in aqueous solutions of CaCl 2 or MgCl 2 and in a synthetic formation brine at temperatures up to 423 K and pressures up to $40 \mathrm{MPa}, \mathrm{J}$. Chem. Eng. Data 58 (2013) 2116-2124.
[102] J. Kiepe, S. Horstmann, K. Fischer, J. Gmehling, Experimental determination and prediction of gas solubility data for $\mathrm{CO} 2+\mathrm{H} 2 \mathrm{O}$ mixtures containing NaNO 3 or KNO 3, Ind. Eng. Chem. Res. 42 (2003) 3851-3856.
[103] X. Han, Z. Yu, J. Qu, T. Qi, W. Guo, G. Zhang, Measurement and correlation of solubility data for CO 2 in NaHCO 3 aqueous solution, J. Chem. Eng. Data 56 (2011) 1213-1219.
[104] B. Rumpf, G. Maurer, An experimental and theoretical investigation on the solubility of carbon dioxide in aqueous solutions of strong electrolytes, Berichte der Bunsengesellschaft für physikalische Chemie 97 (1993) 85-97.
[105] Á. Pérez-Salado Kamps, M. Jödecke, J. Xia, M. Vogt, G Maurer, Influence of salts on the solubility of carbon dioxide in (Water + Methanol). Part 1: Sodium chloride, Ind. Eng. Chem. Res. 45 (2006) 1505-1515.