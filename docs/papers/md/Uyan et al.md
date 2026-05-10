\title{
Predicting $\mathrm{CO}_{2}$ solubility in aqueous $N$-methyldiethanolamine solutions with ePC-SAFT
}

\author{
Mustafa Uyan ${ }^{\mathrm{a}}$, Georg Sieder ${ }^{\mathrm{b}}$, Thomas Ingram ${ }^{\mathrm{b}}$, Christoph Held ${ }^{\mathrm{a}, *}$ \\ ${ }^{\mathrm{a}}$ Laboratory of Thermodynamics, Department of Biochemical and Chemical Engineering, Technische Universität Dortmund, Emil-Figge-Str. 70, 44227 Dortmund, Germany \\ ${ }^{\mathrm{b}}$ BASF SE, GCP/TD - L540, 67056 Ludwigshafen, Germany
}

\section*{ARTICLE INFO}

\section*{Article history:}

Received 18 December 2014
Received in revised form 17 February 2015
Accepted 18 February 2015
Available online 28 February 2015

\section*{Keywords:}

Electrolytes
Modeling
Thermodynamics
Activity coefficients
GLE
VLE
Reaction equilibria
MDEA

\begin{abstract}
In this work, electrolyte PC-SAFT equation of state developed in 2005 with the parameters from Held et al. [Chem. Eng. Res. Des. 92 (2014) 2884-2897] has been applied to predict the solubility of $\mathrm{CO}_{2}$ in aqueous $N$-methyldiethanolamine (MDEA) solutions. The considered temperature range was $313-413 \mathrm{~K}$, MDEA weight fractions up to 0.32 (related to the binary water/MDEA system) and loadings of up to 1.32 (mole $\mathrm{CO}_{2} /$ mole MDEA).

In order to predict $\mathrm{CO}_{2}$ solubilities, the reaction equilibria and phase equilibria were solved simultaneously by explicitly accounting for the electrolyte species being present in the system: $\mathrm{H}^{+}, \mathrm{OH}^{-}$, $\mathrm{HCO}_{3}{ }^{-}, \mathrm{CO}_{3}{ }^{2-}$ and MDEAH ${ }^{+}$. The pure-component parameters for the molecular components ( $\mathrm{H}_{2} \mathrm{O}, \mathrm{CO}_{2}$, MDEA) and for all ions except MDEAH ${ }^{+}$were already available in the literature. MDEAH ${ }^{+}$pure-component parameters were inherited from MDEA, and the charge was explicitly accounted for in ePC-SAFT. Binary parameters were applied only for the pairs $\mathrm{H}_{2} \mathrm{O} / \mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{O} /$ ions, and $\mathrm{H}_{2} \mathrm{O} /$ MDEA . The deviations between experimental and ePC-SAFT modeled $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions was $19.82 \%$ for a temperature range of $313-413 \mathrm{~K}$, a MDEA weight fractions of 0.19 , and $\mathrm{CO}_{2}$ loadings of up to 1.3 (mole $\mathrm{CO}_{2} /$ mole MDEA). As binary parameters have not been adjusted to experimental $\mathrm{CO}_{2}$ solubility data in aqueous MDEA solutions, these results can be considered as predictive.
\end{abstract}
© 2015 Elsevier B.V. All rights reserved.

\section*{1. Introduction}

In times of global warming, the development of process engineering applications for the reduction of anthropogenic carbon dioxide emission is becoming increasingly important [1]. One possibility to remove $\mathrm{CO}_{2}$ from process, synthetic or natural gases is the absorption with aqueous alkanolamine solutions. This concept is known since 1930 [2], and from that time on research has started on developing different alkanolamine systems for the use of $\mathrm{CO}_{2}$ absorption [3]. The big advantage of aqueous amine systems is that the solubility of $\mathrm{CO}_{2}$ is based on physical absorption and chemical absorption caused by reactions of $\mathrm{CO}_{2}$ in the liquid phase. In this way, a high loading of the alkanolamine with the absorbate is achieved. Suitable alkanolamines are especially monoethanolamine (MEA), diethanolamine (DEA) and methyldiethanolamine (MDEA). The latter has advantageous properties with respect to the $\mathrm{CO}_{2}$ load capacity and to chemical and thermal stability. Thus, the industrial relevance of aqueous MDEA solutions

\footnotetext{
* Corresponding author. Tel.: +49 2317552086.

E-mail address: christoph.held@bci.tu-dortmund.de (C. Held).
}
for the purification of gases has continuously increased in the recent years [4].

In the ternary water/ $\mathrm{CO}_{2}$ /MDEA system, significant amounts of different ion species are formed caused by reactions in the liquid phase, especially the protonated MDEA (MDEAH ${ }^{+}$) and hydrogen carbonate ( $\mathrm{HCO}_{3}{ }^{-}$). Modeling phase equilibria in this ternary water/ $\mathrm{CO}_{2}$ /MDEA system requires explicitly accounting for the formation of the ions. This is important as electrolytes have a huge impact on phase equilibria and thermodynamic properties of aqueous systems [5-7]. Modern electrolyte models consider shortrange (SR) interactions and long-range (LR) interactions among the charged species in order to describe the residual Helmholtz energy or the excess Gibbs energy of a system. Debye and Hückel proposed already in 1923 their approach for the characterization of dilute electrolyte solutions [8]. The description of the LR forces requires the dielectric constant of an electrolyte solution, which has shown to influence the results obtained with an electrolyte model [9,10].

The $\mathrm{CO}_{2}$ solubility in aqueous amine solutions has intensively been measured, correlated, and modeled. Among the first approaches to describe experimental data are empirical models [11,12]. However, a huge set of experimental data is required and the application is limited to the range of conditions the parameters

\section*{Nomenclature}

Roman symbols
a Helmholtz free energy per number of molecules (-)
a Activity (-)
c Equation constants (-)
$d \quad$ Temperature-dependent segment diameter ( $\AA$ )
$k_{\mathrm{B}} \quad$ Boltzmann constant, $1.38065 \times 10^{-23} \mathrm{~J} / \mathrm{K}(\mathrm{J} / \mathrm{K})$
$k_{i j} \quad$ Binary interaction parameter (-)
$k_{i j}{ }^{\mathrm{hb}} \quad$ Binary interaction parameter (-)
$K_{a} \quad$ Activity-based equilibrium constant (-)
$m^{\text {seg }} \quad$ Number of segments (-)
$n_{i} \quad$ Mole number of component $i(-)$
$N^{\text {assoc }}$ Number of association sites (-)
NP Number of data points (-)
$p \quad$ Pressure (Pa, bar)
$R \quad$ Ideal gas constant ( $\mathrm{J} / \mathrm{mol} / \mathrm{K}$ )
$T \quad$ Temperature (K)
$u / k_{\mathrm{B}} \quad$ Dispersion-energy parameter (K)
$x \quad$ Mole fraction (-)
$Z \quad$ Real gas factor (-)

Greek symbols
$\alpha \quad \mathrm{CO}_{2}$ loading (mole $\mathrm{CO}_{2} /$ mole MDEA)
$\gamma_{i}$ Symmetrical activity coefficient of component $i$ (related to pure component) (-)
$\gamma_{i}^{*} \quad$ Asymmetrical activity coefficient of component $i$ (related to infinite dilution) (-)
$\varphi_{i} \quad$ Fugacity coefficient of component $i(-)$
$\varepsilon_{r} \quad$ Relative dielectric constant (-)
$\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}} / k_{\mathrm{B}}$ Association-energy parameter (K)
$\phi \quad$ Osmotic coefficient (-)
$\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}} \quad$ Association-volume parameter (-)
$\lambda$ Reaction coordination number (mol)
$\rho \quad$ Number density $\left(1 / \mathrm{m}^{3}\right)$
$v$ Stoichiometric factor (-)
$\sigma_{i}$ Temperature-independent segment diameter of molecule $i$ (Å)

\section*{Subscripts}
$i, j \quad$ Component indices
seg Segment
0 Pure substance

Superscripts
assoc Association
disp Dispersion
exp Experimental
hc Hard chain
ion Ionic
L Liquid phase
mod Modeled
res Residual
V Vapor phase
+,- Positive or negative charge
$\infty \quad$ Infinite dilution
* Related to infinite dilution
$0 \quad$ Pure substance

Abbreviations
ARD Absolute average relative deviation
CPA Cubic plus association
DEA Diethanolamine
EOS Equation of state

\begin{tabular}{ll}
$\mathrm{g}^{\mathrm{E}}$ & Excess Gibbs energy \\
LR & Long range \\
MDEA & Methyldiethanolamine \\
MEA & Monoethanolamine \\
PR & Peng Robinson \\
SAFT & Statistical associating fluid theory \\
SR & Short range \\
VLE & Vapor-liquid equilibria
\end{tabular}
have been fitted to. In the literature, electrolyte and nonelectrolyte models have been developed, which consider SR or $\mathrm{SR}+\mathrm{LR}$ forces in order to describe aqueous amine $+\mathrm{CO}_{2}$ solutions. These models describe the excess Gibbs energy ( $\rightarrow \mathrm{g}^{\mathrm{E}}$-models) or the Helmholtz energy ( → equations of state (EOS)) of a system. Austgen et al. [13] and Zhang and Chen [14] modeled aqueous amine solutions and aqueous solutions containing amine mixtures using eNRTL [15]. Faramarazi et al. [16] applied modified UNIQUAC to describe the $\mathrm{CO}_{2}$ solubility in systems with MEA and MDEA, respectively. Kuranov et al. [17] and Kamps et al. [18] correlated Pitzer parameters [19] to experimental $\mathrm{H}_{2} \mathrm{~S}$ and $\mathrm{CO}_{2}$ solubility data in aqueous MDEA solutions in a broad temperature and pressure range. The Pitzer model was further used by Arcis et al. [20] in order to model the VLE and to estimate the solution enthalpy of $\mathrm{CO}_{2}$ in aqueous MDEA solutions.

The drawback of $\mathrm{g}^{\mathrm{E}}$ models is the huge number of adjustable binary parameters, that often depend on temperature and sometimes even on concentrations. The application of EOS usually requires a much smaller number of binary fitting parameters. Zoghi et al. [21] and Avlund et al. [22] applied the CPA EOS in order to model the VLE of aqueous MDEA, MEA, and DEA solutions by explicitly accounting for the complex association behavior. The association behavior can also be described with SAFT-based EOS. Button and Gubbins [23] used SAFT to model the VLE of aqueous MEA and DEA solutions under the presence of $\mathrm{CO}_{2}$. A big average deviation of $43 \%$ was observed, which probably was due to neglecting chemical reactions. This shortcoming was corrected for in the work of Nasfrifar and Tafazzol [24]; they used PC-SAFT EOS combined with chemical reaction equilibria in order to model gas solubilities $\left(\mathrm{H}_{2} \mathrm{~S}, \mathrm{CO}_{2}\right)$ in aqueous ethanolamine solutions. In a more recent work, Pahlavanzadeh and Fakouri Baygi [25] applied PC-SAFT combined with chemical reaction equilibria in order to predict $\mathrm{CO}_{2}$ solubilities in aqueous MDEA solutions. However, Pahlavanzadeh and Fakouri Baygi neglected the presents of any ions in the systems.

Next to these non-electrolyte EOS models, also electrolyte models have been applied in the literature to model gas solubilities in aqueous amine solutions. Such models (e.g., electrolyte PengRobinson EOS (PR EOS) [26] and various electrolyte SAFT-based approaches [27-31]) describe the Helmholtz energy of an electrolyte solution by considering SR forces as well as the LR forces (either via the Debye-Hückel theory or via the mean spherical approximation). Most researchers consider electrolytes as fully dissociated into cations and anions requiring ion-specific parameters that account also for ion solvation via SR forces. Based on a non-electrolyte PR-EOS (proposed by Huttenhuis et al. [32]), Zoghi et al. [21] included a theory accounting for LR forces and a Born term to describe the solubility of $\mathrm{CO}_{2}$ in aqueous solutions of MDEA in wide ranges of concentration, pressure, temperature, and gas loading. However, they used binary interaction parameters that were fitted to the ternary systems. Using this approach, Zoghi et al. could quantitatively describe the solubility of $\mathrm{CO}_{2}$ in aqueous MDEA solutions.

Although many approaches have been developed and applied so far to model the solubility of $\mathrm{CO}_{2}$ in aqueous amine solutions,
this research field still reveals potential for improvements. This is mainly due to the fact that most of the applied models were applied in a correlative way. However, it is highly desirable to apply one single model to (1) a broad temperature and concentration range, (2) systems where no experimental data are available (model predictions), and (3) conditions at which parameters have not been adjusted (model extrapolations). In this work, the VLE of the ternary system water/ $\mathrm{CO}_{2}$ /MDEA shall be predicted by an electrolyte EOS. One model that has been shown to fulfill these criteria is ePC-SAFT [33]. ePC-SAFT is a SAFT-based model [34,35], and it combines PC-SAFT for the description of the SR forces [36] with the Debye and Hückel theory that accounts for the LR forces among ions [27]. In recent works, it was shown that phase equilibria in complex electrolyte solutions could be satisfactorily modeled and predicted with ePC-SAFT [6,7,37]. One question that has to be addressed in aqueous amine $+\mathrm{CO}_{2}$ solutions is the presence of weak electrolytes. Weak electrolyte solutions were successfully described with an ion-pairing approach within ePCSAFT [38], however at cost of two additional parameters per salt. Alternatively, Held et al. [39] have shown that this ion-pairing approach could be replaced by considering SR dispersion forces also between anions and cations in an electrolyte solution. Thus, this strategy will be applied also in this work. Based on this $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions can be predicted using ePC-SAFT and accounting for the influence of electrolytes on the phase and reaction equilibria. In this work, the $\mathrm{CO}_{2}$ solubility is predicted in a system that contains three volatile components and five ionic species in the liquid phase.

\section*{2. Phase equilibria and ePC-SAFT EOS}

The isofugacity criteria were used in order to solve the vapor-liquid equilibrium in the system water/ $\mathrm{CO}_{2}$ /MDEA:
$x_{i} \varphi_{i}^{\mathrm{L}}\left(T, p, \vec{x}^{\mathrm{L}}\right)=y_{i} \varphi_{i}^{\mathrm{V}}(T, p, \vec{y}) i=$ water, $\mathrm{CO}_{2}$, MDEA
where $x_{i}$ and $y_{i}$ are the mole fractions of component $i$ in the liquid phase L and in the vapor phase V , and $\varphi_{i}$ are the fugacity coefficients of component $i$ at temperature $T$ and pressure $p$, respectively. Fugacity coefficients are calculated by

$$
\begin{equation*}
\ln \varphi_{i}=(Z-1)-\ln Z+a^{\text {res }}+\frac{\partial a^{\text {res }}}{\partial x_{i}}-\Sigma_{j} x_{j}\left(\frac{\partial a^{\text {res }}}{\partial x_{j}}\right) \tag{2}
\end{equation*}
$$

where $Z$ is the compressibility factor, obtained by

$$
\begin{equation*}
Z(\rho)=1+\rho\left(\frac{\partial a^{\mathrm{res}}}{\partial \rho}\right)_{T, x} \tag{3}
\end{equation*}
$$

where $\rho$ is the number density of the system. In Eqs. (2) and (3), ares is the residual Helmholtz energy of an electrolyte system that is calculated within ePC-SAFT by:

$$
\begin{equation*}
a^{\text {res }}=a^{\text {hc }}+a^{\text {disp }}+a^{\text {assoc }}+a^{\text {ion }} \tag{4}
\end{equation*}
$$


In this work, four Helmholtz-energy contributions to $a^{\text {res }}$ are considered. $a^{\text {hc }}$ describes the hard-chain system that represents the reference system in ePC-SAFT. Perturbations to this reference system are explicitly accounted for by dispersion forces ( $a^{\text {disp }}$ ) and associative hydrogen-bonding forces ( $\mathrm{a}^{\text {assoc }}$ ). In order to account for interactions between charged species, a Debye-Hückel term is used ( $a^{\text {ion }}$ ). The dependence of fugacity coefficients of water, $\mathrm{CO}_{2}$, and MDEA on electrolyte species is explicitly accounted for by ePC-SAFT.

Application of the Helmholtz-energy contribution $a^{\text {ion }}$ requires experimental data or expressions for the dielectric constant $\varepsilon$ of the considered electrolyte solution. In this work, $\varepsilon$ is assumed to be independent of the presence of ions and $\mathrm{CO}_{2}$. This assumption was based on the estimation procedure of ion-parameters in our
previous work [39]; in that work, ePC-SAFT ion parameters were adjusted to mixture-density and osmotic coefficients of aqueous electrolyte solutions by neglecting the influence of electrolytes on $\varepsilon$ of water/salt solutions. That is, $\varepsilon$ of the electrolyte solution was assumed to be of the same value as pure water (depending on temperature). In this work, the dielectric constant was assumed to be a function of the ion-free and $\mathrm{CO}_{2}$-free MDEA/water solution according to our previous work [5] using the expression

$$
\begin{equation*}
\varepsilon=\varepsilon_{0, \mathrm{w}}(T) w_{\mathrm{w}}+\varepsilon_{0, \mathrm{MDEA}}(T) w_{\text {MDEA }} \tag{5}
\end{equation*}
$$


The temperature dependence of $\varepsilon$ in pure water (" $0, \mathrm{w}$ ") was described by the correlation of Floriano and Nascimento [40]. The correlation given by Hsieh et al. [41] was used to calculate the dielectric constant of pure MDEA ("0, MDEA").

In ePC-SAFT, ions are characterized by two pure-component parameters, the distance of closest approach $\sigma_{\text {ion }}$ (which is assumed to be the solvated-ion diameter), and the dispersionenergy parameter $u_{\text {ion }} / k_{\mathrm{B}}$, with $k_{\mathrm{B}}$ being the Boltzmann constant. Following the proposal of Held et al. [39], dispersion between like ions (cation-cation, anion-anion) are not accounted for.

In order to describe mixtures, the following Berthelot-Lorentz combining rules were applied for the segment diameter $\sigma_{i j}$ and the dispersion-energy parameter $u_{i j}$ between two components $i$ and $j$ (e.g., water and ion):

$$
\begin{equation*}
\sigma_{i j}=\frac{1}{2}\left(\sigma_{i}+\sigma_{j}\right) \tag{6}
\end{equation*}
$$


$$
\begin{equation*}
u_{i j}=\sqrt{u_{i} u_{j}}\left(1-k_{i j}\right) \tag{7}
\end{equation*}
$$


In Eq. (7) $k_{i j}$ values were applied for correcting the cross-dispersion energy parameter between two components $i$ and $j$. The $k_{i j}$ might also be temperature-dependent.

Considering compounds that form hydrogen bonds require two additional parameters in ePC-SAFT, the association-energy parameter $\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}} / k_{\mathrm{B}}$ and the association-volume parameter $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ between two associating molecules $i$ and $j$ with the association sites A and B . In this work, the Wolbach-Sandler combining rules were applied [42] for describing mixtures of associating molecules $i$ and $j$ :

$$
\begin{equation*}
\varepsilon^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{j}}=\frac{1}{2}\left(\varepsilon^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{i}}+\varepsilon^{\mathrm{A}_{\mathrm{j}} \mathrm{B}_{j}}\right) \tag{8}
\end{equation*}
$$


$$
\begin{equation*}
\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}=\sqrt{\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}} \kappa^{\mathrm{A}_{j} \mathrm{~B}_{j}}}\left(\frac{\sqrt{\sigma_{i} \sigma_{j}}}{1 / 2\left(\sigma_{i}+\sigma_{j}\right)}\right)^{3}\left(1-k_{i j}^{\mathrm{hb}}\right) \tag{9}
\end{equation*}
$$


In Eq. (9) the binary adjustable parameter $k_{i j}{ }^{\text {hb }}$ is introduced. In previous works, it has been shown that the application of such binary parameters related to association strongly improves the description of phase equilibrium data [5,43]. Thus, $k_{i j}{ }^{\text {hb }}$ is used also in this work for water/MDEA mixtures.

Next to the pure-component and binary interaction parameters, expressions for the temperature-dependent diameter $d_{i}$ of a pure component $i$ are required for PC-SAFT calculations. In case of all ions considered in this work, the temperature-independent expression

$$
\begin{equation*}
d_{\text {ion }}=\sigma_{\text {ion }}[1-0.12] \tag{10}
\end{equation*}
$$

was used as in all our previous works on electrolytes [5-7,27,37-39,44]. For all other pure components considered in this work, the following expression was applied [45]:

$$
\begin{equation*}
d_{\mathrm{i}}=\sigma_{\mathrm{i}}\left[1-0.12 \exp \left(-\frac{3 u_{i}}{k_{\mathrm{B}} T}\right)\right] \tag{11}
\end{equation*}
$$


The expression in Eq. (11) was inherited from original PC-SAFT [36]. Next to the standard expression in Eq. (11), Eq. (10) was required as the pure-dispersion interactions among two equal ions were set to zero in ePC-SAFT resulting in a zero $u_{i} / k_{\mathrm{B}}$ value in Eq. (11) finally yielding Eq. (10) for all ions [39].

\section*{3. Chemical reaction equilibria}

The absorption process of $\mathrm{CO}_{2}$ in aqueous amine solutions is based on physical and chemical processes. In the system water/CO2/ MDEA the following four reactions take place in the liquid phase

$$
\begin{equation*}
\mathrm{H}_{2} \mathrm{O} \leftrightarrow \mathrm{H}^{+}+\mathrm{OH}^{-} \tag{12}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O} \leftrightarrow \mathrm{HCO}_{3}^{-}+\mathrm{H}^{+} \tag{13}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{HCO}_{3}^{-} \leftrightarrow \mathrm{CO}_{3}^{2-}+\mathrm{H}^{+} \tag{14}
\end{equation*}
$$


MDEAH ${ }^{+} \leftrightarrow \mathrm{MDEA}+\mathrm{H}^{+}$

The law of mass action relates the thermodynamic equilibrium constant $K_{a}$ to the species activity $a_{i}$ :

$$
\begin{equation*}
K_{a}(T)=\prod_{i}\left(a_{i}\right)^{v_{i}}=\prod_{i}\left(x_{i} \gamma_{i}\right)^{v_{i}} \tag{16}
\end{equation*}
$$

where $v_{i}$ and $\gamma_{i}$ are the stochiometric coefficient and the activity coefficient of the species $i$, respectively. The application of Eq. (16) to Eqs. (12) and (15) yields:

$$
\begin{equation*}
K_{a, 1}=\frac{\chi_{\mathrm{H}^{+}} \times \chi_{\mathrm{OH}^{-}}}{\chi_{\mathrm{H}_{2} \mathrm{O}}} \times \frac{\gamma_{\mathrm{H}^{+}}^{*} \times \gamma_{\mathrm{OH}^{-}}^{*}}{\gamma_{\mathrm{H}_{2} \mathrm{O}}^{0}} \tag{17}
\end{equation*}
$$


$$
\begin{equation*}
K_{a, 2}=\frac{x_{\mathrm{H}^{+}} \times x_{\mathrm{HCO}_{3}}}{x_{\mathrm{CO}_{2}} \times x_{\mathrm{H}_{2} \mathrm{O}}} \times \frac{\gamma_{\mathrm{H}^{+}}^{*} \times \gamma_{\mathrm{HCO}_{3}}^{*}}{\gamma_{\mathrm{CO}_{2}}^{0} \times \gamma_{\mathrm{H}_{2} \mathrm{O}}^{0}} \tag{18}
\end{equation*}
$$


$$
\begin{equation*}
K_{a, 3}=\frac{x_{\mathrm{H}^{+}} \times x_{\mathrm{CO}_{3}^{2-}}}{x_{\mathrm{HCO}_{3}^{-}}} \times \frac{\gamma_{\mathrm{H}^{+}}^{*} \times \gamma_{\mathrm{CO}_{3}^{2-}}^{*}}{\gamma_{\mathrm{HCO}_{3}^{-}}^{*}} \tag{19}
\end{equation*}
$$


$$
\begin{equation*}
K_{a, 4}=\frac{x_{\mathrm{H}^{+}} \times x_{\mathrm{MDEA}}}{x_{\mathrm{MDEAH}^{+}}} \times \frac{\gamma_{\mathrm{H}^{+}}^{*} \times \gamma_{\mathrm{MDEA}}^{*}}{\gamma_{\mathrm{MDEAH}^{+}}^{*}} \tag{20}
\end{equation*}
$$


Note, that the activity coefficients of $\mathrm{H}^{+}$were calculated with the set of pure-component/binary ePC-SAFT parameters for $\mathrm{H}_{3} \mathrm{O}^{+}$ (Tables 4 and 5).

The equilibrium constants $K_{a}$ of the reactions (Eqs. (17)-(20)) were expressed as:

$$
\begin{equation*}
\ln \left(K_{a}\right)=c_{1}+\frac{c_{2}}{T[K]}+c_{3} \times \ln (T[K])+c_{4} \times(T[K]) \tag{21}
\end{equation*}
$$


The constants $c_{1}-c_{4}$ for Eq. (21) were fitted to experimental data ([18,46-48]) and are listed in Table 1.

Application of Eqs. (17)-(20) requires activity coefficients that are accessible with ePC-SAFT based on the fugacity coefficients (Eq. (2)) and the definition of activity coefficients. For water, the generic activity coefficients $\gamma^{0}$ were used that are related to the pure-component state:

$$
\begin{equation*}
\frac{\gamma_{i}=\varphi_{i}(T, p, \vec{x})}{\varphi_{0 i}\left(T, p, x_{i}=1\right)} \tag{22}
\end{equation*}
$$


\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1
Constants $c_{1}-c_{4}$ used for the calculation of equilibrium constants $K_{a}$ in Eqs. (17)-(20). The $K_{a}$ values are given on a mole-basis and were taken from literature [18,46-48].}
\begin{tabular}{llrrl}
\hline & $c_{1}$ & \multicolumn{1}{l}{$c_{2}$} & \multicolumn{1}{l}{$c_{3}$} & \multicolumn{1}{l}{$c_{4}$} \\
\hline$K_{a, 1}$ & 132.899 & $-13,445.9$ & -22.477 & - \\
$K_{a, 2}$ & 212.739 & $-11,333.8$ & -33.844 & -0.0018149 \\
$K_{a, 3}$ & 287.444 & $-13,648.7$ & -48.880 & 0.030232 \\
$K_{a, 4}$ & -83.491 & -819.7 & 10.976 & - \\
\hline
\end{tabular}
\end{table}
where the subscript $0 i$ denotes the reference state 'pure component'. For all other components in the system, rational activity coefficients $\gamma^{*}$ were applied that are related to the infinite-diluted state of the component:

$$
\begin{equation*}
\frac{\gamma_{i}^{*}=\varphi_{i}(T, p, \vec{x})}{\varphi_{i}^{\infty}\left(T, p, x_{i}=0\right)} \tag{23}
\end{equation*}
$$


The $K$-value method was applied to solve the reaction equilibria [49]. With this method the mole fractions of the liquid phase are expressed as reaction coordination numbers $\lambda_{i}$. With the relation $x_{i}=n_{i} / n_{\text {total }}$ it is possible to express the laws of mass action of each individual reaction (Eqs. (17)-(20)) depending on the reaction coordination numbers ( $\lambda_{1}, \lambda_{2}, \lambda_{3}, \lambda_{4}$ ) and the activity coefficients of all eight species

$$
\begin{equation*}
n_{i}=n_{i, 0}+\sum_{r=1}^{4} v_{i} \times \lambda_{r} \tag{24}
\end{equation*}
$$


For $r$ reactions (Eqs. (17)-(20)) and a starting mole number $n_{i, \mathrm{O}}$. With this method, the reaction equilibria were solved following these steps
1. The reaction equilibria for the ideal case (all activity coefficients set equal to unity) are solved.
2. The liquid phase composition obtained in 1 is used as input for ePC-SAFT in order to calculate component activity coefficients according to Eqs. (22) and (23).
3. The reaction equilibria accounting for the component activity coefficients obtained in 2 are solved.
4. Steps 2 and 3 are repeated until the liquid-phase composition does not change with absolute values of $10^{-6}$.

In order to solve the equation system, starting values for $\lambda_{1}-\lambda_{4}$ must be selected. These are listed in Table 2 and are valid independent of temperature and MDEA concentration.

Finally, knowledge of the species distribution in the liquid phase composition allows the calculation of the VLE of the system water/ $\mathrm{CO}_{2}$ /MDEA. That is, the system pressure is calculated at given temperature, MDEA concentration, and $\mathrm{CO}_{2}$ loading $\alpha$ using the isofugacity criteria (Eq. (1)).

\section*{4. Results and discussion}

The main focus of this work was to predict $\mathrm{CO}_{2}$ solubilities in aqueous MDEA solutions with ePC-SAFT by considering the reaction equilibria. In a first step, pure-component ePC-SAFT parameters from the literature were chosen and binary interaction

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2
Starting values for the reaction coordination numbers $\lambda$.}
\begin{tabular}{ll}
\hline Reaction coordination numbers & Starting value \\
\hline$\lambda_{1}$ & $2.0 \times 10^{-6}$ \\
$\lambda_{2}$ & 0.1 \\
$\lambda_{3}$ & $1.0 \times 10^{-3}$ \\
$\lambda_{4}$ & $-9.9 \times 10^{-3}$ \\
\hline
\end{tabular}
\end{table}
parameters were determined. Based on this, the VLE of ternary mixtures water/ $\mathrm{CO}_{2} /$ MDEA at different conditions (e.g., temperature, $\mathrm{CO}_{2}$ loading) was modeled.

All ePC-SAFT prediction and modeling results were compared to experimental data in terms of the absolute relative deviation ARD:

$$
\begin{equation*}
\mathrm{ARD}=100 \times \frac{1}{\mathrm{NP}} \times \sum_{k=1}^{\mathrm{NP}}\left|1-\frac{p_{k}^{\bmod }}{p_{k}^{\exp }}\right| \tag{25}
\end{equation*}
$$

where $p^{\text {calc }}$ and $p^{\text {exp }}$ denote the ePC-SAFT modeled pressure and the experimental pressure for a certain number of available experimental data points NP.

\subsection*{4.1. Pure-component ePC-SAFT parameters}

Modeling mixtures with ePC-SAFT requires pure-component parameters for all components in a first step. The pure-component parameters that were used for water, MDEA, and CO2 are listed in Table 3. All parameters were taken from literature.

For water, the 2 B association model was applied with a set of pure-water parameters that is especially suitable to biological solutions [50]. This parameter set was fitted to densities and vapor pressures between 273 K and 393 K , and thus is appropriate to the temperature range considered in this work (303-413 K). Dipolar interactions are not explicitly accounted for in this approach. MDEA pure-component parameters were inherited from Ref. [51]. In Ref. [51] different association models for the characterization of MDEA were applied. It was shown that the 4C association model has advantages for modeling VLE of the MDEA/water system; this is in accordance to works of Avlund et al. [22] who have shown that the tertiary amine group in MDEA only marginally contributes to the association forces compared to the hydroxyl groups. Thus, the 4C approach was also applied in this work. The pure-component parameters given by Gross and Sadowski [36] were used to characterize $\mathrm{CO}_{2}$. These parameters do not explicitly account for quadrupolar forces. It can be observed from Table 1 that the pure-component parameters for water, MDEA, and $\mathrm{CO}_{2}$ allow reasonably modeling the properties (liquid density, vapor pressure) of the pure components.

The pure-component ePC-SAFT parameters of the ions were inherited from a recent work by Held et al. [39]. Held et al. fitted the segment diameter $\sigma_{\text {ion }}$, the dispersion-energy parameter $u_{\text {ion }} / k_{\mathrm{B}}$, and the $k_{i j}$ parameters between anion and cation as well as between water and ions to experimental solution densities and osmotic coefficients of aqueous electrolyte solutions at atmospheric pressure and 298.15 K . Compared to original ePC-SAFT [27,33], dispersion forces among anion and cation were considered. The pure-component parameters of the ions considered in this work are listed in Table 4. In case of MDEAH ${ }^{+}$,

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3
Pure-component parameters, deviations to experimental data and reference for the parameters.}
\begin{tabular}{|l|l|l|l|l|}
\hline Parameter & Symbol & Water [50] & MDEA [51] & $\mathrm{CO}_{2}$ [36] \\
\hline Segment number (-) & $m_{i}{ }^{\text {seg }}$ & 1.2046 & 3.675 & 2.0729 \\
\hline Segment diameter (A) & $\sigma_{i}$ & * & 3.563 & 2.7852 \\
\hline Dispersion-energy parameter (K) & $u_{i} / k_{\mathrm{B}}$ & 353.94 & 228.711 & 169.21 \\
\hline Number of association sites (-) & $N^{\text {assoc }}$ & 2 & 4 & - \\
\hline Association-energy parameter (K) & $\varepsilon^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{\mathrm{i}}} / k_{\mathrm{B}}$ & 2425.67 & 2046.624 & - \\
\hline Association-volume parameter (-) & $\kappa^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{\mathrm{i}}}$ & 0.04509 & 0.123858 & - \\
\hline ARD liquid density (\%) & & 0.02 [52] & 0.51 [51] & 2.73 [36] \\
\hline ARD vapor pressure (\%) & & 0.60 [52] & 0.41 [51] & 2.78 \\
\hline & & & & [36] \\
\hline
\end{tabular}
\end{table}

\footnotetext{
${ }^{*} \sigma=2.7927+10.11 \exp (-0.01775 T[\mathrm{~K}])-1.417 \exp (-0.01146 T[\mathrm{~K}])$.
}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4
Pure-component parameters of the ions, taken from Ref. [39].}
\begin{tabular}{|l|l|l|}
\hline Ion & $\sigma_{\text {ion }}$ (A) & $u_{\text {ion }} / k_{\mathrm{B}}(\mathrm{K})$ \\
\hline $\mathrm{H}^{+}$ & 3.4654 & 500.00 \\
\hline $\mathrm{OH}^{-}$ & 2.0177 & 650.00 \\
\hline $\mathrm{HCO}_{3}{ }^{-}$ & 2.9296 & 70.00 \\
\hline $\mathrm{CO}_{3}{ }^{2-}$ & 2.4422 & 249.26 \\
\hline MDEAH ${ }^{+}$[this work] ${ }^{\text {a }}$ & 3.5630 & 228.71 \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}} \mathrm{MDEAH}^{+}$was considered as cross-associating ion with $\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}} / \mathrm{k}_{\mathrm{B}}=0 \mathrm{~K}$ using the $N^{\text {assoc }}$ and association-volume parameter inherited from MDEA ( $N^{\text {assoc }}=4$, $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}}=0.123858$ ).
ePC-SAFT parameters were not available in the literature. Unfortunately, experimental data of MDEA-salts (e.g., osmotic coefficients of aqueous MDEAH ${ }^{+} \mathrm{Cl}^{-}$solutions) are not available in the literature. Thus, the pure-component parameters of MDEAH ${ }^{+}$were inherited from the parameters of MDEA except self-association and with the difference that the positive charge of MDEAH ${ }^{+}$was additionally accounted for. A strategy was presented recently also by Zoghi et al. [21].

\subsection*{4.2. Binary systems}

Modeling mixtures with ePC-SAFT requires binary parameters that have to be determined based on the pure-component parameters for water, MDEA, and $\mathrm{CO}_{2}$ listed in Table 3. The binary VLEs water/ $\mathrm{CO}_{2}$, water/MDEA, and the systems containing water/ ions have to be modeled as accurately as possible prior to predict the $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions. In order to model all binary systems the chemical reactions were neglected, and thus assumed to not influence the binary VLEs water/CO2 and water/MDEA.

\subsection*{4.2.1. Ions/water}

Modeling electrolyte solutions requires $k_{i j}$ parameters between anion and cation as well as between water and ions. The $k_{i j}$ parameters used in this work originate from Ref. [39] and are given in Table 5. They were fitted to experimental solution densities and osmotic coefficients of aqueous electrolyte solutions at atmospheric pressure and 298.15 K . All $k_{i j}$ values were considered to be temperature independent. The $k_{i j}$ between $\mathrm{MDEAH}^{+}$and water was set to zero as experimental data of pseudo-binary mixtures containing MDEAH ${ }^{+}$(e.g., osmotic coefficients of aqueous $\mathrm{MDEAH} \mathrm{Cl}^{-}$solutions) were not available in the literature.

\subsection*{4.2.2. $\mathrm{CO}_{2}$ /water}

In order to model the VLE of $\mathrm{CO}_{2} /$ water, induced association between $\mathrm{CO}_{2}$ and water was not considered. That is, association forces were only considered among water molecules in the binary $\mathrm{CO}_{2}$ /water system. The binary interaction parameter $k_{i j}$ between $\mathrm{CO}_{2}$ and water was fitted to binary isothermal VLE data [53] up to

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5
Binary parameters between water and ions, taken from Ref. [39], and of the pairs water/ $\mathrm{CO}_{2}$ and water/MDEA, determined in this work.}
\begin{tabular}{|l|l|l|l|}
\hline Binary pair & $k_{i j}$ & ARD pressure (VLE) (\%) & Data references for ARD \\
\hline $\mathrm{H}^{+}$/water & 0.25 & - & - \\
\hline $\mathrm{OH}^{-}$/water & -0.25 & - & - \\
\hline $\mathrm{HCO}_{3}{ }^{-}$/ water & - & - & - \\
\hline $\mathrm{CO}_{3}{ }^{2-}$ /water & -0.25 & - & - \\
\hline $\mathrm{MDEAH}^{+}$/water & Eq. (27) & - & - \\
\hline $\mathrm{CO}_{2}$ /water & Eq. (26) & 5.26 (304-422 K) & [53] \\
\hline MDEA/water & Eq. (27) ${ }^{\text {a }}$ & $6.13(313-353 \mathrm{~K})$ & [54] \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}}$ For the pair MDEA/water, additionally the binary parameter $k_{i j}{ }^{\mathrm{hb}}=0.015$ was applied.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-06.jpg?height=981&width=774&top_left_y=202&top_left_x=165}
\captionsetup{labelformat=empty}
\caption{Fig.1. Isothermal VLE of the system $\mathrm{CO}_{2} /$ water. Left: $p, x$ diagram, right: $p, y$ diagram. Lines: modeling results with ePC-SAFT using the pure-component parameters from Table 3 and the binary $k_{i j}$ in Eq. (26). Symbols: experimental data [53] (304 K: $348 \mathrm{~K}: ~ 366 \mathrm{~K}: ~>, 394 \mathrm{~K}: \star, 422 \mathrm{~K}: \Delta)$.}
\end{figure}

100 bar for temperatures between 304 K and 422 K , respectively. In order to accurately model the VLE in this temperature and pressure range, the $k_{i j}$ was expressed as quadratic function of temperature:

$$
\begin{align*}
k_{i j, \mathrm{CO}_{2}-W} & =-2.2 \times 10^{-2}+4.2 \times 10^{-4}(T[K]-298)-1.7 \\
& \times 10^{-6}(T[K]-298)^{2} \tag{26}
\end{align*}
$$


Fig. 1 illustrates the modeled VLE of $\mathrm{CO}_{2} /$ water system compared to experimental data. Based on the pure-component parameters of water and $\mathrm{CO}_{2}$ as well as the binary $k_{i j}$ function (Eq. (26)), modeled and experimental phase diagrams ( $p, x$ diagram in Fig. 1a and p,y diagram in Fig. 1b) are in good agreement with ARD value of $5.26 \%$ over the whole considered temperature and pressure range.

\subsection*{4.2.3. MDEA/water}

Compared to the binary VLE water/ $\mathrm{CO}_{2}$, the system water/ MDEA exhibits a much more pronounced and complex associative interaction behavior. In order to account for this, a binary interaction parameter $k_{i j}{ }^{\mathrm{bb}}$ according to Eq. (9) was introduced that corrects for deviations from the combining rule used for the cross association-volume parameter. The binary parameters $k_{i j}{ }^{\mathrm{bb}}$ and $k_{i j}$ were fitted simultaneously to experimental VLE data [54] between 313 K and 353 K . The temperature-independent $k_{i j}{ }^{\text {hb }}$ value was found to be 0.015 . The binary interaction parameter $k_{i j}$ was assumed as being a quadratic function of temperature:

$$
\begin{align*}
k_{i j, \mathrm{MDEA}-W} & =-1.5275 \times 10^{-2}-5.24 \times 10^{-5}(T[K]-298) \\
& +7.9 \times 10^{-6}(T[K]-298)^{2} \tag{27}
\end{align*}
$$


Based on the pure-component parameters in Table 3 and the binary parameters in Table 5, the isothermal VLE of the

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-06.jpg?height=541&width=854&top_left_y=202&top_left_x=1063}
\captionsetup{labelformat=empty}
\caption{Fig. 2. Isothermal VLE of the system MDEA/water. Lines: modeling results with ePC-SAFT using the pure-component parameters from Table 3 and the binary $k_{i j}$ in Eq. (27) and a $k_{i j}{ }^{\text {hb }}$ value of 0.015 . Symbols: experimental data [54] ( 313 K : 333 K : -, 353 K: - ).}
\end{figure}
water/MDEA system can be described in good agreement to the experimental data. The modeling results are shown in Fig. 2.

It can be observed from Fig. 2 that the deviations between ePC-SAFT and experimental data are more pronounced at $x_{\text {MDEA }}>0.15$. However, this concentration range ( $x_{\text {MDEA }}>0.15$ ) is not relevant for the considered ternary system $\mathrm{CO}_{2}$ /water/MDEA, where the maximum MDEA mole fraction is roughly 0.07.

\subsection*{4.3. Ternary $\mathrm{CO}_{2} /$ water/MDEA system}

Modeling the $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions requires solving the reaction equilibria and phase equilibria. The influence of electrolytes is taken into consideration explicitly in this work in order to solve the species distribution (Section 4.3.1) and the phase equilibria (Section 4.3.2) in the ternary $\mathrm{CO}_{2}$ /water/ MDEA system, respectively.

\subsection*{4.3.1. Species distribution}

In this chapter the modeling results of the species distribution for the ternary system $\mathrm{CO}_{2} /$ water $/$ MDEA are presented and compared with experimental data. In this context it should be mentioned that only a few experimental data for the species distribution are available for the present system. This is due to the fact that the individual species can hardly be distinguished in analytical methods [55-57]. To validate the modeling results in this work, the experimental data of Bottinger et al. and Jakobsen et al. were used [56,58]. This data is very trustful, as data by Derks et al. [59] are in quantitative agreement to Jakobsen's data.

Eqs. (17)-(20) were applied to calculate the species distribution using the reaction constants listed in Table 1. The mole fractions were replaced with reaction coordination numbers according to Eq. (24) using the starting values given in Table 2. In a first step, all species activity coefficients $\gamma_{i}$ and $\gamma_{i}^{*}$ were set to unity. This yields the species distribution under thermodynamically ideal conditions. In an iterative procedure, the resulting species mole fractions served as an input in order to calculate the species activity coefficients with ePC-SAFT. The species distribution was recalculated accounting for the activity coefficients. This procedure was repeated until the species distributions (and thus activity coefficients) did not change with absolute values of more than $10^{-6}$. One characteristic result is shown in Fig. 3, in which the experimental and modeled species distribution are compared for $w_{\text {MDEA }}=0.23$ at 313 K . It is obvious from Fig. 3 that the modeled mole fractions of MDEA, MDEAH ${ }^{+}$and $\mathrm{HCO}_{3}{ }^{-}$quantitatively agree

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-07.jpg?height=555&width=853&top_left_y=195&top_left_x=157}
\captionsetup{labelformat=empty}
\caption{Fig. 3. Mole-fraction based species distribution in the system $\mathrm{CO}_{2} /$ water/MDEA at $w_{\text {MDEA }}=0.23$ and 313 K . Symbols: experimental data [58] ( $\mathrm{CO}_{2}$ : - , $\mathrm{CO}_{3}{ }^{2-}$ : , MDEAH ${ }^{+}$: ★, $\mathrm{HCO}_{3}{ }^{-}$: □, MDEA: ). Lines: modeling results accounting for activity coefficients modeled with ePC-SAFT using the pure-component parameters and binary parameters listed in Tables 3-5 and the reaction constants in Table 1. The mole fraction of $\mathrm{HCO}_{3}{ }^{-}$is presented as dashed line. The mole fractions of water, $\mathrm{H}^{+}$, and $\mathrm{OH}^{-}$are not shown.}
\end{figure}
with experimental data. Slight deviations can be observed for the mole fractions of $\mathrm{CO}_{3}{ }^{2-}$ and $\mathrm{CO}_{2}$, respectively.

In some literature works, activity coefficients on the species distribution are neglected [51]. In order to show the influence of species activity coefficients on the species distribution, Fig. 4 illustrates the mole fractions of $\mathrm{CO}_{3}{ }^{2-}$ and $\mathrm{CO}_{2}$, obtained from Eqs. (17)-(20) with and without accounting for species activity coefficients, respectively. It can be observed from Fig. 4 that the modeled and experimental mole fractions of $\mathrm{CO}_{3}{ }^{2-}$ and $\mathrm{CO}_{2}$ are in good agreement if species activity coefficients are explicitly accounted for in Eqs. (17)-(20). Neglecting species activity coefficients cause higher deviations from experimental data. Note that the mole fractions of MDEA, MDEAH ${ }^{+}$and $\mathrm{HCO}_{3}{ }^{-}$are not shown in Fig. 4. These can be modeled without accounting for species activity coefficients in good accordance to experimental data. Further, accounting for activity coefficients allows modeling species distribution in quantitative agreement with experimental data from Bottinger et al. [56] at slightly different conditions ( $w_{\text {MDEA }}=0.2,313 \mathrm{~K}$ ) compared to the data from Jakobsen et al. [58] (results not shown).

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-07.jpg?height=535&width=853&top_left_y=1847&top_left_x=157}
\captionsetup{labelformat=empty}
\caption{Fig. 4. Mole fractions of $\mathrm{CO}_{2}$ and $\mathrm{CO}_{3}{ }^{2-}$ in the system $\mathrm{CO}_{2}$ /water/MDEA at $w_{\text {MDEA }}=0.23$ and 313 K . Symbols: experimental data [58] ( $\left.\mathrm{CO}_{2}:, \mathrm{CO}_{3}{ }^{2-}: /\right)$. Full lines: modeling results accounting for activity coefficients modeled with ePC-SAFT using the pure-component parameters and binary parameters listed in Tables 3-5. Dashed lines: modeling results without accounting for activity coefficients. The mole fractions of MDEA, MDEAH ${ }^{+}, \mathrm{HCO}_{3}{ }^{-}$water, $\mathrm{H}^{+}$, and $\mathrm{OH}^{-}$are not shown.}
\end{figure}

\subsection*{4.3.2. VLE}

The VLE of the system CO2/water/MDEA is modeled in this work with ePC-SAFT. The reaction equilibria and the resulting species distribution (including the electrolyte species) are explicitly accounted for. VLE modeling requires the pure-component ePC-SAFT parameters of the volatile components (Table 3) and of the ions (Table 4) and binary interaction parameters. In this work, $k_{i j}$ parameters between $\mathrm{CO}_{2}$ /water (Eq. (26)), MDEA/water (Eq. (27)) and water/ions (Table 5) were applied. Induced association between $\mathrm{CO}_{2}$ /water and between $\mathrm{CO}_{2}$ /MDEA was not considered. Induced association between MDEAH ${ }^{+}$/MDEA and between MDEAH ${ }^{+}$/water was explicitly accounted for. The binary interaction parameter between MDEAH ${ }^{+}$/water was inherited from MDEA/water, expressed by Eq. (26). Further, the VLE calculations with ePC-SAFT are based on the composition of the liquid phase at constant temperature and constant MDEA weight fraction (related to the binary water/MDEA system). The composition in the liquid phase used as input for the isofugacity criteria (Eq. (1)) was obtained by solving the reaction equilibria according to Section 4.3.1. The fugacity coefficients of the volatile components were modeled by Eq. (2); the influence of electrolytes on fugacity coefficients is explicitly accounted for by the Coulomb interactions described via the Debye-Hückel theory.

Based on this, the VLE of the system $\mathrm{CO}_{2}$ /water/MDEA at $w_{\text {MDEA }}=0.19$ (related to the binary water/MDEA system) was predicted in a temperature range between 313 K and 413 K up to $\mathrm{CO}_{2}$ loading of 1.4 mole $\mathrm{CO}_{2}$ per mole MDEA. Fig. 5 compares the ePC-SAFT predictions with the experimental data available from Kuranov et al. [17]. An accurate description is possible especially at temperatures larger than 333 K . For moderate temperatures ( $<333 \mathrm{~K}$ ) quantitative predictions are possible for a $\mathrm{CO}_{2}$ loading $\alpha<1.05$; this region is of highest industrial relevance. The ePC-SAFT predictions and the experimental data at the conditions ( $313 \mathrm{~K}<T<413 \mathrm{~K}, 0.01<\alpha<1.32, w_{\text {MDEA }}=0.19$ ) deviate with an ARD value of $19.22 \%$ only. Keeping in mind that no parameters were fitted to experimental data of the ternary $\mathrm{CO}_{2} /$ water $/ \mathrm{MDEA}$ system, this is an excellent result. From Fig. 5 it can be observed that deviations are mainly due to modeling inaccuracies at 313 K and 323 K . ARD values of $<10 \%$ are obtained for temperatures $\geq 373 \mathrm{~K}$.

In Fig. 5, rather the high-pressure region is illustrated. In order to compare ePC-SAFT predictions and experimental data also at the low-pressure region, Fig. 6 shows the logarithm of the $\mathrm{CO}_{2}$ partial pressure $p_{\mathrm{CO}_{2}}$ at the same MDEA weight fractions and similar temperatures as in Fig. 5. It can be observed from Fig. 6 that the

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-07.jpg?height=559&width=856&top_left_y=1890&top_left_x=1087}
\captionsetup{labelformat=empty}
\caption{Fig. 5. Isothermal VLE of the system $\mathrm{CO}_{2} /$ water $/ \mathrm{MDEA}$ at $w_{\text {MDEA }}=0.19$. Lines: prediction results with ePC-SAFT using the pure-component parameters from Tables $3-4$ and the binary $k_{i j}$ s in Table 5. Symbols: experimental data from Kuranov et al. [17] ( $313 \mathrm{~K}: \diamond, 333 \mathrm{~K}: \square, 373 \mathrm{~K}: \underset{\star}{\star}, 393 \mathrm{~K}: \underset{\triangle}{\Delta}, 413 \mathrm{~K}: \Theta)$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-08.jpg?height=517&width=847&top_left_y=198&top_left_x=129}
\captionsetup{labelformat=empty}
\caption{Fig. 6. Isothermal partial $\mathrm{CO}_{2}$ pressures in the system $\mathrm{CO}_{2}$ /water/MDEA at $w_{\text {MDEA }}=0.19$. Lines: prediction results with ePC-SAFT using the pure-component parameters from Tables $3-4$ and the binary $k_{i j} s$ in Table 5. Symbols: experimental data [60,61] (313 K: », $343 \mathrm{~K}: \Delta, 373 \mathrm{~K}: \star, 393 \mathrm{~K}: \square$ ).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de35ad1a-166e-41d0-b1ad-9a01f717eb59-08.jpg?height=520&width=851&top_left_y=934&top_left_x=127}
\captionsetup{labelformat=empty}
\caption{Fig. 7. Isothermal partial $\mathrm{CO}_{2}$ pressures in the system $\mathrm{CO}_{2}$ /water/MDEA at $w_{\text {MDEA }}=0.3$. Lines: prediction results with ePC-SAFT using the pure-component parameters from Tables $3-4$ and the binary $k_{i j} s$ in Table 5. Symbols: experimental data [62] ( $313 \mathrm{~K}:, 333 \mathrm{~K}: \triangle, 353 \mathrm{~K}: \star, 373 \mathrm{~K}: \square$ ).}
\end{figure}
ePC-SAFT predictions are in good agreement with the experimental $p_{\mathrm{CO}_{2}}$ data from Ermatchkov et al. [60] and Jou et al. [61], respectively, also at the lower-pressure region.

Figs. 5 and 6 are related to a constant MDEA weight fraction of 0.19 . It is shown that species distribution ( $w_{\text {MDEA }}=0.23$, Figs. 3 and 4 ) as well the VLE ( $w_{\text {MDEA }}=0.19$, Figs. 5 and 6 ) can be predicted in good agreement to experimental data. In order to compare ePCSAFT predictions and experimental data also at higher MDEA weight fractions, Fig. 7 shows the logarithm of the $\mathrm{CO}_{2}$ partial pressure $p_{\mathrm{CO}_{2}}$ at $w_{\text {MDEA }}=0.3$ at temperatures between 313 K and 373 K and $\mathrm{CO}_{2}$ loadings up to 1.26 , respectively. It can be observed from Fig. 7 that the ePC-SAFT predictions are in good agreement with the experimental $p_{\mathrm{CO}_{2}}$ data from Jou et al. [62]. The ePC-SAFT
predictions for the total pressure at $w_{\text {MDEA }}=0.32$ between 313 K and 413 K (data from Kuranov et al. [17]) are worse (ARD $=25.91 \%$ ) compared to the predictions at $w_{\text {MDEA }}=0.19$ ( $\mathrm{ARD}=19.22 \%$ ).

The results presented until here (illustrated in Figs. 3-7) are limited to MDEA weight fractions of up to 0.32 . Many data exist in the literature containing $\mathrm{CO}_{2}$ solubility in more concentrated MDEA solutions, especially the works from the groups of Chen and Maurer shall be mentioned [13,18]. Although not within the focus, we briefly investigated the capability of ePC-SAFT to predict $\mathrm{CO}_{2}$ solubility in solutions containing $w_{\text {MDEA }}=0.5$ at rather low temperatures. At these conditions, association behavior of MDEAH ${ }^{+}$becomes more pronounced, and effects caused by influences on the dielectric constant significantly increase. Although not shown graphically, as a result ARD values of $43 \%$ were observed at temperatures of 298 and 323 K at $\mathrm{CO}_{2}$ loadings $0.3<\alpha<0.7$, respectively. Without accounting for dielectric constant and MDEAH ${ }^{+}$cross association, predictions strongly overestimated $\mathrm{CO}_{2}$ solubility in solutions containing $w_{\text {MDEA }}=0.5$ at 298 and 323 K , respectively.

These results show that more research has to be done on permittivity studies of electrolyte solutions. The other way around, the availability of predictive ePC-SAFT allows fitting permittivity to experimental $\mathrm{CO}_{2}$ solubility data, which might be addressed in future works.

In order to have an imagination of the presence of electrolytes on the residual Helmholtz energy, the energy contributions to $a^{\text {res }}$ in Eq. (4) were investigated at $323 \mathrm{~K}, w_{\text {MDEA }}=0.5$, and $\alpha_{\mathrm{CO}_{2}}=1.358$. As a result, $a^{\text {ion }}$ contributes with $5 \%$ to $a^{\text {res }}$. This contribution is still low considering the fact that the mole fractions of all ions ( $\mathrm{H}^{+}, \mathrm{OH}^{-}, \mathrm{MDEAH}^{+}, \mathrm{HCO}_{3}{ }^{-}, \mathrm{CO}_{3}{ }^{2-}$ ) add up to 0.1108 .

\subsection*{4.3.3. Comparison to literature models}

In the literature, many approaches have been developed and applied so far in order to model the solubility of $\mathrm{CO}_{2}$ in aqueous MDEA and other amine solutions. In almost all existing literature works, interaction parameters have been fitted to experimental data in the ternary $\mathrm{CO}_{2}$ /water/amine system. Many examples for $\mathrm{g}^{\mathrm{E}}$ models can be found in literature (UNIQUAC [16], Pitzer model [17-20]) that require fitting parameters in order to model the $\mathrm{CO}_{2}$ solubility in aqueous amine solutions reasonably. Interaction parameters were also fitted for equations of state that have been applied to the ternary $\mathrm{CO}_{2}$ /water/amine system (SAFT [23], PC-SAFT [24], ePR EOS [21]). In a more recent work, Pahlavanzadeh and Fakouri Baygi [25] showed that PC-SAFT combined with chemical reaction equilibria allows predicting $\mathrm{CO}_{2}$ solubilities in aqueous MDEA solutions with good agreement to experimental data. In their work, the influence of electrolytes was not explicitly taken into account.

Table 6 lists several models that have been applied so far to model the $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions so far. Table 6 contains published ARD values between modeled and experimental data. All ARD numbers refer to the data of Kuranov et al. [17] at $w_{\text {MDEA }}=0.19$ and $w_{\text {MDEA }}=0.32$ for the whole temperature range

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 6
Comparison of the predictions using ePC-SAFT (this work) with modeling results obtained from literature, expressed as ARD values (\%) between modeled and experimental total pressures (data from Kuranov et al. [17]) in the $\mathrm{CO}_{2} /$ water $/$ MDEA system. Whole data range was used $\left(313 \mathrm{~K}<T<413 \mathrm{~K}\right.$, $w_{\text {MDEA }}=\{0.19$ and 0.32$\left.\}, \alpha_{\mathrm{CO}_{2}}<1.316\right)$ for ARD calculations.}
\begin{tabular}{|l|l|l|l|}
\hline Model & Number of fitting parameters ${ }^{\text {a }}$ & NP & ARD (\%) \\
\hline Electrolyte Peng-Robinson [21] & 5 & 81 & 10.1 \\
\hline Fürst and Renon EOS [63] & 4 & 81 & 17.8 \\
\hline Electrolyte Soave-Redlich-Kwong [32] & 5 & 64 & 20.0 \\
\hline PC-SAFT [51] & 0 & 82 & 26.4 \\
\hline ePC-SAFT [this work] & 0 & 82 & 22.9 \\
\hline
\end{tabular}
\end{table}

\footnotetext{
${ }^{\mathrm{a}}$ Binary interaction parameters that were fitted to the experimental $\mathrm{CO}_{2}$ solubility data in aqueous MDEA solutions.
}
( $313-413 \mathrm{~K}$ ), respectively. The highest $\mathrm{CO}_{2}$ loadings considered in the measurements of Kuranov et al. (and thus also in the ARD values in Table 6) were $1.316\left(w_{\text {MDEA }}=0.19\right.$ at 313 K ) and 1.157 ( $w_{\text {MDEA }}=0.32$ at 313 K ), respectively. Table 6 only compiles state-of-the-art EOS, $\mathrm{g}^{\mathrm{E}}$ models were not considered. All models considered in Table 6 explicitly account for the reaction equilibria in order to describe the $\mathrm{CO}_{2}$ solubility. It becomes obvious from Table 6 that only two models have been applied so far to predict the $\mathrm{CO}_{2}$ solubility in water/MDEA solutions, PC-SAFT [51] and ePCSAFT [this work]. Applying the other models required binary interaction parameters that were fitted to the ternary $\mathrm{CO}_{2}$ /water/ MDEA system; usually four to five interaction parameters were used, mainly $k_{i j}$ values between MDEAH ${ }^{+}$/non-ionic species and MDEAH ${ }^{+}$/ionic species. A non-negligible amount of ions is present in the liquid phased of the $\mathrm{CO}_{2}$ /water/MDEA system. Thus, researchers usually account for Coulomb forces among the ions via the electrolyte theories of Debye-Hückel, Born, or/and MSA. The drawback of this is the need for pure-component parameters for MDEAH ${ }^{+}$. The models listed in Table 6 are electrolyte models, except for PC-SAFT [51]. Applying PC-SAFT (neglecting chargeinduced interactions) does neither require pure-ion parameters nor ion-related binary interaction parameters. However, neglecting the presence of electrolytes in $\mathrm{CO}_{2}$ /water/MDEA solutions is a harsh assumption. Nevertheless, this approach allows predicting $\mathrm{CO}_{2}$ solubility in very good agreement to experimental data. Accounting for the presence of electrolytes in reaction and phase equilibria allows predicting the $\mathrm{CO}_{2}$ solubility ( $313 \mathrm{~K}<T<413 \mathrm{~K}$, $w_{\text {MDEA }}=\{0.19$ and 0.32$\}$ ) with an ARD value of $22.9 \%$, whereas a slightly higher deviation is obtained without considering the influence of electrolytes ( $\mathrm{ARD}=26.4 \%$ ). This shows that the system is mainly determined by associative forces, that are explicitly considered using €PC-SAFT. Applying ePC-SAFT for modeling $\mathrm{CO}_{2}$ solubilities in aqueous amine solutions is promising as correlative models (with four to five binary interaction parameters) yield similar ARD values compared to ePC-SAFT.

In summary, ePC-SAFT can be recommended to predict $\mathrm{CO}_{2}$ solubilities in aqueous amine solutions for broad conditions of temperature, $\mathrm{CO}_{2}$ loading, and amine weight fraction, respectively. The advantage using ePC-SAFT is that fitting binary interaction parameters to ternary $\mathrm{CO}_{2}$ /water/amine systems is not required. However, such parameters can generally be introduced in order to model such systems with higher accuracy. Introducing a binary interaction parameter $k_{i j}$ between water and MDEAH ${ }^{+}$in order to model $\mathrm{CO}_{2}$ solubilities at $313 \mathrm{~K}<T<413 \mathrm{~K}$ and $w_{\text {MDEA }}=0.19$ with ePC-SAFT reduces the ARD to $\ll 10 \%$, respectively (results not shown).

\section*{5. Conclusion}

In the literature, many models have been proposed for modeling VLEs of $\mathrm{CO}_{2}$ /water/amine systems. However, the accuracy of the models is still not satisfying considering the number of interaction parameters used to correlate the experimental data in such ternary systems. It was the aim of this work to predict the $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions with ePC-SAFT [39] in broad ranges of temperature, $\mathrm{CO}_{2}$ loading, and MDEA weight fraction, respectively.

In the first steps, binary interaction parameters for the pairs $\mathrm{CO}_{2}$ /water and MDEA/water were adjusted to experimental VLE data. Caused by the reactions in the liquid phase in $\mathrm{CO}_{2}$ /water/ MDEA solutions, eight components are present in the system: $\mathrm{CO}_{2}$, water, MDEA, MDEAH ${ }^{+}, \mathrm{H}^{+}, \mathrm{OH}^{-}, \mathrm{HCO}_{3}{ }^{-}$, and $\mathrm{CO}_{3}{ }^{2-}$. Required purecomponent parameters for all these components and binary interaction parameters for ion/water pairs were taken from literature when available. All other binary parameters were set to zero in this work. The influence of electrolytes on activity
coefficients was explicitly accounted for in order to calculate the reaction equilibrium as well as the phase equilibrium, respectively.

Based on pure-component parameters and binary interaction parameters, $\mathrm{CO}_{2}$ solubilities in aqueous MDEA solutions were predicted with ePC-SAFT. It could be shown that experimental data could be predicted with good agreement to experimental data; that is, binary interaction parameters have not been adjusted to experimental data of the ternary $\mathrm{CO}_{2}$ /water/MDEA system. Relatively low ARD values were obtained for the ePC-SAFT predictions ( $22.9 \%$ ). ePC-SAFT predicts the data with very good accuracy at lower MDEA weight fractions and higher temperatures. The deviations to experimental data increase with increasing MDEA weight fraction and at temperatures lower than 333 K .

Compared with other models applied in the literature satisfactory accuracies were obtained by the ePC-SAFT predictions considering the fact that interaction parameters have not been adjusted to experimental $\mathrm{CO}_{2}$ solubilities in the ternary system. These results are highly promising and could serve as a basis to investigate additional components(e.g., $\mathrm{CH}_{4}$, other amines) in future works. Finally, it has to be mentioned that a complete electrolyte model should also account for changes of the dielectric constant of electrolyte solutions. However, a highly complex experimental dielectric behavior is expected in the considered system with dependencies on temperature, MDEA concentration, and ion concentrations. Caused by the non-availability of such data, the dielectric constant of the medium was assumed to be the same as water/MDEA mixture upon modeling the complex solutions.

\section*{References}
[1] Bundesministerium für Wirtschaft und Technologie, Der Weg zum zukunftsfähigen Kraftwerk mit fossilen Brennstoffen, Bundesministerium für Wirtschaft und Technologie, Berlin, 2007.
[2] R.R. Bottoms, Process for Separating Acidic Gases, Girdler Corporation, United States, 1930.
[3] Y.E. Kim, J.A. Lim, S.K. Jeong, Y.I. Yoon, S.T. Bae, S.C. Nam, Comparison of carbon dioxide absorption in aqueous MEA, DEA, TEA, and AMP solutions, Bull. Korean Chem. Soc. 34 (2013) 783-787.
[4] A.L. Kohl, R.B. Nielsen, Knovel (Firm), Gas Purification, Gulf Publishing, Houston, Texas, 1997.
[5] C. Held, A. Prinz, V. Wallmeyer, G. Sadowski, Measuring and modeling alcohol/ salt systems, Chem. Eng. Sci. 68 (2012) 328-339.
[6] C. Held, T. Reschke, R. Müller, W. Kunz, G. Sadowski, Measuring and modeling aqueous electrolyte/amino-acid solutions with ePC-SAFT, J. Chem. Thermodyn. 68 (2014) 1-12.
[7] M. Sadeghi, C. Held, A. Samieenasab, C. Ghotbi, M.J. Abdekhodaie, V. Taghikhani, G. Sadowski, Thermodynamic properties of aqueous salt containing urea solutions, Fluid Phase Equilibr. 325 (2012) 71-79.
[8] P. Debye, E. Hückel, Zur Theorie der Elektrolyte. I. Gefrierpunktserniedrigung und verwandte Erscheinungen, Phys. Z. 24 (1923) 185-206.
[9] B. Maribo-Mogensen, G.M. Kontogeorgis, K. Thomsen, Comparison of the Debye-Huckel and the mean spherical approximation theories for electrolyte solutions, Ind. Eng. Chem. Res. 51 (2012) 5353-5363.
[10] B. Maribo-Mogensen, G.M. Kontogeorgis, K. Thomsen, Modeling of dielectric properties of complex fluids with an equation of state, J. Phys. Chem. B 117 (2013) 3389-3397.
[11] V.D. Pitsinigos, A.I. Lygeros, Predicting $\mathrm{H}_{2} \mathrm{~S}-\mathrm{MEA}$ equilibria, Hydrocarb. Process. 68 (1989) 43-44.
[12] M.L. Posey, G.T. Rochelle, A thermodynamic model of methyldiethanolamine-$\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$-water, Ind. Eng. Chem. Res. 36 (1997) 3944-3953.
[13] D.M. Austgen, G.T. Rochelle, C.C. Chen, Model of vapor-liquid equilibria for aqueous acid gas-alkanolamine systems. 2. Representation of $\mathrm{H}_{2} \mathrm{~S}$ and $\mathrm{CO}_{2}$ solubility in aqueous MDEA and $\mathrm{CO}_{2}$ solubility in aqueous mixtures of MDEA with MEA or DEA, Ind. Eng. Chem. Res. 30 (1991) 543-555.
[14] Y. Zhang, C.C. Chen, Thermodynamic modeling for $\mathrm{CO}_{2}$ absorption in aqueous MDEA solution with electrolyte NRTL model, Ind. Eng. Chem. Res. 50 (2011) 163-175.
[15] C.C. Chen, H.I. Britt, J.F. Boston, L.B. Evans, Local composition model for excess Gibbs energy of electrolyte systems. Part I: single solvent single completely dissociated electrolyte systems, AIChE J. 28 (1982) 588-596.
[16] L. Faramarzi, G.M. Kontogeorgis, K. Thomsen, E.H. Stenby, Extended UNIQUAC model for thermodynamic modeling of $\mathrm{CO}_{2}$ absorption in aqueous alkanolamine solutions, Fluid Phase Equilibr. 282 (2009) 121-132.
[17] G. Kuranov, B. Rumpf, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of $N$-methyldiethanolamine in the temperature range $313-413$ K at pressures up to 5 MPa , Ind. Eng. Chem. Res. 35 (1996) 1959-1966.
[18] Á.P.-S. Kamps, A. Balaban, M. Jödecke, G. Kuranov, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of $N$-methyldiethanolamine at temperatures from 313 to 393 K and pressures up to 7.6 MPa : new experimental data and model extension, Ind. Eng. Chem. Res. 40 (2001) 696-706.
[19] K.S. Pitzer, Thermodynamics of electrolytes; I. theoretical basis and general equations, J. Phys. Chem. 77 (1973) 268-277.
[20] H. Arcis, L. Rodier, K. Ballerat-Busserolles, J.Y. Coxam, Modeling of (vapor plus liquid) equilibrium and enthalpy of solution of carbon dioxide ( $\mathrm{CO}_{2}$ ) in aqueous methyldiethanolamine (MDEA) solutions, J. Chem. Thermodyn. 41 (2009) 783-789.
[21] A.T. Zoghi, F. Feyzi, M.R. Dehghani, Modeling $\mathrm{CO}_{2}$ solubility in aqueous $N$-methyldiethanolamine solution by electrolyte modified Peng-Robinson plus association equation of state, Ind. Eng. Chem. Res. 51 (2012) 9875-9885.
[22] A.S. Avlund, G.M. Kontogeorgis, M.L. Michelsen, Modeling systems containing alkanolamines with the CPA equation of state, Ind. Eng. Chem. Res. 47 (2008) 7441-7446.
[23] J.K. Button, K.E. Gubbins, SAFT prediction of vapour-liquid equilibria of mixtures containing carbon dioxide and aqueous monoethanolamine or diethanolamine, Fluid Phase Equilibr. 158 (1999) 175-181.
[24] K. Nasrifar, A.H. Tafazzol, Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions using the PC-SAFT equation of state, Ind. Eng. Chem. Res. 49 (2010) 7620-7630.
[25] H. Pahlavanzadeh, S. Fakouri Baygi, Modeling $\mathrm{CO}_{2}$ solubility in aqueous methyldiethanolamine solutions by perturbed chain-SAFT equation of state, J. Chem. Thermodyn. 59 (2013) 214-221.
[26] J.A. Myers, S.I. Sandler, R.H. Wood, An equation of state for electrolyte solutions covering wide ranges of temperature, pressure, and composition, Ind. Eng. Chem. Res. 41 (2002) 3282-3297.
[27] C. Held, L.F. Cameretti, G. Sadowski, Modeling aqueous electrolyte solutions. Part 1: fully dissociated electrolytes, Fluid Phase Equilibr. 270 (2008) 87-96
[28] X.Y. Ji, H. Adidharma, Ion-based SAFT2 to represent aqueous single- and multiple-salt solutions at 298.15 K, Ind. Eng. Chem. Res. 45 (2006) 7719-7728.
[29] A. Galindo, A. Gil-Villegas, G. Jackson, A.N. Burgess, SAFT-VRE: phase behavior of electrolyte solutions with the statistical associating fluid theory for potentials of variable range, J. Phys. Chem. B 103 (1999) 10272-10281.
[30] S.P. Tan, H. Adidharma, M. Radosz, Recent advances and applications of statistical associating fluid theory, Ind. Eng. Chem. Res. 47 (2008) 8063-8082.
[31] X.Y. Ji, S.P. Tan, H. Adidharma, M. Radosz, Statistical associating fluid theory coupled with restrictive primitive model extended to bivalent ions. SAFT2: 2. brine/seawater properties predicted, J. Phys. Chem. B 110 (2006) 16700-16706.
[32] P.J.G. Huttenhuis, N.J. Agrawal, E. Solbraa, G.F. Versteeg, The solubility of carbon dioxide in aqueous $N$-methyldiethanolamine solutions, Fluid Phase Equilibr. 264 (2008) 99-112.
[33] L.F. Cameretti, G. Sadowski, J.M. Mollerup, Modeling of aqueous electrolyte solutions with perturbed-chain statistical associated fluid theory, Ind. Eng. Chem. Res. 44 (2005) 3355-3362 ibidem, 8944.
[34] W.G. Chapman, G. Jackson, K.E. Gubbins, Phase-equilibria of associating fluids chain molecules with multiple bonding sites, Mol. Phys. 65 (1988) 1057-1079.
[35] W.G. Chapman, K.E. Gubbins, G. Jackson, M. Radosz, New reference equation of state for associating liquids, Ind. Eng. Chem. Res. 29 (1990) 1709-1721.
[36] J. Gross, G. Sadowski, Perturbed-chain SAFT: an equation of state based on a perturbation theory for chain molecules, Ind. Eng. Chem. Res. 40 (2001) 1244-1260.
[37] C. Held, T. Neuhaus, G. Sadowski, Thermodynamic properties of aqueous ectoine, proline, and urea solutions - measurement and modeling, Biophys. Chem. 152 (2010) 28-39.
[38] C. Held, G. Sadowski, Modeling aqueous electrolyte solutions. Part 2: weak electrolytes, Fluid Phase Equilibr. 279 (2009) 141-148.
[39] C. Held, T. Reschke, S. Mohammad, A. Luza, G. Sadowski, ePC-SAFT revised, Chem. Eng. Res. Des. 92 (2014) 2884-2897.
[40] W.B. Floriano, M.A.C. Nascimento, Dielectric constant and density of water as a function of pressure at constant temperature, Br. J. Phys. 34 (2004) 38-41.
[41] C.J. Hsieh, J.M. Chen, M.H. Li, Dielectric constants of aqueous diisopropanolamine, diethanolamine, $\quad N$-methyldiethanolamine,
triethanolamine, and 2-amino-2-methyl-1-propanol solutions, J. Chem. Eng. Data 52 (2007) 619-623.
[42] J.P. Wolbach, S.I. Sandler, Using molecular orbital calculations to describe the phase behavior of cross-associating mixtures, Ind. Eng. Chem. Res. 37 (1998) 2917-2928.
[43] A. Nann, C. Held, G. Sadowski, Liquid-liquid equilibria of 1-butanol/water/IL systems, Ind. Eng. Chem. Res. 52 (2013) 18472-18481.
[44] M. Sadeghi, C. Held, C. Ghotbi, M.J. Abdekhodaie, G. Sadowski, Thermodynamic properties of aqueous glucose-urea-salt systems, J. Sol. Chem. (2014) .
[45] J.A. Barker, D. Henderson, Perturbation theory and equation of state for fluids - square-well potential, J. Chem. Phys. 47 (1967) 2856-2861.
[46] C.S. Patterson, G.H. Slocum, R.H. Busey, R.E. Mesmer, Carbonate equilibria in hydrothermal systems: first ionization of carbonic acid in NaCl media to $300^{\circ} \mathrm{C}$, Geochim. Cosmochim. Acta 46 (1982) 1653-1663.
[47] C.S. Patterson, R.H. Busey, R.E. Mesmer, Second ionization of carbonic acid in NaCl media to $250^{\circ} \mathrm{C}$, J. Sol. Chem. 13 (1984) 647-661.
[48] A.P.S. Kamps, G. Maurer, Dissociation constant of $N$-methyldiethanolamine in aqueous solution at temperatures from 278 K to 368 K , J. Chem. Eng. Data 41 (1996) 1505-1513.
[49] M. Luckas, J. Krissmann, Thermodynamik der Elektrolytlösungen eine einheitliche Darstellung der Berechnung komplexer Gleichgewichte, Springer, Berlin, 2001.
[50] D. Fuchs, J. Fischer, F. Tumakaka, G. Sadowski, Solubility of amino acids: influence of the pH value and the addition of alcoholic cosolvents on aqueous solubility, Ind. Eng. Chem. Res. 45 (2006) 6578-6584.
[51] H. Pahlavanzadeh, S.F. Baygi, Modeling $\mathrm{CO}_{2}$ solubility in aqueous methyldiethanolamine solutions by perturbed chain-SAFT equation of state, J. Chem. Thermodyn. 59 (2013) 214-221.
[52] L.F. Cameretti, G. Sadowski, Modeling of aqueous amino acid and polypeptide solutions with PC-SAFT, Chem. Eng. Process. 47 (2008) 1018-1025.
[53] P.C. Gillespie, G.M. Wilson, Vapor-liquid and liquid-liquid equilibria: watermethane, water-carbon dioxide, water-hydrogen sulfide, water- $n$-pentane, water-methane-n-pentane, GPA research report RR-48 1982.
[54] I. Kim, H.F. Svendsen, E. Børresen, Ebulliometric determination of vapor-liquid equilibria for pure water, monoethanolamine, $N$-methyldiethanolamine, 3-(methylamino)-propylamine, and their binary and ternary solutions, J. Chem. Eng. Data 53 (2008) 2521-2531.
[55] W. Bottinger, M. Maiwald, H. Hasse, Online NMR spectroscopic study of species distribution in MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ and DEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$, Fluid Phase Equilibr. 263 (2008) 131-143.
[56] W. Bottinger, M. Maiwald, H. Hasse, Online NMR spectroscopic study of species distribution in MDEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ and MDEA-PIP- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$, Ind. Eng. Chem. Res. 47 (2008) 7917-7926.
[57] V. Ermatchkov, A.P.S. Kamps, G. Maurer, Chemical equilibrium constants for the formation of carbamates in (carbon dioxide plus piperazine plus water) from H-1-NMR-spectroscopy, J. Chem. Thermodyn. 35 (2003) 1277-1289.
[58] J.P. Jakobsen, J. Krane, H.F. Svendsen, Liquid-phase composition determination in $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$-alkanolamine systems: an NMR study, Ind. Eng. Chem. Res. 44 (2005) 9894-9903.
[59] P.W.J. Derks, P.J.G. Huttenhuis, J.-H. van Aken, a.G..F. Mars, G.F. Versteeg, Determination of the liquid-phase speciation in the MDEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ system, Energy Procedia 4 (2011) 599-605.
[60] V. Ermatchkov, A.P.S. Kamps, G. Maurer, Solubility of carbon dioxide in aqueous solutions of $N$-methyldiethanolamine in the low gas loading region, Ind. Eng. Chem. Res. 45 (2006) 6081-6091.
[61] F.Y. Jou, A.E. Mather, F.D. Otto, Solubility of $\mathrm{H}_{2} \mathrm{~S}$ and $\mathrm{CO}_{2}$ in aqueous methyldiethanolamine solutions, Ind. Eng. Chem. Process Des. Dev. 21 (1982) 539-544.
[62] F.Y. Jou, F.D. Otto, A.E. Mather, Vapor-liquid equilibrium of carbon-dioxide in aqueous mixtures of monoethanolamine and methyldiethanolamine, Ind. Eng. Chem. Res. 33 (1994) 2002-2005.
[63] P.W.J. Derks, J.A. Hogendoorn, G.F. Versteeg, Experimental and theoretical study of the solubility of carbon dioxide in aqueous blends of piperazine and $N$-methyldiethanolamine, J. Chem. Thermodyn. 42 (2010) 151-163.