\title{
Modeling solubility of $\mathrm{CO}_{2}$ in aqueous monoethanolamine (MEA) solution using SAFT-HR equation of state
}

\author{
Azam Najafloo*, Samane Zarei \\ Department of Chemical Engineering, Central Tehran Branch, Islamic Azad University, Tehran, Iran
}

\section*{ARTICLE INFO}

\section*{Article history:}

Received 8 March 2017
Received in revised form
28 September 2017
Accepted 29 September 2017
Available online 4 October 2017

\section*{Keywords:}

SAFT-HR EOS
$\mathrm{CO}_{2}$ absorption
Monoethanolamine
Association scheme
Vapor-liquid equilibrium

\begin{abstract}
A rigorous thermodynamics model of $\mathrm{CO}_{2}$ absorption by monoethanolamine (MEA) is essential to model treatment of acid gases by aqueous MEA. In this study, the statistical associating fluid theory (SAFT) is applied for modeling the $\mathrm{CO}_{2}$ absorption by MEA. The pure component properties of MEA, vapor-liquid equilibrium properties of binary MEA- $\mathrm{H}_{2} \mathrm{O}$ and ternary MEA- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ are evaluated by considering the SAFT expression of Huang and Radosz (SAFT-HR). Consequently, pure component and binary interaction parameters of the SAFT-HR equation of state (EOS) for MEA are calculated utilizing the experimental data. The association scheme 2 B is chosen with examining different association schemes $2 \mathrm{~B}, 3 \mathrm{~B}$ and 4 C , and considering the capability of the model in prediction of pure component properties. It is also assumed that activities of species in chemical equilibrium equal to their mole fractions. The model predictions show a good agreement with the experimental data. Meanwhile, absolute average deviation percentage of ternary MEA- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ system by the SAFT-HR EOS is $34.71 \%$ which it is less than $36.42 \%$ and $42.29 \%$ for the PC-SAFT EOS and e-NRTL model, respectively.
\end{abstract}
© 2017 Elsevier B.V. All rights reserved.

\section*{1. Introduction}

Sweetening of acid gas which it mainly composed of hydrogen sulfide ( $\mathrm{H}_{2} \mathrm{~S}$ ) and carbon dioxide ( $\mathrm{CO}_{2}$ ), are generally done by absorption process. Sweetening process of acid gas is made via aqueous solutions of alkanolamines. Monoethanolamine (MEA) and methyl diethanolamine (MDEA) are some examples of alkanolamines used in the absorption process. Among them, aqueous MEA solutions have been used extensively for this purpose due to the rapid reaction rate, low cost of the solvent, ease of reclaiming, reasonable thermal stability, low molecular weight, high absorbing capacity on a mass basis, and relatively low solubility of hydrocarbons in the solution [1]. The absorption process by MEA is done by $\mathrm{CO}_{2}$ capture from acid gas. Consequently, a rigorous model for precise description of $\mathrm{CO}_{2}$ absorption is necessary.

Vapor-liquid equilibria (VLE) characterizations of water- $\mathrm{CO}_{2}$ alkanomine systems are obtained via three methods including empirical correlations, excess Gibbs energy and equation of state (EOS) models. Several researchers [2-4] used Kent-Eisenberg [5] model in representation of water- $\mathrm{CO}_{2}$-Alkanoamine systems. The

\footnotetext{
* Corresponding author.

E-mail address: najaflooazam@gmail.com (A. Najafloo).
}
empirical methods such as Kent-Eisenberg [5] based on chemical reaction equilibrium in the liquid phase have poor extrapolation capabilities [6].

Several researchers applied the excess Gibbs energy method in their studies. Deshmukh and Mather [7] predicted partial pressure of the acid gases over MEA solutions by a mathematical model based on extended Debye-Hückel theory. Austgen et al. [8,9] used electrolyte-NRTL model in defining aqueous acid gas-alkanolamine systems. The Deshmukh-Mather thermodynamic model for MEA by Weiland et al. [10] and Jou et al. [11], pitzer equation by Kamps et al. [12], extended UNIQUAC model by faramarzi et al. [13] and the electrolyte-NRTL equation for MEA solution by Zhang et al. [14] are some examples of applications of the excess Gibbs energy method for ternary component systems of water- $\mathrm{CO}_{2}$-alkanomine.

One of main disadvantages of the excess Gibbs energy model is requirement of a large number of complicated adjustable binary interaction parameters that must be correlated to multicomponent system of experimental data. For example, Faramazi et al. [13] in their study, adjusted 36 parameters of extended UNIQUAC model for prediction of $\mathrm{CO}_{2}$ solubility in MEA solutions. In the EOS model, the multicomponent system of experimental data is not necessary and only binary interaction energy parameters are fitted.

Some studies reported the VLE prediction of water- $\mathrm{CO}_{2}$-alkanomine systems using the EOS models. In case of association

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1
Pure component parameters of SAFT-HR EOS.}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Name of compound} & \multirow[t]{2}{*}{Association scheme} & \multirow[t]{2}{*}{T range/K} & \multirow[t]{2}{*}{$m$} & \multirow[t]{2}{*}{$\mathrm{u}^{0} / \mathrm{k} / \mathrm{K}$} & \multirow[t]{2}{*}{$\nu^{00} / \mathrm{mL} . \mathrm{mol}^{-1}$} & \multirow[t]{2}{*}{$\varepsilon^{\mathrm{A}_{\mathrm{i}} \mathrm{B}_{\mathrm{j}}} / \mathrm{k} / \mathrm{K}$} & \multirow[t]{2}{*}{$K^{A_{i} B_{j}}$} & \multicolumn{2}{|l|}{\%AAD} & \multirow[t]{2}{*}{Ref.} \\
\hline & & & & & & & & $p^{\text {sat }}$ & $\rho^{l}$ & \\
\hline \multirow[t]{3}{*}{MEA} & 2B & 285-400 & 2.034 & 447.504 & 18.452 & 2860.654 & 0.00222 & 1.2 & 0.5 & This work \\
\hline & 3B & 285-400 & 4.278 & 207.431 & 7.227 & 3390.102 & 0.01829 & 2.0 & 1.1 & This work \\
\hline & 4C & 285-400 & 1.838 & 488.148 & 21.349 & 1860.732 & 0.00263 & 2.5 & 0.2 & This work \\
\hline $\mathrm{H}_{2} \mathrm{O}$ & 3B & 283-613 & 1.179 & 528.17 & 10.000 & 1809.00 & 0.01593 & 1.3 & 3.2 & [22] \\
\hline \multicolumn{2}{|l|}{$\mathrm{CO}_{2}$} & 218-288 & 1.417 & 216.08 & 13.578 & & & 2.8 & 0.86 & [22] \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2
AAD\% of VLE calculations for MEA- $\mathrm{H}_{2} \mathrm{O}$ system.}
\begin{tabular}{llllll}
\hline \multicolumn{2}{l}{ Associating Scheme } & & AAD\% & $k_{i j}$ \\
\cline { 1 - 2 } \cline { 4 - 5 } MEA & $\mathrm{H}_{2} \mathrm{O}$ & & $\mathrm{x}_{\text {MEA }}$ & $\mathrm{y}_{\text {MEA }}$ & \\
\hline 2 B & 3 B & & 5.28 & 3.01 & 0 \\
\hline
\end{tabular}
\end{table}
equations of state, Mac Dowell et al. [15] used the statistical associating fluid theory for potentials of variable attractive range (SAFTVR EOS) for description of the fluid phase behavior of $\mathrm{MEA}+\mathrm{H}_{2} \mathrm{O}+\mathrm{CO}_{2}$ mixtures. Nasrifar and Tafazol [16] calculated the VLE properties of MEA, diethanolamine (DEA) and MDEA solutions by perturbed-chain statistical associating fluid theory (PC-SAFT EOS). Pahlavanzadeh and Fakouri Baygi [17] for DEA and Fakouri Baygi and Pahlavanzadeh [18] for MEA solutions utilized the PCSAFT EOS. Zoghi et al. [19] modelled $\mathrm{CO}_{2}$ solubility in aqueous MDEA solutions using a modified Peng-Robinson EOS including association term. Najafloo et al. [20] applied the electrolyte-SAFTHR EOS [21] to model the solubility of $\mathrm{CO}_{2}$ in aqueous mixtures of 2-((2-aminoethyl)amino)ethanol (AEEA) and MDEA.

The SAFT-HR EOS doesn't have complexities of other versions of SAFT namely the PC-SAFT, SAFT-VR, electrolyte-SAFT-HR and etc. From literature review, it is observed that the SAFT-HR EOS previously was not applied for estimation of VLE properties of MEA $+\mathrm{H}_{2} \mathrm{O}+\mathrm{CO}_{2}$ system. Therefore in this study, the SAFT-HR EOS [22,23] is implemented in modeling of $\mathrm{CO}_{2}$ absorption by MEA. Subsequently, a comparison between capabilities of the SAFT-HR EOS and PC-SAFT EOS in prediction of $\mathrm{CO}_{2}$ solubility in MEA solution is done.

\section*{2. SAFT-HR EOS}

Free Helmholtz energy of SAFT-HR EOS was introduced by Huang and Radosz [22].

$$
\begin{equation*}
a^{r e s}=a^{h s}+a^{d i s p}+a^{c h a i n}+a^{a s s o c} \tag{1}
\end{equation*}
$$


Where $a^{\text {res }}, a^{h s}$ and $a^{\text {disp }}$ represent residual Helmholtz energy, contributions of hard sphere and dispersion interactions to the Helmholtz energy, respectively. $a^{\text {chain }}$ and $a^{\text {assoc }}$ are contributions of covalent chain-forming bonds and hydrogen bonding interactions among segments in the free Helmholtz energy. The hard sphere, dispersion, chain and association terms, and corresponding

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3
Coefficients of equilibrium constants of Equation (8).}
\begin{tabular}{lllllll}
\hline$K_{i}$ & $A$ & $B$ & $C$ & $D$ & Trange $(K)$ & Ref \\
\hline$K_{1}$ & 132.899 & -13445.9 & -22.4773 & 0 & $273-498$ & {$[28]$} \\
$K_{2}$ & 2.1211 & -8189.38 & 0 & -0.007484 & $273-323$ & {$[18]$} \\
$K_{3}$ & 2.151 & -1545.3 & 0 & 0 & $273-323$ & {$[29]$} \\
$K_{4}$ & 231.456 & -12092.1 & -36.7816 & 0 & $273-498$ & {$[28]$} \\
$K_{5}$ & 216.049 & -12431.7 & -35.4819 & 0 & $273-498$ & {$[28]$} \\
\hline
\end{tabular}
\end{table}
correlations and parameters were presented in Huang and Radosz [22].

\section*{3. Results and discussions}

\subsection*{3.1. Pure component parameters}

The adjustable parameters of the SAFT-HR EOS for pure associating compounds are the chain length number ( $m$ ), temperatureindependent segment volume ( $v_{i}^{00}$ ), temperature-independent dispersion energy of interaction between segments ( $\varepsilon^{0}$ ), volume of association ( $\kappa^{A_{i} B_{j}}$ ) and energy of association ( $\varepsilon^{A_{i} B_{j}}$,). For nonassociating compounds, only the first three parameters are needed. In this study, the SAFT-HR EOS parameters for pure $\mathrm{H}_{2} \mathrm{O}$ and $\mathrm{CO}_{2}$ are taken from Huang and Radosz [22]. The parameters of SAFT-HR EOS for pure MEA are determined by simultaneous optimization of the saturated vapor pressure and the liquid density via the following objective function:

$$
\begin{equation*}
O F=\frac{\left|P^{\text {sat }, \exp }-P^{\text {sat }, \text { cal }}\right|}{P^{\text {sat }, \exp }}+\frac{\left|\rho^{\text {sat }, \exp }-\rho^{\text {sat }, \text { cal }}\right|}{\rho^{\text {sat }, \exp }} \tag{2}
\end{equation*}
$$


Where $P^{\text {sat }}$ and $\rho^{\text {sat }}$ are the saturated vapor pressure and the saturated liquid density of pure MEA that taken from DIPPR correlations that Avlund et al. [24] applied for calculating MEA parameters set for CPA EOS. In adjusting work of pure MEA parameters for the SAFT-HR EOS, different schemes 2B, 3B and 4C for association term are considered. Pure parameters of SAFT-HR EOS and their relating absolute average deviation errors (AAD\%) are given in Table 1. The parameters of MEA are determined in this research. Based on Table 1, the association scheme 2B represents the better estimation of the saturated vapor pressure and the saturated liquid density. Consequently, the association scheme 2B is chosen for further calculation of binary and ternary systems.

\subsection*{3.2. Binary interaction parameters}

Binary interaction parameters ( $k_{i j}$ ) are adjusted for binary systems to obtain accurate VLE calculations. In this study, there are three binary interaction parameters for $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}, \mathrm{CO}_{2}-\mathrm{MEA}$ and $\mathrm{H}_{2} \mathrm{O}$-MEA. The binary interaction parameter for $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ are obtained from Najafloo et al. [25]. There aren't any experimental data for the solubility of the $\mathrm{CO}_{2}$ in the pure MEA. So three choices can be used to get the binary interaction parameter of $\mathrm{CO}_{2}$-MEA. In the first approach, the parameter can be assumed zero. In the second method, the binary interaction parameter for $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ can be calculated by optimization of the solubility experimental data of $\mathrm{CO}_{2}$ in the $\mathrm{CO}_{2}-\mathrm{MEA}-\mathrm{H}_{2} \mathrm{O}$ system. Finally, $\mathrm{N}_{2} \mathrm{O}$ analogy can be applied. Using this method, the experimental data of physical solubilities of $\mathrm{N}_{2} \mathrm{O}$ in aqueous MEA are changed to the physical solubility data of $\mathrm{CO}_{2}$ in aqueous MEA as a nonreactive ternary system. In this study, for simplicity and to expression the predictability of the EOS, the first method is adopted. For calculating binary interaction parameter of $\mathrm{H}_{2} \mathrm{O}$ -

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4
The characteristics of the experimental data sources used for the ternary $\mathrm{CO}_{2}-\mathrm{MEA}-\mathrm{H}_{2} \mathrm{O}$ system.}
\begin{tabular}{|l|l|l|l|l|}
\hline Source & $T / \mathrm{K}$ & $P_{\mathrm{CO}_{2}} / \mathrm{kPa}$ & MEA mole fraction & $\alpha_{\mathrm{CO}_{2}}$ \\
\hline Jones et al. [32] & 313-413 & 0.073-918 & 0.05 & 0.076-0.728 \\
\hline Lee et al. [33] & 313-373 & 1.2-6616 & 0.05 & 0.139-1.19 \\
\hline Lawson and Garst [34] & 313-343 & 1.3-2750 & 0.05-0.11 & 0.11-0929 \\
\hline Lee et al. [2] & 298-393 & 0.1-10000 & 0.02-0.11 & 0.065-2.152 \\
\hline Isaacs et al. [35] & 353-373 & 0.009-1.75 & 0.05 & 0.0368-0.315 \\
\hline Austgen et al. [9] & 313-353 & 0.093-228 & 0.05 & 0.266-0.698 \\
\hline Shen and Li [36] & 313 & 1.57-2550 & 0.05 & 0.561-1.049 \\
\hline Dawodu and Meisen [37] & 373 & 455-3863 & 0.09 & 0.541-0.723 \\
\hline Song et al. [38] & 312 & 3.1-2359 & 0.11 & 0.49-1.061 \\
\hline Jane and Li [39] & 353 & 3.57-121.8 & 0.05 & 0.363-0.58 \\
\hline Park et al. [40] & 313 & 3.5-2092 & 0.05 & 0.512-1.046 \\
\hline Mathonat et al. [41] & 313-393 & 2000-10000 & 0.11 & 0.55-1.07 \\
\hline Park et al. [42] & 313 & 2.6-2189 & 0.03-0.05 & 0.478-1.068 \\
\hline Tong et al. [29] & 313-393 & 3.95-408.17 & 0.11 & 0.211-0.748 \\
\hline Hilliard [43] & 313-333 & 0.005-50.2 & 0.06-0.16 & 0.114-0.591 \\
\hline Jou et al. [11] & 273-423 & 0.0012-19954 & 0.11 & 0.002-1.324 \\
\hline Ma'mun et al. [44] & 393 & 7.354-191.9 & 0.11 & 0.155-0.4182 \\
\hline Xu and Rochelle [45] & 373-443 & 12-1626 & 0.11 & 0.303-0.52 \\
\hline
\end{tabular}
\end{table}

MEA, this system should be modelled by the SAFT-HR EOS. In order to model this system both Bubble-T and Dew-T calculations should be applied. Experimental data is taken from Cai et al. [26,27]. In modeling work, the binary interaction parameter for $\mathrm{H}_{2} \mathrm{O}$-MEA was initially set to zero and the corresponding calculations were performed. The results are shown in Table 2. Based on the AAD\% observed in Table 2, the results of SAFT-HR EOS show good agreement with experimental data. So for further calculation of $\mathrm{CO}_{2}-\mathrm{MEA}-\mathrm{H}_{2} \mathrm{O}$ system, the binary interaction parameter for $\mathrm{H}_{2} \mathrm{O}$-MEA is set to zero.

\subsection*{3.3. Modeling the $\mathrm{CO}_{2}-\mathrm{MEA}-\mathrm{H}_{2} \mathrm{O}$ system}

The acid gas solubility in aqueous amines solutions is determined by both its physical solubility and the chemical equilibrium for the aqueous phase reactions among acid gas, water and amines. Aqueous phase chemical reactions involved in the MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ system can be expressed as:

$$
\begin{equation*}
2 \mathrm{H}_{2} \mathrm{O} \stackrel{K_{1}}{\longleftrightarrow} \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{OH}^{-} \tag{3}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{MEAH}^{+}+\mathrm{H}_{2} \mathrm{O} \stackrel{K_{2}}{\longleftrightarrow} \mathrm{MEA}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{4}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{MEACOO}^{-}+\mathrm{H}_{2} \mathrm{O} \stackrel{K_{3}}{\longleftrightarrow} \mathrm{MEA}+\mathrm{HCO}_{3}^{-} \tag{5}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{CO}_{2}+2 \mathrm{H}_{2} \mathrm{O} \stackrel{K_{4}}{\longleftrightarrow} \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{HCO}_{3}^{-} \tag{6}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{HCO}_{3}^{-}+\mathrm{H}_{2} \mathrm{O} \stackrel{K_{5}}{\longleftrightarrow} \mathrm{H}_{3} \mathrm{O}^{+}+\mathrm{CO}_{3}^{-2} \tag{7}
\end{equation*}
$$


The mass and charge balance equations for the reacting species were expressed by Fakouri Baygi and Pahlavanzadeh [18].

Temperature dependence of above equilibrium contents can be expressed as:

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5
AAD\% of ternary MEA- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ system by SAFT-HR, PC-SAFT EOS and e-NRTL.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Author} & \multicolumn{2}{|l|}{This Work (SAFT-HR)} & \multicolumn{2}{|l|}{\begin{tabular}{l}
Baygi and Pahlavanzadeh [18] \\
(PC-SAFT)
\end{tabular}} & \multicolumn{2}{|l|}{Zhang et al. [15] (e-NRTL)} \\
\hline & np & AAD\% & np & AAD\% & np & AAD\% \\
\hline Jones et al. [32] & 50 & 19.71 & 50 & 26.17 & 48 & 32.2 \\
\hline Lee et al. [33] & 45 & 30.99 & 45 & 36.51 & 45 & 44.4 \\
\hline Lawson and Garst [34] & 21 & 35.91 & 21 & 34.30 & 24 & 30.7 \\
\hline Lee et al. [2] & 253 & 31.50 & 253 & 34.76 & 256 & 50.5 \\
\hline Isaacs et al. [35] & 16 & 27.45 & 16 & 22.66 & 19 & 112 \\
\hline Austgen et al. [9] & 8 & 12.35 & 8 & 11.97 & 8 & 42.6 \\
\hline Shen and Li [36] & 13 & 18.06 & 13 & 30.92 & 13 & 35.5 \\
\hline Dawodu and Meisen [37] & 5 & 26.80 & 5 & 17.05 & 5 & 43.2 \\
\hline Song et al. [38] & 10 & 112.75 & 10 & 66.87 & 10 & 74.4 \\
\hline Jane and Li [39] & 7 & 27.33 & 7 & 30.91 & 7 & 37.7 \\
\hline Park et al. [40] & 7 & 10.80 & 7 & 21.25 & 7 & 28.6 \\
\hline Mathonat et al. [41] & 9 & 28.77 & 9 & 35.62 & 9 & 36.0 \\
\hline Park et al. [42] & 13 & 37.59 & 13 & 50.65 & 13 & 49.8 \\
\hline Tong et al. [29] & 21 & 72.67 & 21 & 53.53 & - & - \\
\hline Hilliard [43] & 42 & 42.59 & 42 & 34.97 & 55 & 35.5 \\
\hline Jou et al. [11] & 100 & 49.52 & 100 & 43.16 & 124 & 33.5 \\
\hline Ma'mun et al. [44] & 19 & 39.96 & 19 & 21.03 & 19 & 13.5 \\
\hline Xu and Rochelle [45] & 52 & 15.44 & 52 & 46.88 & 63 & 28.0 \\
\hline Overall & 691 & 34.71 & 691 & 36.42 & 725 & 42.29 \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/872fb91b-a0c4-4ad1-9f0c-44ffd251cf21-4.jpg?height=761&width=1105&top_left_y=223&top_left_x=465}
\captionsetup{labelformat=empty}
\caption{Fig. 1. A comparison between experimental data of Jones et al. [32], SAFT-HR and PC-SAFT EOSs for $\mathrm{CO}_{2}$ partial pressure in ternary system of MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$.}
\end{figure}

$$
\begin{equation*}
K_{i}=\exp \left(A+\frac{B}{T}+C \ln (T)+D T\right) \tag{8}
\end{equation*}
$$


The coefficients of equilibrium constant correlation given by other authors [18,28,29] are listed in Table 3.

The equilibrium relation between vapor and liquid phases for water, MEA and carbon dioxide can be expressed as:

$$
\begin{equation*}
x_{i} \phi_{i}^{l}=y_{i} \phi_{i}^{v} \tag{9}
\end{equation*}
$$

where $x_{i}, y_{i}$ and $\varphi_{i}$ are the liquid phase mole fraction, vapor phase mole fraction and the fugacity coefficient of species $i$. Superscripts $l$ and $v$ refer to liquid and vapor phases, respectively. The fugacity coefficients can be calculated using different equations of state. Here, the SAFT-HR EOS is chosen for the fugacity coefficient calculation.

Equation (8), the thermodynamic equilibrium constant expressions and the mass and charge balance equations are solved by Smith-Missen algorithm [30]. For finding the concentration of species in chemical equilibrium, it is assumed all species activity equal to their mole fraction. This assumption ( $a_{i}=x_{i}$ ) has been used by other authors [17,18,31].

Table 4 displays the characteristics of the experimental data sources used for the ternary $\mathrm{CO}_{2}$ - MEA- $\mathrm{H}_{2} \mathrm{O}$ system. Table 5 shows results of the ternary systems by the method which it is outlined in chemical and phase equilibrium section. The results of PC-SAFT EOS as used by Fakouri Baygi and Pahlavanzadeh [18] and e-NRTL model as implemented by Zhang et al. [14] for each experimental data set are given in Table 5. The average absolute partial pressure deviations for SAFT-HR, PC-SAFT and e-NRTL are calculated around $34.71 \%, 36.42 \%$ and $42.29 \%$, respectively. Based on mentioned results, the SAFT-HR EOS has lower overall absolute average

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/872fb91b-a0c4-4ad1-9f0c-44ffd251cf21-4.jpg?height=765&width=1110&top_left_y=1765&top_left_x=460}
\captionsetup{labelformat=empty}
\caption{Fig. 2. Experimental data of Tong et al. [29], Jou et al. [11] and Ma'mun et al. [44] in comparison to the SAFT-HR and PC-SAFT EOSs.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/872fb91b-a0c4-4ad1-9f0c-44ffd251cf21-5.jpg?height=754&width=1101&top_left_y=226&top_left_x=499}
\captionsetup{labelformat=empty}
\caption{Fig. 3. A comparison between the experimental data of Lee et al. [2], SAFT-HR and PC-SAFT EOSs in temperature ranges $313.15-393.15 \mathrm{~K}$ and $\mathrm{m}_{\mathrm{MEA}}=3.75$.}
\end{figure}
percentage error in comparison to the PC-SAFT EOS and e-NRTL model. It is concluded that operability of the SAFT-HR EOS in some experimental data set predominate the PC-SAFT EOS and e-NRTL. It is valuable it to point out the SAFT-HR EOS predictions are acceptable within the AAD\% in CO2 partial pressure for many experimental data are exposed in Table 5. A large number of complicated adjustable binary interaction parameters have been discussed as a main disadvantage of the excess Gibbs energy model. In addition, extra terms in other versions of SAFT-HR except PCSAFT mean larger number of adjustable parameters. For more comparisions, we also considered that number of adjusted parameters in comparisons. Baygi and Pahlavanzadeh [18] utilized six regressed and eight published parameters for PC-SAFT EOS in order to describe MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ system. Zhang et al. [15] have fitted twelve parameters for e-NRTL. But in SAFT-HR EOS, only five regressed (this work) and eight published [22] parameters were
applied. Numbers of applied parameters for SAFT-HR EOS are lower than e-NRTL by Zhang et al. [14] and PC-SAFT EOS by Baygi and Pahlavanzadeh [19]. The SAFT-HR EOS has same number of adjustable parameters as to PC-SAFT EOS. In the SAFT-HR EOS, binary coefficient of MEA and $\mathrm{H}_{2} \mathrm{O}$ assumes zero, while in Baygi and Pahlavanzadeh [19] was fitted.

Fig. 1 shows a comparison between experimental partial pressure of $\mathrm{CO}_{2}$ of Jones et al. [32] and model predictions in temperature range $313.15-413.15 \mathrm{~K}$ and $\mathrm{CO}_{2}$ loading $0.076-0.728$. Based on Fig. 1 and Table 5, a good agreement between experimental data and model predictions is seen.

Fig. 2 compares the results of model predictions for $\mathrm{CO}_{2}$ partial pressure in temperatures 313 and $393 \mathrm{~K}, \mathrm{CO}_{2}$ loading range 0.002-1.324 and $30 \mathrm{wt} \%$ of MEA with the experimental data by Tong et al. [29], Jou et al. [11] and Ma'mun et al. [44]. A proper capability of the SAFT-HR EOS in characterization of MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/872fb91b-a0c4-4ad1-9f0c-44ffd251cf21-5.jpg?height=754&width=1099&top_left_y=1774&top_left_x=501}
\captionsetup{labelformat=empty}
\caption{Fig. 4. A comparison between the experimental data of Park et al. [42] and Shen and Li [36], SAFT-HR and PC-SAFT EOSs.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/872fb91b-a0c4-4ad1-9f0c-44ffd251cf21-6.jpg?height=767&width=1107&top_left_y=226&top_left_x=465}
\captionsetup{labelformat=empty}
\caption{Fig. 5. A comparison between the experimental data of Austgen et al. [9] and the SAFT-HR EOS.}
\end{figure}
ternary systems is represented in Fig. 2.
In Fig. 3, $\mathrm{CO}_{2}$ partial pressure of MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ system obtained by the SAFT-HR EOS is compared with experimental data of Lee et al. [2]. The experimental data are reported in temperature range $313.15-393.15 \mathrm{~K}$ and $\mathrm{CO}_{2}$ loading $0.11-0.929$ in initial concentration 3.75 molality for MEA. The prediction results and experimental data coincide in the entire temperature and loading ranges. Figs. 2 and 3 are utilized to depict the effect of MEA concentration on model prediction by the SAFT-HR EOS. It is concluded that the proposed model has proper performance in the mentioned concentration. Fig. 4 exhibits the results of proposed model in comparison to experimental data of Park et al. [40] and Shen and Li [36]. The experimental data included $\mathrm{CO}_{2}$ partial pressure at different $\mathrm{CO}_{2}$ loading $0.478-1.068$ in temperature 313.15 K and $15.3 \mathrm{wt} \%$ of MEA. Austgen et al. [9] measured $\mathrm{CO}_{2}$ partial pressure in MEA-CO2$\mathrm{H}_{2} \mathrm{O}$ system in temperatures 313.15 and 353.15 K at initial MEA
concentration $2.5 \mathrm{kmol} / \mathrm{m}^{3}$. $\mathrm{CO}_{2}$ loading in Austgen et al. [9] study varied between 0.266 and 0.698 . Fig. 5 compares the experimental data of Austgen et al. [9] and model prediction by the SAFT-HR EOS. Based on Fig. 5, a good agreement between the experimental data and the predicted results are seen.

A comparison between the experimental data of Isaacs et al. [35] for ternary MEA- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ system and the SAFT-HR EOS predictions are declared in Fig. 6. It is obvious that the SAFT-HR EOS model can precisely estimate vapor liquid equilibrium of ternary system at two temperatures 353.15 and 373.15 K . In Figs. 1-4 and 6, results of SAFT-HR EOS were compared to PC-SAFT EOS by Baygi and Pahlavanzadeh [19]. Absolute average deviations (AAD\%) in Table 5 showed that two models haven't great difference. Same conclusion was derived from figures. According to Fig. 4, the SAFT-HR EOS shows better agreement for Park et al. [42] and Shen and Li [36] experimental data in comparison to the PC-SAFT EOS.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/872fb91b-a0c4-4ad1-9f0c-44ffd251cf21-6.jpg?height=752&width=1105&top_left_y=1778&top_left_x=465}
\captionsetup{labelformat=empty}
\caption{Fig. 6. A comparison between the experimental data reported by Isaacs et al. [35], SAFT-HR and PC-SAFT EOSs.}
\end{figure}

\section*{4. Conclusions}

In this research, vapor-liquid equilibrium of ternary MEA-CO2$\mathrm{H}_{2} \mathrm{O}$ system was evaluated by applying the SAFT-HR EOS. In this regard, the pure component properties of MEA, binary vapor-liquid equilibrium data of MEA- $\mathrm{H}_{2} \mathrm{O}$ and ternary vapor-liquid equilibrium data of MEA- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ system were utilized in determination of the pure component and binary interaction parameters of the SAFT-HR EOS. Based on the capability of model prediction for the saturated liquid density and the saturated vapor pressure of MEA, the association scheme 2 B was chosen for describing the hydrogen bonding interactions of MEA. Model results were calculated using the different experimental data sets and the overall absolute deviation error $34.71 \%$ was reported. A comparison between the SAFT-HR EOS, PC-SAFT EOS and e-NRTL model was done in evaluation of vapor-liquid equilibrium of ternary MEA- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$ system. Because of lower absolute average deviation error, the SAFT-HR EOS is most accurate. In addition, the SAFT-HR EOS parameters were fitted using wide experimental ranges including $298-443 \mathrm{~K}$ for temperature, 0.005-19954 for $\mathrm{CO}_{2}$ partial pressure, 0.02-0.16 for MEA mole fraction and $0.002-2.152$ for $\mathrm{CO}_{2}$ loading.

\section*{Nomenclatures and abbreviations}

\begin{tabular}{|l|l|}
\hline a & Helmholtz energy \\
\hline \multicolumn{2}{|l|}{$A, B, C, D, E$ coefficients of correlations} \\
\hline $d$ & effective segment diameter \\
\hline $k_{i j}$ & Binary interaction parameter \\
\hline K & Mole based chemical equilibrium constant \\
\hline $x$ & liquid phase mole fraction, mole fraction in SAFT-HR EOS \\
\hline $y$ & vapor phase mole fraction \\
\hline $m$ & segment number \\
\hline $P$ & pressure \\
\hline T & temperature \\
\hline $\varepsilon$ & energy parameter \\
\hline $\rho$ & density \\
\hline $\sigma$ & temperature-independent segment diameter \\
\hline $\varphi$ & fugacity coefficients \\
\hline assoc & association \\
\hline disp & dispersion \\
\hline hs & hard sphere \\
\hline res & residual \\
\hline
\end{tabular}

\section*{References}
[1] Y.G. Li, A.E. Mather, Correlation and prediction of the solubility of carbon dioxide in a mixed alkanolamine solution, Industrial Eng. Chem. Res. 33 (1994) 2006-2015.
[2] J.I. Lee, F.D. Otto, A.E. Mather, Equilibrium between carbon dioxide and aqueous monoethanolamine solutions, J. Appl. Chem. Biotechnol. 26 (1976) 541-549.
[3] F.Y. Jou, A.E. Mather, F.D. Otto, Solubility of hydrogen sulfide and carbon dioxide in aqueous methyldiethanolamine solutions, Industrial Eng. Chem. Process Des. Dev. 21 (1982) 539-544.
[4] A. Chakma, A. Meisen, Improved Kent-Eisenberg model for predicting CO2 solubilities in aqueous diethanolamine (DEA) solutions, Gas Sep. Purif. 4 (1990) 37-40.
[5] R.L. Kent, B. Eisenberg, Better data for amine treating, Hydrocarb. process 55 (1976) 87-90.
[6] L. Chunxi, W. Fürst, Representation of $\mathrm{CO2}$ and $\mathrm{H2S}$ solubility in aqueous MDEA solutions using an electrolyte equation of state, Chem. Eng. Sci. 55 (2000) 2975-2988.
[7] R.D. Deshmukh, A.E. Mather, A mathematical model for equilibrium solubility of hydrogen sulfide and carbon dioxide in aqueous alkanolamine solutions, Chem. Eng. Sci. 36 (1981) 355-362.
[8] D.M. Austgen, G.T. Rochelle, X. Peng, C.C. Chen, Model of vapor-liquid equilibria for aqueous acid gas-alkanolamine systems using the electrolyte-NRTL equation, Industrial Eng. Chem. Res. 28 (1989) 1060-1073.
[9] D.M. Austgen, G.T. Rochelle, C.C. Chen, Model of vapor-liquid equilibria for aqueous acid gas-alkanolamine systems. 2. Representation of hydrogen sulfide and carbon dioxide solubility in aqueous MDEA and carbon dioxide
solubility in aqueous mixtures of MDEA with MEA or DEA, Industrial Eng. Chem. Res. 30 (1991) 543-555.
[10] R.H. Weiland, T. Chakravarty, A.E. Mather, Solubility of carbon dioxide and hydrogen sulfide in aqueous alkanolamines, Industrial Eng. Chem. Res. 32 (1993) 1419-1430.
[11] F.-Y. Jou, A.E. Mather, F.D. Otto, The solubility of CO2 in a 30 mass percent monoethanolamine solution, Can. J. Chem. Eng. 73 (1995) 140-147.
[12] Á.P.-S. Kamps, A. Balaban, M. Jödecke, G. Kuranov, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of N-methyldiethanolamine at temperatures from 313 to 393 K and pressures up to 7.6 MPa : new experimental data and model extension, Industrial Eng. Chem. Res. 40 (2001) 696-706.
[13] L. Faramarzi, G.M. Kontogeorgis, K. Thomsen, E.H. Stenby, Extended UNIQUAC model for thermodynamic modeling of $\mathrm{CO2}$ absorption in aqueous alkanolamine solutions, Fluid Phase Equilibria 282 (2009) 121-132.
[14] Y. Zhang, H. Que, C.-C. Chen, Thermodynamic modeling for CO2 absorption in aqueous MEA solution with electrolyte NRTL model, Fluid Phase Equilibria 311 (2011) 67-75.
[15] N. Mac Dowell, F. Llovell, C.S. Adjiman, G. Jackson, A. Galindo, Modeling the fluid phase behavior of carbon dioxide in aqueous solutions of monoethanolamine using transferable parameters with the SAFT-VR approach, Industrial Eng. Chem. Res. 49 (2010) 1883-1899.
[16] K. Nasrifar, A.H. Tafazzol, Vapor-Liquid equilibria of acid Gas-Aqueous ethanolamine solutions using the PC-SAFT equation of state, Industrial Eng. Chem. Res. 49 (2010) 7620-7630.
[17] H. Pahlavanzadeh, S. Fakouri Baygi, Modeling CO2 solubility in aqueous methyldiethanolamine solutions by perturbed chain-SAFT equation of state, J. Chem. Thermodyn. 59 (2013) 214-221.
[18] S. Fakouri Baygi, H. Pahlavanzadeh, Application of the perturbed chain-SAFT equation of state for modeling CO2 solubility in aqueous monoethanolamine solutions, Chem. Eng. Res. Des. 93 (2015) 789-799.
[19] A.T. Zoghi, F. Feyzi, M.R. Dehghani, Modeling CO2 solubility in aqueous Nmethyldiethanolamine solution by electrolyte modified Peng-Robinson Plus association equation of state, Industrial Eng. Chem. Res. 51 (2012) 9875-9885.
[20] A. Najafloo, A.T. Zoghi, F. Feyzi, Measuring solubility of carbon dioxide in aqueous blends of N -methyldiethanolamine and 2-((2-aminoethyl)amino) ethanol at low CO2 loadings and modelling by electrolyte SAFT-HR EoS, J. Chem. Thermodyn. 82 (2015) 143-155.
[21] A. Najafloo, F. Feyzi, A. Zoghi, Development of electrolyte SAFT-HR equation of state for single electrolyte solutions, Korean J. Chem. Eng. 31 (2014) 2251-2260.
[22] S.H. Huang, M. Radosz, Equation of state for small, large, polydisperse, and associating molecules, Industrial Eng. Chem. Res. 29 (1990) 2284-2294.
[23] S.H. Huang, M. Radosz, Equation of state for small, large, polydisperse, and associating molecules: extension to fluid mixtures, Industrial Eng. Chem. Res. 30 (1991) 1994-2005.
[24] A.S. Avlund, G.M. Kontogeorgis, M.L. Michelsen, Modeling systems containing alkanolamines with the CPA equation of state, Industrial Eng. Chem. Res. 47 (2008) 7441-7446.
[25] A. Najafloo, F. Feyzi, A.T. Zoghi, Modeling solubility of CO2 in aqueous MDEA solution using electrolyte SAFT-HR EoS, J. Taiwan Inst. Chem. Eng. 58 (2016) 381-390.
[26] Z. Cai, R. Xie, Z. Wu, Binary isobaric Vapor-Liquid equilibria of ethanolamines + water, J. Chem. Eng. Data 41 (1996) 1101-1103.
[27] S.-B. Park, H. Lee, Vapor-liquid equilibria for the binary monoethanolamine+ water and monoethanolamine+ethanol systems, Korean J. Chem. Eng. 14 (1997) 146-148.
[28] T.J. Edwards, G. Maurer, J. Newman, J.M. Prausnitz, Vapor-liquid equilibria in multicomponent aqueous solutions of volatile weak electrolytes, AIChE J. 24 (1978) 966-976.
[29] D. Tong, J.P.M. Trusler, G.C. Maitland, J. Gibbins, P.S. Fennell, Solubility of carbon dioxide in aqueous solution of monoethanolamine or 2-amino-2-methyl-1-propanol: experimental measurements and modelling, Int. J. Greenh. Gas Control 6 (2012) 37-47.
[30] W.R. Smith, R.W. Missen, Strategies for solving the chemical equilibrium problem and an efficient microcomputer-based algorithm, Can. J. Chem. Eng. 66 (1988) 591-598.
[31] K. Nasrifar, A.H. Tafazzol, Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions using the PC-SAFT equation of state, Industrial Eng. Chem. Res. 49 (2010) 7620-7630.
[32] J.H. Jones, H.R. Froning, E.E. Claytor, Solubility of acidic gases in aqueous monoethanolamine, J. Chem. Eng. Data 4 (1959) 85-92.
[33] J.I. Lee, F.D. Otto, A.E. Mather, The solubility of H 2 S and CO 2 in aqueous monoethanolamine solutions, Can. J. Chem. Eng. 52 (1974) 803-805.
[34] J.D. Lawson, A.W. Garst, Gas sweetening data: equilibrium solubility of hydrogen sulfide and carbon dioxide in aqueous monoethanolamine and aqueous diethanolamine solutions, J. Chem. Eng. Data 21 (1976) 20-30.
[35] E.E. Isaacs, F.D. Otto, A.E. Mather, Solubility of mixtures of hydrogen sulfide and carbon dioxide in a monoethanolamine solution at low partial pressures, J. Chem. Eng. Data 25 (1980) 118-120.
[36] K.P. Shen, M.H. Li, Solubility of carbon dioxide in aqueous mixtures of monoethanolamine with methyldiethanolamine, J. Chem. Eng. Data 37 (1992) 96-100.
[37] O.F. Dawodu, A. Meisen, Solubility of carbon dioxide in aqueous mixtures of
alkanolamines, J. Chem. Eng. Data 39 (1994) 548-552.
[38] J.-H. Song, J.-H. Yoon, H. Lee, K.-H. Lee, Solubility of carbon dioxide in monoethanolamine + ethylene glycol + water and monoethanolamine + poly(ethylene glycol) + water, J. Chem. Eng. Data 41 (1996) 497-499.
[39] I.S. Jane, M.-H. Li, Solubilities of mixtures of carbon dioxide and hydrogen sulfide in water + diethanolamine + 2-Amino-2-methyl-1-propanol, J. Chem. Eng. Data 42 (1997) 98-105.
[40] S.-B. Park, C.-S. Shim, H. Lee, K.-H. Lee, Solubilities of carbon dioxide in the aqueous potassium carbonate and potassium carbonate-poly(ethylene glycol) solutions, Fluid Phase Equilibria 134 (1997) 141-149.
[41] C. Mathonat, V. Majer, A.E. Mather, J.P.E. Grolier, Use of flow calorimetry for determining enthalpies of absorption and the solubility of CO2 in aqueous monoethanolamine solutions, Industrial Eng. Chem. Res. 37 (1998)

4136-4141.
[42] J.-Y. Park, S.J. Yoon, H. Lee, J.-H. Yoon, J.-G. Shim, J.K. Lee, B.-Y. Min, H.-M. Eum, M.C. Kang, Solubility of carbon dioxide in aqueous solutions of 2-amino-2-ethyl-1,3-propanediol, Fluid Phase Equilibria 202 (2002) 359-366.
[43] M.D. Hilliard, A Predictive Thermodynamic Model for an Aqueous Blend of Potassium Carbonate, Piperazine, and Monoethanolamine for Carbon Dioxide Capture from FlueGas, University of Texas at Austin, 2008.
[44] S. Ma'mun, R. Nilsen, H.F. Svendsen, O. Juliussen, Solubility of carbon dioxide in 30 mass $\%$ monoethanolamine and 50 mass $\%$ methyldiethanolamine solutions, J. Chem. Eng. Data 50 (2005) 630-634.
[45] Q. Xu, G. Rochelle, Total pressure and CO2 solubility at high temperature in aqueous amines, Energy Procedia 4 (2011) 117-124.