\title{
Vapor-Liquid Equilibria of Acid Gas-Aqueous Ethanolamine Solutions Using the PC-SAFT Equation of State
}

\author{
Khashayar Nasrifar* and Amir H. Tafazzol \\ Department of Chemical Engineering, Shiraz University of Technology, Shiraz, Iran
}
Downloaded via BRIGHAM YOUNG UNIV on July 8, 2025 at 20:37:21 (UTC). See https://pubs.acs.org/sharingguidelines for options on how to legitimately share published articles.

\begin{abstract}
Using the perturbed-chain statistical associating fluid theory (PC-SAFT), the vapor pressure, saturated liquid density, and heat of vaporization for monoethanolamine (MEA), diethanolamine (DEA), and methyldiethanolamine (MDEA) were calculated. PC-SAFT accurately described the properties of the pure ethanolamines along the coexistence curve. Then, the vapor-liquid equilibria (VLE) of the aqueous ethanolamine solutions were calculated by temperature-independent binary interaction parameters. Using the binary interaction parameters for the systems DEA + water, DEA + methanol, and methanol + water, the VLE of the ternary system DEA + water + methanol was predicted. The results indicated that PC-SAFT successfully described the equilibrium properties of the aqueous ethanolamine solutions. Finally, the solubilities of carbon dioxide and hydrogen sulfide in the aqueous ethanolamine solutions were predicted and compared to the experimental data. While no adjustable parameters were used, PC-SAFT reasonably described the solubility data.
\end{abstract}

\section*{1. Introduction}

Aqueous ethanolamine solutions have been used for decades to remove acid gases from natural gas streams and carbon dioxide from the flue gas of industries. These solutions have regained attention in order to optimize the existing processes and to strictly control the greenhouse effect.

Pure ethanolamines such as monoethanolamine (MEA), diethanolamine (DEA), and methyldiethanolamine (MDEA) are self-associating compounds. In aqueous solutions, the ethanolamines form hydrogen bonds with water molecules as well. Additionally, when aqueous ethanolamine solutions are used to remove acid gases, new species are formed, ${ }^{1}$ e.g., carbonates, sulfides, and carbamate. Aqueous MEA and DEA solutions can form stable carbamate when these solvents are used to absorb carbon dioxide; however, MDEA solution cannot. As a result, MDEA has gained more attention in the gas industry. Formation of carbamate degrades amine solutions by forming stable complexes. Furthermore, absorption mechanisms are different for MEA and DEA as primary and secondary amines and MDEA as a tertiary amine. Due to heats of absorption, reaction rates, and heat capacity, secondary and tertiary amines find application in the gas industry. However, primary (and some secondary) amines are used for carbon dioxide removal from flue gases. MDEA also shows selective removal of hydrogen sulfide in mixtures containing hydrogen sulfide and carbon dioxide. In fact, the rate of reaction for hydrogen sulfide with MDEA is much faster than that of carbon dioxide. Hence, the importance of describing acid gas-ethanolamine solutions is warrant.

In gas processing, some appreciable amount of light hydrocarbons is absorbed by ethanolamine solutions. The absorbed gases are subsequently vented to the atmosphere. ${ }^{2,3}$ The vented gases are a further source of concern both economically and environmentally.

From a design point of view, the vapor-liquid equilibria (VLE) of aqueous ethanolamine solutions are important. Equally important are the vapor pressures, saturated liquid densities, and thermal and transport properties of pure ethanolamines. There-

\footnotetext{
* To whom correspondence should be addressed. Tel.: +98-917-709-8918. Fax: +98-711-735-4520. E-mail: nasrifar@sutech.ac.ir.
}
fore, developing a thermodynamic model to satisfactorily describe these properties is vital in process design. Such a model should be predictive to a large extent because the measurements of these properties for wide ranges of temperature and pressure are too expensive.

Equations of state are powerful tools for calculating equilibria, volumetric properties, and thermal properties of pure compounds and multicomponent mixtures. Many attempts have been made to empirically correlate the equilibrium properties of ethanolamine solutions in contact with acid gases. ${ }^{4-6}$ However, these methods are hardly predictive. Button and Gubbins ${ }^{7}$ used the statistical associating fluid theory (SAFT) of Huang and Radosz ${ }^{8,9}$ to effectively describe the solubility of carbon dioxide in aqueous ethanolamine solutions. However, Button and Gubbins ${ }^{7}$ avoided considering the possibility of forming electrolytes ${ }^{10}$ by absorbing carbon dioxide in aqueous MEA and DEA solutions. Although the method of Button and Gubbins ${ }^{7}$ seems to be an oversimplification, it emphasizes that the SAFT approach is predictive and might be improved by applying additional perturbation terms.

SAFT modeling of complex mixtures was reviewed by Müller and Gubbins ${ }^{11}$ and Economou. ${ }^{12}$ Von Solms et al. ${ }^{13}$ pointed out the capabilities and limitations of a simplified perturbedchain SAFT approach, especially in dealing with aqueous solutions. They suggested that modeling aqueous solutions is a challenging problem due to the difficulty of modeling the water molecule and its interaction with other molecules.

Recently, Avlund et al. ${ }^{14}$ evaluated the equilibria of binary aqueous solutions containing ethanolamine components. Using the cubic plus association (CPA) ${ }^{15}$ equation of state, Avlund et al. ${ }^{14}$ showed that CPA is a reliable correlative tool; however, the predictability of the CPA equation of state was not demonstrated. CPA has the advantage of simplicity, especially for engineering purposes. However, because of weak repulsive and dispersion terms, its predictability must be strictly evaluated before a specific application.

The study of Button and Gubbins ${ }^{7}$ using the SAFT approach of Huang and Radosz ${ }^{8,9}$ looks promising. However, the perturbedchain SAFT approach (PC-SAFT) of Gross and Sadowski ${ }^{16}$ accounts more rigorously for the dispersion term and this may improve the predictability of the approach. Therefore, we use
the PC-SAFT approach in this work. In practice, existing models have been used successfully to calculate the solubility of acid gases in aqueous ethanolamine solutions. For instance, activity coefficient models like NRTL can be employed with balance equations and chemical equilibrium relations to calculate sour gas solubility in aqueous ethanolamine solutions. PC-SAFT may never replace them. However, because of its predictive accuracy in describing associating liquids, PC-SAFT can be used as a screening device for new solvents when few experimental data are available. Further, SAFT can be used to calculate the thermodynamic properties of ethanolamine solutions. These properties are vital in designing amine treating plants.

In the following sections, first, we briefly explain the chemistry of acid gas-aqueous ethanolamine solutions, prevalent equations, and the PC-SAFT equation of state. Then we determine the missing parameters of pure MEA, DEA, and MDEA using PC-SAFT. Afterward, the VLE of aqueous systems containing the ethanolamine components are evaluated. Further, the predictability of the PC-SAFT approach is evaluated for the ternary system DEA + water + methanol. Studying this mixture is important as methanol is added to aqueous ethanolamine solutions to enhance mercaptan absorption from gas streams. Finally, the solubility of acid gases in the aqueous ethanolamine solutions is predicted while no adjustable parameter is used.

\section*{2. Chemistry of Acid Gas-Aqueous Ethanolamine Solutions}

In aqueous solutions, carbon dioxide and hydrogen sulfide react with the ethanolamine through an acid-base buffer mechanism. The following parallel reversible reactions take place.

Dissociation of water:

$$
\begin{equation*}
2 \mathrm{H}_{2} \mathrm{O} \stackrel{k \neq}{\mathrm{OH}^{-}}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{1}
\end{equation*}
$$


Formation of bicarbonate:

$$
\begin{equation*}
\mathrm{CO}_{2}+2 \mathrm{H}_{2} \mathrm{O} \stackrel{k \pm}{\Leftrightarrow} \mathrm{HCO}_{3}^{-}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{2}
\end{equation*}
$$


Formation of carbonate:

$$
\begin{equation*}
\mathrm{HCO}_{3}^{-}+\mathrm{H}_{2} \mathrm{O} \stackrel{k \underset{3}{\xi}}{\Leftrightarrow} \mathrm{CO}_{3}{ }^{2-}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{3}
\end{equation*}
$$


Formation of bisulfide:

$$
\begin{equation*}
\mathrm{H}_{2} \mathrm{~S}+\mathrm{H}_{2} \mathrm{O} \stackrel{k!}{\Leftrightarrow} \mathrm{HS}^{-}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{4}
\end{equation*}
$$


Formation of sulfide:

$$
\begin{equation*}
\mathrm{HS}^{-}+\mathrm{H}_{2} \mathrm{O} \stackrel{k \breve{s}}{\Leftrightarrow} \mathrm{~S}^{2-}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{5}
\end{equation*}
$$


Dissociation of protonated amines:

$$
\begin{equation*}
\mathrm{MDEAH}^{+}+\mathrm{H}_{2} \mathrm{O} \Leftrightarrow \mathrm{MDEA}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{6}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{MEAH}^{+}+\mathrm{H}_{2} \mathrm{O} \Leftrightarrow \mathrm{MEA}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{7}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{DEAH}^{+}+\mathrm{H}_{2} \mathrm{O} \Leftrightarrow \mathrm{DEA}+\mathrm{H}_{3} \mathrm{O}^{+} \tag{8}
\end{equation*}
$$


In addition to these reactions, MEA and DEA react with bicarbonate to form carbamate. Formation of carbamate is less reversible and may lead to stable product.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1. Temperature-Dependent Equilibrium Constants (Based on Mole Fraction) ${ }^{\boldsymbol{a}}$ for Reactions $\mathbf{1}-\mathbf{1 0}^{\mathbf{5 1}}$}
\begin{tabular}{|l|l|l|l|l|l|}
\hline $k_{i}^{x}$ & A & $B$ & C & D & $T$ range (K) \\
\hline $k_{1}^{x}$ & 132.899 & -13445.9 & -22.4773 & 0 & 273-498 \\
\hline $k_{2}^{x}$ & 231.456 & -12092.1 & -36.7816 & 0 & 273-498 \\
\hline $k_{3}^{x}$ & 216.049 & -12431.7 & -35.4819 & 0 & 273-498 \\
\hline $k_{4}^{x}$ & 214.582 & -12995.4 & -33.5471 & 0 & 273-423 \\
\hline $k_{5}^{x}$ & -32.0 & -3338.0 & 0 & 0 & 287-343 \\
\hline $k_{6}^{x}$ & -9.4165 & -4234.98 & 0 & 0 & 298-333 \\
\hline $k_{7}^{x}$ & 2.1211 & -8189.38 & 0 & -0.007484 & 273-323 \\
\hline $k_{8}^{x}$ & -13.3373 & -4218.71 & 0 & 0.009872 & 273-323 \\
\hline $k_{9}^{x}$ & 2.8898 & -3635.09 & 0 & 0 & 298-393 \\
\hline $k_{10}^{x}$ & 16.5027 & -4068.76 & -1.5027 & 0 & 298-393 \\
\hline
\end{tabular}
\end{table}
${ }^{a} \ln \left(k_{i}^{x}\right)=A+B / T+C \ln (T)+D T$.
Dissociation of carbamate:

$$
\begin{align*}
& \mathrm{MEACOO}{ }^{-}+\mathrm{H}_{2} \mathrm{O} \stackrel{k \underset{0}{k s}}{\Leftrightarrow} \mathrm{MEA}+\mathrm{HCO}_{3}^{-}  \tag{9}\\
& \mathrm{DEACOO}^{-}+\mathrm{H}_{2} \mathrm{O} \stackrel{k \mathrm{O}_{0}}{\Leftrightarrow} \mathrm{DEA}+\mathrm{HCO}_{3}^{-} \tag{10}
\end{align*}
$$


These reactions are accounted for in this work.

\section*{3. Chemical Equilibria and Balance Equations}

The chemical equilibria taking place in the liquid phase are mathematically expressed by

$$
\begin{equation*}
k_{i}^{x}=\prod_{j}\left(x_{j} \gamma_{j}\right)^{v_{j, i}} \quad i=1,2, \ldots, 10 \tag{11}
\end{equation*}
$$

where $k_{i}^{x}$ is the mole fraction based equilibrium constant for the reaction $i$. The temperature-dependent equilibrium constants are given in Table 1. The parameter $x_{j}$ is the mole fraction of species $j$ in the liquid phase, $\gamma_{j}$ is the activity coefficient of species $j$, and $v_{j, i}$ is the stoichiometric coefficient of species $j$ in the reaction $i$. However, in order to completely determine the system of equations, balance equations are required.

Water mole balance:

$$
\begin{equation*}
N_{\mathrm{H}_{2} \mathrm{O}}^{\circ}=N_{\mathrm{H}_{2} \mathrm{O}}+N_{\mathrm{OH}^{-}}+N_{\mathrm{HCO}_{3}^{-}}+N_{\mathrm{CO}_{3}^{2-}} \tag{12}
\end{equation*}
$$


Amine mole balance:

$$
\begin{equation*}
N_{\mathrm{Am}}^{\mathrm{o}}=N_{\mathrm{Am}^{\mathrm{Am}}}+N_{\mathrm{AmH}^{+}}+N_{\mathrm{AmCOO}^{-}} \tag{13}
\end{equation*}
$$


Acid gas mole balances:

$$
\begin{gather*}
L_{\mathrm{CO}_{2}} N_{\mathrm{Am}}^{\circ}=N_{\mathrm{CO}_{2}}+N_{\mathrm{HCO}_{3}^{-}}+N_{\mathrm{CO}_{3^{2-}}}+N_{\mathrm{AmCOO}^{-}}  \tag{14}\\
L_{\mathrm{H}_{2} \mathrm{~S}^{2}} N_{\mathrm{Am}^{\circ}}=N_{\mathrm{H}_{2} \mathrm{~S}}+N_{\mathrm{HS}^{-}}+N_{\mathrm{S}^{2-}} \tag{15}
\end{gather*}
$$


Charge balance:

$$
\begin{array}{r}
N_{\mathrm{AmH}^{+}}+N_{\mathrm{H}_{3} \mathrm{O}^{+}}=N_{\mathrm{HS}^{-}}+2 N_{\mathrm{S} 2^{-}}+N_{\mathrm{HCO}_{3}^{-}}+2 N_{\mathrm{CO}_{3}^{2-}}+ \\
N_{\mathrm{OH}^{-}}+N_{\mathrm{AmCOO}^{-}} \tag{16}
\end{array}
$$


In these equations, $L$ is the loading (moles of acid gas per mole of amine), $N$ is the number of moles, and Am stands for the amine (MEA, DEA, or MDEA). If Am represents MDEA, $N_{\mathrm{AmCOO}}{ }^{-}$will vanish as MDEA does not form carbamate.

\section*{4. Phase Equilibria}

PC-SAFT is used to perform equilibrium calculations between molecular species ( $\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}$, MEA, DEA, MDEA, and water). Further, it is assumed that ionic species are solely contained in the liquid phase. Therefore, the vapor phase will contain the
acid gases, amine, and water molecules. The equilibrium relations are then expressed by

$$
\begin{equation*}
x_{i} \phi_{i}^{\mathrm{l}}=y_{i} \phi_{i}^{\mathrm{v}} \quad i=\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}, \mathrm{Am}, \text { water } \tag{17}
\end{equation*}
$$

where $x$ and $y$ are, respectively, the liquid and vapor phase mole fractions and $\phi_{i}$ is the fugacity coefficient of species $i$ as calculated by the PC-SAFT equation of state.

\section*{5. The PC-SAFT Equation of State}

In terms of molar Helmholtz free energy, PC-SAFT is expressed by

$$
\begin{equation*}
a^{\mathrm{res}}=a^{\mathrm{hc}}+a^{\mathrm{disp}}+a^{\mathrm{assoc}}+a^{\mathrm{polar}} \tag{18}
\end{equation*}
$$

where $a^{\text {res }}$ is the residual Helmholtz free energy at the same temperature and density of the fluid of interest ( $a^{\text {res }}=A^{\text {res }} / R T$ ). The polar contribution to the Helmholtz free energy is trivial as we work on the ethanolamine solutions. In principle, selfassociating compounds are polar fluids. However, Al Saifi et al. ${ }^{17}$ showed that in binary solutions of associating fluids, i.e., two alcohols, the polar contribution to the equilibrium pressure is not substantial. Karakatsani and Economou ${ }^{18}$ and Karakatsani et al. ${ }^{19}$ illustrated that, for water, the polar contribution is considerably smaller than the associating contribution. In fact, the polar contribution is just important in SAFT modeling of solutions containing polar compounds or one associating and one polar compound. ${ }^{20-23}$ Therefore, it is supposed that, in aqueous ethanolamine solutions, hydrogen bonding (association term, $a^{\text {assoc }}$ ) dominantly contributes to the Helmholtz free energy of the solution and the polar contribution is less effective. Therefore we set $a^{\text {polar }}$ to zero for simplicity. The other contributions, however, cannot be ignored.

The hard-chain contribution to the Helmholtz free energy $a^{\text {hc }}$ accounts for the excluded volume in the fluid and the covalent bonds in the chain molecules ( $a^{\text {hc }}=\bar{m} a^{\text {hs }}+a^{\text {chain }}$ ). We use the expression suggested by Boublik ${ }^{24}$ and Mansoori et al. ${ }^{25}$ for the excluded volume ( $a^{\text {hs }}$ ). The chain contribution to the Helmholtz free energy $a^{\text {chain }}$ was derived by replacing association bonds with covalent bonds. Several attempts were made to improve the accuracy of the chain contribution by including the dimer effect on the chain formation. ${ }^{26-28}$ Because these modifications were not evaluated strictly, we decided to use the conventional expression suggested by Chapman et al. ${ }^{29}$ and Wertheim. ${ }^{30}$ Therefore we get

$$
\begin{array}{r}
a^{\mathrm{hc}}= \\
\frac{\bar{m}}{\zeta_{0}}\left[\frac{3 \zeta_{1} \zeta_{2}}{1-\zeta_{3}}+\frac{\zeta_{2}^{3}}{\zeta_{3}\left(1-\zeta_{3}\right)^{2}}+\left(\frac{\zeta_{2}^{3}}{\zeta_{3}^{2}}-\zeta_{0}\right) \ln \left(1-\zeta_{3}\right)\right]+ \\
\sum_{i} x_{i}\left(1-m_{i}\right) \ln g_{i i}^{\mathrm{hs}}\left(d_{i i}\right) \tag{19}
\end{array}
$$

where $g_{i i}^{\mathrm{hs}}\left(d_{i i}\right)$ is the hard-sphere radial distribution function at contact. This term is given later. The two other parameters are defined by

$$
\begin{gather*}
\xi_{n}=\frac{\pi N_{\mathrm{Av}}}{6} \rho \sum_{i} x_{i} m_{i} d_{i i}^{n} \quad n \in\{0,1,2,3\}  \tag{20}\\
\bar{m}=\sum_{i}^{\mathrm{nc}} x_{i} m_{i} \tag{21}
\end{gather*}
$$

where $\rho$ is the molar density, $m_{i}$ is the number of segments in a molecule of component $i$, and $N_{\mathrm{Av}}$ is Avogadro's constant.

The parameter $d_{i i}$ describes soft repulsions between molecules. In terms of the segmental diameter $\sigma_{i i}$ and the depth of the square-well potential $\varepsilon_{i i}$, the parameter $d_{i i}$ is expressed by

$$
\begin{equation*}
d_{i i}=\sigma_{i i}\left[1-0.12 \exp \left(-3 \frac{\varepsilon_{i i}}{k T}\right)\right] \tag{22}
\end{equation*}
$$


The dispersion contribution to the Helmholtz free energy $a^{\text {disp }}$ accounts for van der Waals (vdW) forces. In earlier versions of the SAFT approach, the dispersion term was usually defined as a perturbation to the hard-sphere repulsive term ( $a^{\text {hs }}$ ). Gross and Sadowski ${ }^{16}$ suggested a perturbation to the hard-chain repulsive term ( $\bar{m} a^{\text {hs }}+a^{\text {chain }}$ ), however. The expression derived by Gross and Sadowski ${ }^{16}$ is slightly complicated. However, comparisons made in predicting the VLE of normal ${ }^{16}$ and associating fluids ${ }^{31}$ using PC-SAFT and the SAFT version of Huang and Radosz ${ }^{8,9}$ revealed that PC-SAFT is more accurate than the SAFT version of Huang and Radosz. ${ }^{8,9}$ In this work we use the dispersion expression defined by Gross and Sadowski: ${ }^{16}$

$$
\begin{equation*}
a^{\mathrm{disp}}=-2 \pi \rho\left[I_{1}(\eta, \bar{m})\right]\left(m^{2} \varepsilon \sigma^{3}\right)_{\mathrm{m}}-\pi \rho \bar{m} C_{1}\left[I_{2}(\eta, \bar{m})\right]\left(m^{2} \varepsilon^{2} \sigma^{3}\right)_{\mathrm{m}} \tag{23}
\end{equation*}
$$

where $C_{1}$ is the compressibility of the hard-chain fluid:

$$
\begin{equation*}
C_{1}=\left(1+Z^{\mathrm{hc}}+\rho \frac{\partial Z^{\mathrm{hc}}}{\partial \rho}\right)^{-1} \tag{24}
\end{equation*}
$$

$I_{1}(\eta, \bar{m})$ and $I_{2}(\eta, \bar{m})$ are expressed by ${ }^{16}$

$$
\begin{align*}
& I_{1}(\eta, \bar{m})=\sum_{j=0}^{6} a_{j}(\bar{m}) \eta^{j}  \tag{25}\\
& I_{2}(\eta, \bar{m})=\sum_{j=0}^{6} b_{j}(\bar{m}) \eta^{j} \tag{26}
\end{align*}
$$


In eq 23 , the mixing rules for $\left(m^{2} \varepsilon \sigma^{3}\right)_{\mathrm{m}}$ and $\left(m^{2} \varepsilon^{2} \sigma^{3}\right)_{\mathrm{m}}$ are defined by ${ }^{16}$

$$
\begin{equation*}
\left(m^{2} \varepsilon \sigma^{3}\right)_{\mathrm{m}}=\sum_{i}^{\mathrm{nc}} \sum_{j}^{\mathrm{nc}} x_{i} x_{j} m_{i} m_{j}\left(\frac{\varepsilon_{i j}}{k T}\right) \sigma_{i j}^{3} \tag{27}
\end{equation*}
$$

and

$$
\begin{equation*}
\left(m^{2} \varepsilon^{2} \sigma^{3}\right)_{\mathrm{m}}=\sum_{i}^{\mathrm{nc}} \sum_{j}^{\mathrm{nc}} x_{i} x_{j} m_{i} m_{j}\left(\frac{\varepsilon_{i j}}{k T}\right)^{2} \sigma_{i j}^{3} \tag{28}
\end{equation*}
$$

where the conventional combining rules for $\varepsilon_{i j}$ and $\sigma_{i j}$ are employed:

$$
\begin{gather*}
\sigma_{i j}=\frac{\sigma_{i}+\sigma_{j}}{2}  \tag{29}\\
\varepsilon_{i j}=\sqrt{\varepsilon_{i} \varepsilon_{j}}\left(1-k_{i j}\right) \tag{30}
\end{gather*}
$$


In eq $30, k_{i j}$ is the binary interaction parameter.
For evaluating the VLE of normal fluids, inclusion of $a^{\mathrm{hc}}$ and $a^{\text {disp }}$ in the PC-SAFT approach is sufficient. Three parameters, i.e., the number of segments ( $m$ ), the depth of the square-well potential ( $\varepsilon / k$ ), and the segment diameter ( $\sigma$ ) are required to characterize each compound. However, in ethanolamine solutions, hydrogen bonding contributes dominantly to the nonideality of the ethanolamine solutions and its contribution should be taken into account.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2. Pure Component Parameters Used in This Work}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow{2}{*}{} & \multirow[b]{2}{*}{association scheme} & \multirow[b]{2}{*}{$T$ range (K)} & \multirow[b]{2}{*}{$m$} & \multirow[b]{2}{*}{$\sigma(\AA)$} & \multirow[b]{2}{*}{$\varepsilon / k(\mathrm{~K})$} & \multirow[b]{2}{*}{$\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}} / k$ (K)} & \multirow[b]{2}{*}{$\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}}$} & \multicolumn{2}{|c|}{$\% \mathrm{AAD}^{a}$} & \multirow[b]{2}{*}{ref} \\
\hline & & & & & & & & $p^{\text {sat }}$ & $\rho^{\text {sat }}$ & \\
\hline MEA & 4C & 283-580 & 4.2941 & 2.6842 & 264.34 & 985.17 & 0.0498 & 3.36 & 0.50 & this work \\
\hline DEA & 4C & 301-640 & 5.2048 & 2.9477 & 269.00 & 1517.6 & 0.1014 & 2.36 & 0.95 & this work \\
\hline MDEA & 3B & 340-620 & 7.2069 & 2.8264 & 219.94 & 3187.2 & 0.0135 & 2.28 & 0.65 & this work \\
\hline methanol & 2B & 200-512 & 1.5255 & 3.2300 & 188.90 & 2899.5 & 0.035176 & 2.36 & $2.01{ }^{b}$ & 31 \\
\hline water & 2B & 273-647 & 1.0656 & 3.0007 & 366.51 & 2500.7 & 0.034868 & 1.88 & $6.83^{b}$ & 31 \\
\hline $\mathrm{H}_{2} \mathrm{~S}$ & & 187-362 & 1.6686 & 3.0349 & 229.00 & & & 0.39 & 0.59 & this work \\
\hline $\mathrm{CO}_{2}$ & & 216-304 & 2.0729 & 2.7852 & 169.21 & & & 2.78 & $2.73{ }^{b}$ & 16 \\
\hline methane & & 97-300 & 1.0000 & 3.7039 & 150.03 & & & 0.36 & $0.67^{b}$ & 16 \\
\hline
\end{tabular}
\end{table}
${ }^{a} \% \mathrm{AAD}=(100 / \mathrm{npts}) \sum_{j}^{\text {npts }} \mathrm{Icalcd}_{j}-\operatorname{exptl}_{j} / \operatorname{exptl}_{j} .{ }^{b}$ Percent average absolute deviation in saturated liquid volume.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-04.jpg?height=451&width=587&top_left_y=622&top_left_x=274}
\captionsetup{labelformat=empty}
\caption{Figure 1. Experimental ${ }^{34}$ and correlated saturated densities for MEA and DEA.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-04.jpg?height=454&width=596&top_left_y=1189&top_left_x=267}
\captionsetup{labelformat=empty}
\caption{Figure 2. Experimental ${ }^{34}$ and correlated vapor pressures of MDEA as a function of density.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-04.jpg?height=426&width=543&top_left_y=1756&top_left_x=297}
\captionsetup{labelformat=empty}
\caption{Figure 3. Experimental ${ }^{34}$ and predicted heats of vaporization for MEA, DEA, and MDEA.}
\end{figure}

The Helmholtz free energy due to association $a^{\text {assoc }}$ is defined by ${ }^{32,11}$

$$
\begin{equation*}
a^{\text {assoc }}=\sum_{i}^{\mathrm{nc}} x_{i}\left[\sum_{\mathrm{A}_{i}}\left(\ln X^{\mathrm{A}_{i}}-\frac{X^{\mathrm{A}_{i}}}{2}\right)+\frac{1}{2} M_{i}\right] \tag{31}
\end{equation*}
$$

where $X^{\mathrm{A}_{i}}$ is the mole fraction of molecules $i$ not bonded at site A and $M_{i}$ is the number of sites on molecule $i$. The parameter $X^{\mathrm{A}_{i}}$ is given by ${ }^{9,32}$

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-04.jpg?height=1073&width=763&top_left_y=616&top_left_x=1103}
\captionsetup{labelformat=empty}
\caption{Figure 4. Isobaric VLE ${ }^{37}$ of the system MEA + water at (a) 66.66 and (b) 101.33 kPa .}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3. Binary Interaction Parameters for the Systems Studied in This Work}
\begin{tabular}{|l|l|l|l|}
\hline system & $T$ range (K) & $k_{i j}$ & ref (exptl data) \\
\hline MEA + water & 361-443 & -0.045 & 37 \\
\hline DEA + water & 311-459 & -0.04 & 37, 38 \\
\hline MDEA + water & 350-459 & 0 & 39 \\
\hline DEA + methanol & 365.15 & 0.05 & 38 \\
\hline water + methanol & 338-373 & -0.045 & 41 \\
\hline MDEA + methane & 298-403 & $0.1591-38.948 / T$ & 40 \\
\hline
\end{tabular}
\end{table}

$$
\begin{equation*}
X^{\mathrm{A}_{i}}=\left[1+N_{\mathrm{Av}} \sum_{j} \sum_{\mathrm{B}_{j}} \rho_{j} X^{\mathrm{B}_{j}} \Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}\right]^{-1} \tag{32}
\end{equation*}
$$

where the internal sum sign runs over all sites on molecule $j$. In eq $32, \rho_{j}$ is the molar density of component $j$ :

$$
\begin{equation*}
\rho_{j}=x_{j} \rho \tag{33}
\end{equation*}
$$

where $\rho$ is the molar density of the solution. The association strength $\Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ is given by ${ }^{9}$

$$
\begin{equation*}
\Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}=g_{i j}\left(d_{i j}\right)^{\mathrm{hs}}\left[\exp \left(\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}} / k T\right)-1\right]\left(\sigma_{i j}{ }^{3} k^{\mathrm{A}_{i} \mathrm{~B}_{j}}\right) \tag{34}
\end{equation*}
$$


\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-05.jpg?height=1031&width=728&top_left_y=138&top_left_x=203}
\captionsetup{labelformat=empty}
\caption{Figure 5. Isobaric and isothermal $\mathrm{VLE}^{37,38}$ of the system DEA + water at (a) 6.66 kPa and (b) 365.15 K .}
\end{figure}
where $g_{i j}\left(d_{i j}\right)^{\text {hs }}$ is

$$
\begin{align*}
g_{i j}\left(d_{i j}\right)^{\mathrm{hs}} & =\frac{1}{1-\zeta_{3}}+ \\
& 3\left(\frac{d_{i i} d_{j j}}{d_{i i}+d_{j j}}\right) \frac{\zeta_{2}}{\left(1-\zeta_{3}\right)^{2}}+2\left(\frac{d_{i i} d_{j j}}{d_{i i}+d_{j j}}\right)^{2} \frac{\zeta_{2}^{2}}{\left(1-\zeta^{3}\right)^{3}} \tag{35}
\end{align*}
$$


In eq 35 , if one sets $i$ equal to $j$, the expression for $g_{i i}\left(d_{i i}\right)^{\mathrm{hs}}$ given in eq 19 will be recovered.

The association energy $\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ and the effective association volume $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ between associating substances $i$ and $j$ are determined from the association energies $\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}}$ and $\varepsilon^{\mathrm{A}_{j} \mathrm{~B}_{j}}$ and the effective association volumes $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}}$ and $\kappa^{\mathrm{A}_{j} \mathrm{~B}_{j}}$, respectively. The combining rules suggested by Wolbach and Sandler ${ }^{33}$ are used. These combining rules were applied successfully by several investigators, e.g., Gross and Sadowski, ${ }^{31}$ Karakatsani et al., ${ }^{19}$ and Kleiner and Sadowski. ${ }^{22}$ These combining rules are expressed by

$$
\begin{gather*}
\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}}=\frac{1}{2}\left(\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}}+\varepsilon^{\mathrm{A}_{j} \mathrm{~B}_{j}}\right)  \tag{36}\\
\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}=\sqrt{\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}} \kappa^{\mathrm{A}_{j} \mathrm{~B}_{j}}}\left(\frac{\sqrt{\sigma_{i i} \sigma_{j j}}}{0.5\left(\sigma_{i i}+\sigma_{j j}\right)}\right)^{3} \tag{37}
\end{gather*}
$$


Hence, if one of the substances in a mixture is nonassociating, $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ and consequently $\Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ will vanish, i.e., no induced association will be considered. ${ }^{22}$

\section*{6. Results and Discussion}

Pure component parameters $m, \sigma, \varepsilon / k, \varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}} / k$, and $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}}$ for MEA, DEA, and MDEA were determined using the following objective function:
![](https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-05.jpg?height=1581&width=749&top_left_y=138&top_left_x=1110)

Figure 6. Isobaric $\mathrm{VLE}^{39}$ of the system MDEA + water at (a) 40, (b) 53.3, and (c) 67.7 kPa .

$$
\begin{equation*}
\Omega=\sum_{i=1}^{\text {npts }}\left|\frac{p_{i}^{\text {sat,exp }}-p_{i}^{\text {sat,calc }}}{p_{i}^{\text {sat,exp }}}\right|+\sum_{j=1}^{\text {npts }}\left|\frac{\rho_{j}^{\text {sat,exp }}-\rho_{j}^{\text {sat,calc }}}{\rho_{j}^{\text {sat,exp }}}\right| \tag{38}
\end{equation*}
$$

where the smoothed experimental data were taken from Yaws. ${ }^{34}$ Compressibility factors and fugacities for calculating saturated liquid densities and vapor pressures of the ethanolamines were evaluated from eqs 18-37 and the use of standard thermodynamics. ${ }^{35}$ Because MEA, DEA, and MDEA contain one or two hydroxyl functional groups, Button and Gubbins ${ }^{7}$ used a single association site for the two sets of lone pairs on oxygen and a single site for each hydrogen connected to oxygen or nitrogen. Button and Gubbins ${ }^{7}$ used this simplification to limit the number of adjustable parameters knowing the difference in bond strengths between hydrogen and oxygen and those between hydrogen and nitrogen. On the other hand, Avlund et al. ${ }^{14}$ took the known difference in the bond strength into account and totally ignored the amine functional group compared to the hydroxyl functional group. In fact, the electronegativity of nitrogen is much weaker than that of oxygen. Consequently, using two sites for each hydroxyl functional group, Avlund et al. ${ }^{14}$ adopted the 4C association scheme for DEA and MDEA

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-06.jpg?height=496&width=748&top_left_y=140&top_left_x=191}
\captionsetup{labelformat=empty}
\caption{Figure 7. Solubility of methane in MDEA. ${ }^{40}$}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-06.jpg?height=496&width=723&top_left_y=715&top_left_x=206}
\captionsetup{labelformat=empty}
\caption{Figure 8. Isothermal VLE ${ }^{38}$ of the system DEA + methanol at 365.15 K .}
\end{figure}
according to the classification of Huang and Radosz. ${ }^{8}$ Using this methodology, MEA would have two sites as MEA has only one hydroxyl functional group, i.e., the 2 B association scheme. Since the CPA model with the 4C association scheme performed better than the 2 B association scheme, Avlund et al. ${ }^{14}$ used the 4 C association scheme for MEA as well.

As such, we adopted the 4C scheme for MEA and DEA. Since PC-SAFT performed better in calculating the vapor pressures and saturated liquid densities of MDEA with the 3 B association scheme than with the 4 C association scheme, we adopted the 3B association scheme for MDEA. The missing parameters of the ethanolamines and the accuracy of PC-SAFT in correlating the vapor pressures and saturated liquid densities of the ethanolamines are given in Table 2. Table 2 also contains the PC-SAFT parameters for methanol (2B association scheme), water ( 2 B association scheme), methane, carbon dioxide, and hydrogen sulfide. For water, the 3 B and 4 C association schemes were also used successfully. ${ }^{36}$ However, in this work, the PCSAFT parameters were taken from Gross and Sadowski ${ }^{16,31}$ (2B association scheme) and applied without change.

Figure 1 shows the experimental and calculated densities of MEA and DEA. The density curve for MDEA was omitted for clarity. The agreement between the calculated and experimental values is good except near the critical points. In fact, similar to equations of state with a mean field theory, PC-SAFT overestimates experimental pressures and temperatures near the critical point. This can be shown more clearly in Figure 2, where the vapor pressure of MDEA is depicted as a function of saturated density. However, far from the critical region, where amine solutions are used in practice, the agreement is satisfactory.

Figure 3 illustrates the heat of vaporization for MEA, DEA, and MDEA as a function of temperature. It can be seen that the predictions from PC-SAFT markedly describe the experimental data. ${ }^{34}$ Figures 1-3 also indicate that PC-SAFT ac-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-06.jpg?height=496&width=732&top_left_y=142&top_left_x=1117}
\captionsetup{labelformat=empty}
\caption{Figure 9. Isobaric $\mathrm{VLE}^{41}$ of the system methanol + water at 101.3 kPa .}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-06.jpg?height=1040&width=743&top_left_y=741&top_left_x=1108}
\captionsetup{labelformat=empty}
\caption{Figure 10. Experimental ${ }^{38}$ and predicted equilibrium pressures of the system DEA + methanol + water starting at (a) 0.14553 DEA + 0.85447 water and (b) $0.07869 \mathrm{DEA}+0.92131$ water (numbers are mole fractions).}
\end{figure}
curately describes the thermodynamic properties of MDEA using the 3 B association scheme.

Figure 4 exhibits the VLE of the system MEA + water at two different total pressures, 66.66 and 101.33 kPa . Figure 4 indicates that, with a single temperature-independent binary interaction parameter $\left(k_{i j}\right)$, the VLE of the system MEA + water can be correlated accurately. From here on, the term correlation is used when a binary interaction parameter is used, i.e., $k_{i j} \neq$ 0 ; otherwise, the term prediction is used, i.e., $k_{i j}=0$. The binary interaction parameter for the system MEA + water is given in Table 3.

Figure 5 depicts the VLE of the system DEA + water in two parts. Figure 5a presents an isobaric diagram at 6.66 kPa , and Figure 5b depicts an isothermal diagram at 365.15 K . Both figures indicate that the experimental data were correlated accurately using a single temperature-independent binary interaction parameter of -0.04 .

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-07.jpg?height=1252&width=653&top_left_y=140&top_left_x=242}
\captionsetup{labelformat=empty}
\caption{Figure 11. Experimental ${ }^{42}$ (symbols) and predicted (lines) mole fractions for the species in the system $\mathrm{CO}_{2}+\mathrm{MEA}+$ water ( $w_{\text {meA }}{ }^{\circ}=19.5 \%$ and $T=313.15 \mathrm{~K}$ ).}
\end{figure}

Figure 6 is a three-part diagram, showing the VLE of the system MDEA + water at three different pressures of 40, 53.3, and 67.7 kPa , respectively. Clearly, PC-SAFT accurately predicts the VLE of aqueous MDEA solution for a wide range of temperatures with no binary interaction parameter ( $k_{i j}=0$ ).

Figure 7 demonstrates the solubility of methane in pure MDEA for the temperature range from 298 to 403 K . Shown in Figure 7 is that PC-SAFT is not predictive for this system. Nevertheless, the solubility of methane in MDEA can be correlated using a temperature-dependent binary interaction parameter as given in Table 3.

In Figure 8 one can see the VLE of the system DEA + methanol at 365.15 K . Again, with a single $k_{i j}$, it is likely to correlate the experimental equilibrium values. Methanol is often added to aqueous ethanolamine solutions to facilitate the absorption of acid gases. In order to evaluate the VLE of such ternary solutions, the binary interaction parameter for the system methanol + water is also needed. Figure 9 illustrates the isobaric VLE of the system methanol + water. PC-SAFT accurately describes the equilibrium temperatures as a function of mole fraction with a temperature-independent $k_{i j}$ of -0.045 . It is wellknown that $k_{i j}$ is a function of temperature for most equations of state. Thus accurate modeling of the VLE for the system methanol + water over the temperature range from 338 to 373 K with a single binary interaction parameter suggests that the dispersion term in PC-SAFT accurately captures the nonideality arisen from the van der Waals forces.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-07.jpg?height=1331&width=708&top_left_y=129&top_left_x=1132}
\captionsetup{labelformat=empty}
\caption{Figure 12. Experimental ${ }^{46}$ (symbols) and predicted (lines) partial pressures of (a) $\mathrm{CO}_{2}$ and (b) $\mathrm{H}_{2} \mathrm{~S}$ in $15.3 \mathrm{wt} \%$ aqueous MEA solution.}
\end{figure}

Once the VLE of the binary systems DEA + water, DEA + methanol, and methanol + water were evaluated and the binary interaction parameters were determined, we evaluated the VLE of the ternary system DEA + methanol + water starting with the solutions $0.14553 \mathrm{DEA}+0.85447$ water and 0.07869 DEA +0.92131 water (the numbers are mole fraction), respectively. Figure 10 exhibits the equilibrium pressure of the ternary systems as a function of methanol mole fraction at four different temperatures. Figure 10 indicates that PC-SAFT successfully describes the VLE of these cross-associating systems. Clearly, the predictions are in good agreement with the experimental data at low temperatures but deteriorate with increasing temperature.

In order to determine the solubility of carbon dioxide and hydrogen sulfide in the aqueous ethanolamine solutions, we first assumed that the liquid phase is ideal; i.e., we set $\gamma_{i}=1$ in eq 11. Gabrielsen et al. ${ }^{52}$ used this assumption and reasonably estimated the solubility of carbon dioxide in the aqueous ethanolamines. To see the impact of this assumption, we calculated the species mole fraction for the solubility of carbon dioxide in $19.5 \mathrm{wt} \%$ aqueous MEA. The results are exhibited in Figure 11. The agreement between the calculated and experimental values is good at small loadings up to a value of 0.5 . However, the agreement deteriorates at larger loadings. The mole fractions of carbon dioxide and MEA carbamate are overpredicted at loadings larger than 0.5 ; however, the mole fraction of $\mathrm{HCO}_{3}{ }^{-}$is accurately predicted for the whole range.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-08.jpg?height=1210&width=634&top_left_y=135&top_left_x=246}
\captionsetup{labelformat=empty}
\caption{Figure 13. Experimental ${ }^{42}$ (symbols) and predicted (lines) mole fractions for the species in the system $\mathrm{CO}_{2}+\mathrm{DEA}+$ water ( $w_{\mathrm{DEA}^{\circ}}=20 \%$ and $T =293.15 \mathrm{~K}$ ).}
\end{figure}

Since the equilibrium reaction between MEA and $\mathrm{MEAH}^{+}$is fast, the accurate mole fractions of the individual species cannot be determined experimentally. Therefore, we combined the mole fractions of both species together and compared the results to the experimental data. Clearly, the agreement is satisfactory. For the sake of completeness, the predicted mole fractions of MEA and MEAH ${ }^{+}$are also depicted in Figure 11. The results indicate that the ideal solution assumption is plausible. To keep the model predictive and show the strength of the PC-SAFT equation in calculating acid gas solubility in the aqueous ethanolamine solutions, hereon, we assume that the liquid phase behaves ideally in calculating species mole fractions ( $\gamma_{i}=1$ ). The species mole fractions having been calculated, equilibrium calculations are performed using PC-SAFT. The presence of ionic species in the liquid phase makes the equilibrium calculations difficult. In fact, the dispersion contribution between molecular species is different from that between ionic species. ${ }^{43}$ For a rigorous modeling, PC-SAFT must be revisited. A contribution for long-range ionic interactions should also be accounted for. ${ }^{44,45,53}$ However, as the ionic concentrations are small (see Figure 11) and ions are considered to solely interact with water molecules, $44,45,53$ we keep the equilibrium calculations as simple as possible by assuming an effective water mole fraction. In other words, keeping the number of moles for the acid gas and the amine constant, the number of moles for the ionic species and water are lumped together. Then, the liquid phase would only contain three molecular species, i.e., water, ethanolamine, and the acid gas. Consequently, equilibrium calculations would be performed easily for this pseudoternary system.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-08.jpg?height=1241&width=668&top_left_y=138&top_left_x=1149}
\captionsetup{labelformat=empty}
\caption{Figure 14. Experimental ${ }^{47}$ (symbols) and predicted (lines) partial pressures of (a) $\mathrm{CO}_{2}$ and (b) $\mathrm{H}_{2} \mathrm{~S}$ in $25 \mathrm{wt} \%$ aqueous DEA solution.}
\end{figure}

Parts a and b of Figure 12 exhibit the solubilities of carbon dioxide and hydrogen sulfide in $15.3 \mathrm{wt} \%$ aqueous MEA solutions at different temperatures, respectively. While no adjustable parameter was used, PC-SAFT satisfactorily described the solubility data, especially at high temperatures. Clearly, in comparison to carbon dioxide, the solubility data of hydrogen sulfide in the aqueous MEA solution were more accurately predicted.

Figure 13 shows the species mole fraction in the liquid phase for calculating the solubility of carbon dioxide in $20 \mathrm{wt} \%$ aqueous DEA solution at 293 K . Experimental data are also shown in Figure 13. Clearly the agreement between the calculated and experimental data is quite good. Once more, the calculations indicated that the ideal solution assumption is reasonable.

Parts $a$ and $b$ of Figure 14 depict carbon dioxide and hydrogen sulfide solubilities in $25 \mathrm{wt} \%$ aqueous DEA solution at different temperatures, respectively. The agreement between the predicted and experimental values is more pronounced at higher temperatures. Depicted in Figure 14, PC-SAFT more accurately predicts the solubility of hydrogen sulfide than that of carbon dioxide in the aqueous DEA solution.

Figure 15 illustrates the mole fractions of species produced by dissolving carbon dioxide in a $20 \mathrm{wt} \%$ MDEA aqueous solution at 373 K . No experimental data were found for comparison. When compared to similar calculations made in the literature, ${ }^{48}$ the results were found to be quite similar.

In parts a and b of Figure 16, the total pressures of the vapor phase containing carbon dioxide and hydrogen sulfide were respectively predicted and compared to the experimental data.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-09.jpg?height=602&width=655&top_left_y=140&top_left_x=240}
\captionsetup{labelformat=empty}
\caption{Figure 15. Predicted mole fractions for species in the system $\mathrm{CO}_{2}+$ MDEA + water $\left(w_{\text {Mdea }}{ }^{\circ}=20 \%\right.$ and $\left.T=373.15 \mathrm{~K}\right)$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-09.jpg?height=1303&width=687&top_left_y=851&top_left_x=225}
\captionsetup{labelformat=empty}
\caption{Figure 16. Experimental ${ }^{49}$ (symbols) and predicted (lines) total pressures of the systems (a) $\mathrm{CO}_{2}+$ MDEA + water ( $w_{\text {MDEA }}{ }^{\circ}=48.77 \%$ ) and (b) $\mathrm{H}_{2} \mathrm{~S}+$ MDEA + water $\left(w_{\text {MDEA }}{ }^{\circ}=48.79 \%\right)$ at different temperatures.}
\end{figure}

Obviously, PC-SAFT markedly predicts the experimental values for the whole temperature and loading range. However, the predictions are less accurate for the solubility of carbon dioxide in MDEA solutions, especially at 393 K , where PC-SAFT systematically underpredicts the experimental solubility data. The result might be improved by the removing ideal solution assumption and using an electrolyte perturbation term for the weak electrolytes. ${ }^{53}$

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/9c764164-a3fe-491f-8bb1-75d54cd27420-09.jpg?height=1278&width=653&top_left_y=129&top_left_x=1157}
\captionsetup{labelformat=empty}
\caption{Figure 17. Experimental ${ }^{50}$ (symbols) and predicted (lines) partial pressures of $\mathrm{CO}_{2}$ in different aqueous MDEA solutions (weight \%) at (a) 323.15 and (b) 373.15 K .}
\end{figure}

Finally, in parts a and b of Figure 17, one can see the predictions of partial pressures for the solubility of carbon dioxide in different weight percent aqueous MDEA solutions at 323 and 373 K , respectively. The agreement with experimental data is less satisfactory at small loadings. The agreement with experimental data is also less satisfactory at 323 K than at 373 K .

\section*{7. Conclusion}

PC-SAFT has been applied to MEA, DEA, and MDEA. The pure component parameters for these ethanolamines have been determined and reported. For MEA and DEA, the 4C association scheme was used. For MDEA, the 3 B association scheme was the best.

The VLE of aqueous ethanolamine solutions have been evaluated and their binary interaction parameters have been determined and reported.

PC-SAFT has also been employed to calculate the solubility of methane in MDEA. It was found that PC-SAFT is not predictive for this system. However, the methane solubility in MDEA can be correlated using a temperature-dependent binary interaction parameter.

The accuracy of PC-SAFT in predicting the VLE of the ternary system DEA + methanol + water has been evaluated. The results have shown that PC-SAFT qualitatively describes the experimental values at high temperatures; however, at low temperatures the predictions are more accurate.

PC-SAFT has been used to predict the solubility of acid gases in the aqueous ethanolamine solutions for wide ranges of loadings and temperatures. While no adjustable parameter was used, PC-SAFT predicted the solubility of hydrogen sulfide more accurately than that of carbon dioxide in the ethanolamine solutions. At higher temperatures, the agreement between the experimental data and the predicted ones is more pronounced.

\section*{List of Symbols}
$a=$ reduced Helmholtz free energy (A/RT)
$a_{j}=$ polynomials given in ref 16
$A=$ molar Helmholtz free energy ( $\mathrm{J} \mathrm{mol}^{-1}$ )
$b_{j}=$ polynomials given in ref 16
$C_{1}=$ compressibility of hard-chain fluid given by eq 24
calcd $=$ calculated value
$d=$ soft repulsion diameter ( $\AA$ )
exptl $=$ experimental value
$g=$ radial distribution function at contact
$I_{1}=$ parameter defined by eq 25
$I_{2}=$ parameter defined by eq 26
$k=$ Boltzmann constant $\left(1.38066 \times 10^{-23} \mathrm{~J} \mathrm{~K}^{-1}\right)$
$k_{i}^{x}=$ mole fraction-based equilibrium constant for reaction $i$
$k_{i j}=$ binary interaction parameter
$L=$ loading (moles of acid gas/mole of amine)
$m=$ number of segments in a molecule
$\bar{m}=$ mean value for the number of segments in a mixture
$M=$ number of association sites on a molecule
$\mathrm{nc}=$ number of components
npts $=$ number of experimental data points
$N=$ number of moles
$N_{\mathrm{Av}}=$ Avogadro's constant ( $6.022 \times 10^{23} \mathrm{~mol}^{-1}$ )
$p=$ pressure ( Pa )
$R=$ universal gas constant ( $8.314 \mathrm{~J} \mathrm{~mol}^{-1} \mathrm{~K}^{-1}$ )
$T=$ temperature (K)
$x=$ mole fraction
$y=$ vapor phase mole fraction
$X^{\mathrm{A}_{i}}=$ fraction of molecules of component $i$ not bonded at site A
$Z=$ compressibility factor

\section*{Greek Symbols}
$\gamma=$ activity coefficient
$\varepsilon=$ depth of square-well potential (J)
$\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{i}}=$ association energy between sites A and B on the same molecules (J)
$\varepsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}}=$ association energy between site A on molecule $i$ and site B on molecule $j(\mathrm{~J})$
$\phi=$ fugacity coefficient
$\zeta=$ parameter defined by eq 20
$\eta=$ packing fraction ( $\zeta_{3}$ )
$\kappa^{\mathrm{A}_{i} \mathrm{~B}_{i}}=$ association volume between sites A and B on the same molecules
$\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}=$ association volume between site A on molecule $i$ and site B on molecule $j$
$\pi=$ constant (3.141 592 6)
$\rho=$ molar density ( $\mathrm{mol} \mathrm{m}^{-3}$ )
$\nu=$ stoichiometric number in a reaction
$\sigma=$ diameter of a segment ( $\AA$ )
$\Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}=$ association strength between site A on molecule $i$ and site B on molecule $j\left(\AA^{3}\right)$
$\Omega=$ objective function

\section*{Subscripts/Superscripts}
assoc $=$ association
$\mathrm{Am}=$ amine
$\mathrm{A}_{i}=$ site A on molecule $i$
$\mathrm{B}_{i}=$ site B on molecule $i$
calc $=$ calculated value
chain = chain term
disp = dispersion term
exp $=$ experimental value
hc = hard chain
hs = hard sphere
$i, j, k=$ dummy indices
1= liquid
$\mathrm{m}=$ mixture
$n=$ dummy index
polar $=$ polar term
res $=$ residual
sat $=$ saturated
$\mathrm{v}=$ vapor
${ }^{\circ}=$ initial value for number of moles or weight $\%$

\section*{Literature Cited}
(1) Jakobsen, J. P.; Krane, J.; Svendsen, H. F. Liquid-Phase Composition Determination in $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{O}$-alkanolamine systems: An NMR study. Ind. Eng. Chem. Res. 2005, 44, 9894.
(2) Jou, F.-Y.; Carroll, J. J.; Mather, A. E.; Otto, F. D. Solubility of Methane and Ethane in Aqueous Solutions of Methyldiethanolamine. J. Chem. Eng. Data 1998, 43, 781.
(3) Jou, F.-Y.; Mather, A. E. Solubility of Ethane in Aqueous Solutions of Monoethanolamine and Diethanolamine. J. Chem. Eng. Data 2006, 51, 1141.
(4) Kent, R. L.; Eisenberg, B. Better Data for Amine Treating. Hydrocarbon Process. 1976, 55, 87.
(5) Pitsinigos, V. D.; Lygeros, A. I. Predicting $\mathrm{H}_{2} \mathrm{~S}$-MEA Equilibria. Hydrocarbon Process. 1989, 68, 43.
(6) Posey, M. L.; Rochelle, G. T. A Thermodynamic Model of Methyldiethanolamine- $\mathrm{CO}_{2}-\mathrm{H}_{2} \mathrm{~S}$-Water. Ind. Eng. Chem. Res. 1997, 36, 3944.
(7) Button, J. K.; Gubbins, K. E. SAFT Prediction of Vapour-Liquid Equilibria of Mixtures Containing Carbon Dioxide and Aqueous Monoethanolamine or Diethanolamine. Fluid Phase Equilib. 1999, 158-160, 175.
(8) Huang, S. H.; Radosz, M. Equation of State for Small, Large, Polydisperse, and Associating Molecules. Ind. Eng. Chem. Res. 1990, 29, 2284.
(9) Huang, S. H.; Radosz, M. Equation of State for Small, Large, Polydisperse, and Associating Molecules: Extension to Fluid Mixtures. Ind. Eng. Chem. Res. 1991, 30, 1994.
(10) Austgen, D. M.; Rochelle, G. T.; Peng, X.; Chen, C.-C. Model of Vapor-Liquid-Equilibria for Aqueous Acid Gas-Alkanolamine Systems Using the Electrolyte-NRTL Equation. Ind. Eng. Chem. Res. 1989, 28, 1060.
(11) Müller, E. A.; Gubbins, K. E. Molecular-Based Equations of State for Associating Fluids: A Review of SAFT and Related Approaches. Ind. Eng. Chem. Res. 2001, 40, 2193.
(12) Economou, I. G. Statistical Associating Fluid Theory: A Successful Model for the Calculation of Thermodynamic and Phase Equilibrium Properties of Complex Fluid Mixtures. Ind. Eng. Chem. Res. 2002, 41, 953.
(13) Von Solms, N.; Kouskoumvekaki, I. A.; Michelsen, M. L.; Kontogeorgis, G. M. Capabilities, Limitations and Challenges of a Simplified PC-SAFT Equation of State. Fluid Phase Equilib. 2006, 241, 344.
(14) Avlund, A. S.; Kontogeorgis, G. M.; Michelsen, M. L. Modeling Systems Containing Alkanolamines with the CPA Equation of State. Ind. Eng. Chem. Res. 2008, 47, 7441.
(15) Kontogeorgis, G. M.; Voutsas, E. C.; Yakoumis, I. V.; Tassios, D. P. An Equation of State for Associating Fluids. Ind. Eng. Chem. Res. 1996, 35, 4310.
(16) Gross, J.; Sadowski, G. Perturbed-Chain SAFT: An Equation of State Based on a Perturbation Theory for Chain Molecules. Ind. Eng. Chem. Res. 2001, 40, 1244.
(17) Al-Saifi, N. M.; Hamad, E. Z.; Englezos, P. Prediction of VaporLiquid Equilibrium in Water-Alcohol-Hydrocarbon Systems with the Dipolar Perturbed-Chain SAFT Equation of State. Fluid Phase Equilib. 2008, 271, 82.
(18) Karakatsani, E. K.; Economou, I. G. Perturbed Chain-Statistical Associating Fluid Theory Extended to Dipolar and Quadrupolar Molecular Fluids. J. Phys. Chem. B 2006, 110, 9252.
(19) Karakatsani, E. K.; Spyriouni, T.; Economou, I. G. Extended Statistical Associating Fluid Theory (SAFT) Equations of State for Dipolar Fluids. AIChE J. 2005, 51, 2328.
(20) Dominik, A.; Chapman, W. G.; Kleiner, M.; Sadowski, G. Modeling of Polar Systems with the Perturbed-Chain SAFT Equation of State. Investigation of the Performance of Two Polar Terms. Ind. Eng. Chem. Res. 2005, 44, 6928.
(21) Tumakaka, F.; Sadowski, G. Application of the Perturbed-Chain SAFT Equation of State to Polar Systems. Fluid Phase Equilib. 2004, 217, 233.
(22) Kleiner, M.; Sadowski, G. Modeling of Polar Systems Using PCPSAFT: An Approach to Account for Induced-Association Interactions. J. Phys. Chem. C 2007, 111, 15544.
(23) Karakatsani, E. K.; Economou, I. G. Phase Equilibrium Calculations for Multi-Component Polar Fluid Mixtures with tPC-PSAFT. Fluid Phase Equilib. 2007, 261, 265.
(24) Boublik, T. Hard Sphere Equation of State. J. Chem. Phys. 1970, 53, 471.
(25) Mansoori, G. A.; Carnahan, N. F.; Starling, K. E.; Leland, T. W. Equilibrium Thermodynamic Properties of the Mixture of Hard Spheres. J. Chem. Phys. 1971, 54, 1523.
(26) Ghonasgi, D.; Chapman, W. G. A New Equation of State for Hard Chain Molecules. J. Chem. Phys. 1994, 100, 6633.
(27) Nasrifar, Kh.; Bolland, O. Simplified Hard-Sphere and Hard-Sphere Chain Equations of State for Engineering Applications. Chem. Eng. Commun. 2006, 193, 1277.
(28) Nasrifar, Kh. A Semi-Empirical Hard-Sphere Chain Equation of State: Pure and Mixture. Fluid Phase Equilib. 2007, 261, 258.
(29) Chapman, W. G.; Jackson, G.; Gubbins, K. E. Phase Equilibria of Associating Fluids. Chain Molecules with Multiple Bonding Sites. Mol. Phys. 1988, 65, 1057.
(30) Wertheim, M. S. Thermodynamic Perturbation Theory of Polymerization. J. Chem. Phys. 1987, 87, 7323.
(31) Gross, J.; Sadowski, G. Application of the Perturbed-Chain SAFT Equation of State to Associating Systems. Ind. Eng. Chem. Res. 2002, 41, 5510.
(32) Chapman, W. G.; Gubbins, K. E.; Jackson, G.; Radosz, M. New Reference Equation of State for Associating Liquids. Ind. Eng. Chem. Res. 1990, 29, 1709.
(33) Wolbach, J. P.; Sandler, S. I. Using Molecular Orbital Calculations to Describe the Phase Behavior of Cross-Associating mixtures. Ind. Eng. Chem. Res. 1998, 37, 2917.
(34) Yaws, C. L. Chemical Properties Handbook: Physical, Thermodynamic, Environmental, Transport, Safety, and Health related Properties for Organic and Inorganic Chemicals; McGraw-Hill: New York, 1999.
(35) Prausnitz, J. M.; Lichtenthaler, R. N.; Gomes de Azevedo, E. Molecular Thermodynamics of Fluid-Phase Equilibria; Prentice Hall: Englewood Cliffs, NJ, 1999.
(36) Economou, I. G.; Tsonopoulos, C. Association Models and Mixing Rules in Equation of State for Water/Hydrocarbon Mixtures. Chem. Eng. Sci. 1997, 52, 511.
(37) Cai, Z.; Xie, R.; Wu, Z. Binary Isobaric Vapor-Liquid Equilibria of Ethanolamines + Water. J. Chem. Eng. Data 1996, 41, 1101.
(38) Horstmann, S.; Mougin, P.; Lecomte, F.; Fischer, K.; Gmehling, J. Phase Equilibrium and Excess Enthalpy Data for the System Methanol + 2, 2'-Diethanolamine + Water. J. Chem. Eng. Data 2002, 47, 1496.
(39) Voutsas, E.; Vrachnos, A.; Magoulas, K. Measurement and Thermodynamic Modeling of the Phase Equilibrium of Aqueous NMethyldiethanolamine solutions. Fluid Phase Equilib. 2004, 224, 193.
(40) Jou, F.-Y.; Mather, A. E. Solubility of Methane in Methyldiethanolamine. J. Chem. Eng. Data 2006, 51, 1429.
(41) Kurihara, K.; Nakamichi, M.; Kojima, K. Isobaric Vapor-Liquid Equilibria for Methanol + Ethanol + Water and the Three Constituent Binary Systems. J. Chem. Eng. Data 1993, 38, 446.
(42) Böttinger, W.; Maiwald, M.; Hasse, H. Online NMR Spectroscopic Study of Species Distribution in MEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$ and DEA- $\mathrm{H}_{2} \mathrm{O}-\mathrm{CO}_{2}$. Fluid Phase Equilib. 2008, 263, 131.
(43) Fürst, W.; Renon, H. Representation of Excess Properties of Electrolyte Solutions Using a New Equation of State. AIChE J. 1993, 39, 335.
(44) Galindo, A.; Gil-Villegas, A.; Jackson, G.; Burgess, A. N. SAFTVR: Phase Behavior of Electrolyte Solutions with the Statistical Associating Fluid Theory for Potential of Variable Range. J. Phys. Chem. B 1999, 103, 10272.
(45) Cameretti, L. F.; Sadowski, G.; Mollerup, J. M. Modeling of Aqueous Electrolyte Solutions with Perturbed-Chain Statistical Associated Fluid Theory. Ind. Eng. Chem. Res. 2005, 44, 3355.
(46) Jones, J. H.; Froning, H. R.; Claytor, E. E., Jr. Solubility of Acid Gases in Aqueous Monoethanolamine. J. Chem. Eng. Data 1959, 4, 85.
(47) David Lawson, J.; Garst, A. W. Gas Sweetening Data: Equilibrium Solubility of Hydrogen Sulfide and Carbon Dioxide in Aqueous Monoethanolamine and Aqueous Diethanolamine. J. Chem. Eng. Data 1976, 21, 20.
(48) Vrachnos, A.; Voutsas, E.; Magoulas, K.; Lygeros, A. Thermodynamics of Acid Gas-MDEA-Water Systems. Ind. Eng. Chem. Res. 2004, 43, 2798.
(49) Pérez-Salado Kamps, Á.; Balaban, A.; Jödecke, M.; Kuranov, G.; Smirnova, N. A.; Maurer, G. Solubility of Single Gases Carbon Dioxide and Hydrogen Sulfide in Aqueous Solutions of N-Methyldiethanolamine at Temperatures from 313 to 393 K and Pressures up to 7.6 MPa : New Experimental Data and Model Extension. Ind. Eng. Chem. Res. 2001, 40, 696.
(50) Rho, S.-W.; Yoo, K.-P.; Lee, J. S.; Nam, S. C.; Son, J. E.; Min, B.-M. Solubility of $\mathrm{CO}_{2}$ in Aqueous Methyldiethanolamine solutions. J. Chem. Eng. Data 1997, 42, 1161.
(51) Austgen, D. M.; Rochelle, G. T.; Chen, C.-C. Model of VaporLiquid Equilibria for Aqueous Acid Gas-Alkanolamine systems. 2. Representation of $\mathrm{H}_{2} \mathrm{~S}$ and $\mathrm{CO}_{2}$ Solubility in Aqueous MDEA and $\mathrm{CO}_{2}$ Solubility in Aqueous Mixtures of MDEA with MEA or DEA. Ind. Eng. Chem. Res. 1991, 30, 543.
(52) Gabrielsen, J.; Michelsen, M. L.; Stenby, E. H.; Kontogergis, G. M. A Model for Estimating $\mathrm{CO}_{2}$ Solubility in Aqueous Alkanolamines. Ind. Eng. Chem. Res. 2005, 44, 3348.
(53) Held, C.; Sadowski, G. Modeling Aqueous Electrolyte Solutions. Part 2. Weak Electrolytes. Fluid Phase Equilib. 2009, 279, 141.

Received for review July 25, 2009
Revised manuscript received June 14, 2010
Accepted June 18, 2010
IE901181N