\title{
Thermodynamic Modeling of Pure, Binary, and Ternary Mixtures of Alkanolamines Using Three Versions of SAFT Equations of State
}

\author{
Arash Pakravesh* and Hosseinali Zarei
}

Cite This: J. Chem. Eng. Data 2025, 70, 1182-1194
Read Online
Downloaded via BRIGHAM YOUNG UNIV on September 23, 2025 at 20:21:54 (UTC). See https://pubs.acs.org/sharingguidelines for options on how to legitimately share published articles.

\begin{abstract}
Accurate thermodynamic modeling of pure alkanolamines and their mixtures plays a key role in the design and development of various industrial processes. Due to the effectiveness of SAFT-type equations of state (EOSs) in the thermodynamic modeling, in this study, we applied the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs to model the four most widely used alkanolamines, including monoethanolamine (MEA), diethanolamine (DEA), methyldiethanolamine (MDEA), and 2-amino-2-methyl-1-propanol (AMP). First, the pure-compound parameters for the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR EOS were obtained using $P \rho T$ data over a wide range of temperature and pressure. The thermodynamic properties of pure
![](https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-01.jpg?height=385&width=725&top_left_y=821&top_left_x=1207)
alkanolamines, including density, isobaric heat capacity, sound velocity, isobaric thermal expansivity, isothermal compressibility, saturated vapor pressure, saturated liquid density, and critical point, were calculated using P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs and compared with experimental data. The P $\rho$ T-SAFT-HR EOS demonstrated superior performance in predicting these thermodynamic properties. The calculations were then extended to mixtures, where the thermodynamic properties of eight binary and five ternary alkanolamine mixtures were modeled by using EOSs. Comparing the results of the studied EOSs in predicting the thermodynamic properties of binary and ternary mixtures also revealed the superior performance of the P $\rho$ T-SAFT-HR EOS.
\end{abstract}

\section*{1. INTRODUCTION}

Alkanolamines and their aqueous solutions have many applications in industry, from acid gas separation to enhanced fossil fuel recovery. ${ }^{1}$ Accurate knowledge of the thermodynamic properties of alkanolamines plays a key role in the design and operation of chemical and biochemical processes. ${ }^{1-4}$ Thermodynamic modeling is even more important in separation processes, such as acid gas removal, because more than $40 \%$ of the total cost of such processes is related to the separation unit. ${ }^{5}$ Thermodynamic modeling of pure alkanolamines and their mixtures is, therefore, a basic requirement for their industrial applications. ${ }^{6}$ MEA, DEA, MDEA, and AMP are some of the most widely used solvents in acid gas removal processes. ${ }^{7}$ Since the process of acid gas removal using these alkanolamines is based on chemical absorption, the thermodynamic models describing them are generally classified into three major categories: semiempirical models, excess Gibbs energy models, and EOSs. Among these, EOSs are promising for predicting the thermodynamic properties of pure alkanolamines and their mixtures due to their superior predictability and requirement for fewer adjusted parameters. ${ }^{8}$

Since the late 1980s, the statistical associating fluid theory (SAFT) ${ }^{9-11}$ has become an important and practical model for predicting the thermodynamic properties of a wide range of fluids. ${ }^{12-16}$ Drawing from the thermodynamic perturbation theory (TPT1) of Wertheim, ${ }^{17-20}$ the SAFT was developed as a versatile model capable of describing the thermodynamic
properties of complex fluids, including polar and associating fluids, in contrast to classical EOSs [18]. Theoretical and computational flexibility of the SAFT EOS has made it possible to continuously modify and develop different versions of the model, including Soft-SAFT, ${ }^{21}$ SAFT-CP, ${ }^{22}$ PC-SAFT, ${ }^{23}$ SAFT-VR-Mie, ${ }^{24}$ and more recently P $\rho$ T-SAFT-HR. ${ }^{25}$ Therefore, studying the performance of the SAFT-type EOSs to predict the thermodynamic properties of alkanolamines, as associating fluids, as well as their aqueous solutions, has attracted much attention in recent years. ${ }^{26}$

The first step in applying the SAFT-type EOSs is to estimate their pure-compound parameters. ${ }^{27}$ SAFT-type EOSs typically have five (or six) adjustable parameters for associating fluids. These parameters can be obtained by fitting experimental data. ${ }^{28}$ Therefore, in order to apply SAFT-type EOSs to predict the thermodynamic properties of alkanolamines, their pure-compound parameters must first be estimated. Traditionally, saturated vapor pressure and liquid-phase density data have been used to calculate the adjustable parameters of the

Received: July 14, 2024
Revised: November 16, 2024
Accepted: November 21, 2024
Published: November 29, 2024
![](https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-01.jpg?height=216&width=151&top_left_y=2342&top_left_x=1781)
alkanolamines. However, the results of previous studies have shown that the use of experimental data of other thermodynamic properties such as critical point, sound velocity, and pressure-density-temperature, independently or in combination with saturated vapor pressure and liquid-phase density data, to calculate pure component parameters can improve the results of the thermodynamic model. ${ }^{25,28-31}$

Button and Gubbins' study ${ }^{27}$ was the first effort to estimate SAFT-type EOS adjustable parameters for alkanolamines. They used the SAFT-HR EOS to predict the vapor-liquid equilibria (VLE) of binary and ternary mixtures containing MEA and DEA. After that, several modified versions of the SAFT EOS have been applied to thermodynamically model alkanolamine systems including MEA, AMP, DEA, and MDEA. By estimating the pure-compound parameters of the PC-SAFT EOS for MEA, DEA, and MDEA, Nasrifar and Tafazol ${ }^{32}$ predicted the thermodynamic properties of binary and ternary mixtures containing these alkanolamines. Mac Dowell et al. ${ }^{33}$ modeled the fluid-phase behavior of carbon dioxide in aqueous solutions of MEA by obtaining the parameters of the SAFT-VR EOS for MEA. Continuing the previous research, Rodriguez et al. ${ }^{34}$ studied the phase behavior of carbon dioxide in aqueous solutions of MEA, DEA, MDEA, and AMP using the SAFT-VR EOS. Pereira et al. ${ }^{8,35}$ calculated the thermodynamic properties of alkanolamine mixtures, including MEA, DEA, MDEA, and AMP, using the Soft-SAFT EOS. Najafloo and Zarei ${ }^{36}$ investigated the performance of the SAFT-HR EOS for modeling the solubility of carbon dioxide in aqueous monoethanolamine solutions by calculating the parameters of the SAFT-HR EOS for MEA. Ayad et al. ${ }^{37}$ also used PC-SAFT EOS to predict the thermodynamic properties of AMP binary mixtures with different types of solvents. Moreover, SAFT-type EOSs are becoming a popular choice for thermodynamic modeling of alkanolamine mixtures, ${ }^{35}$ and several versions of SAFT EOS such as PC-SAFT, ${ }^{6,37-45}$ SAFT-VR, ${ }^{46}$ SAFT-VRSW, ${ }^{47}$ SAFT-VR-Mie, ${ }^{48-50}$ Soft-SAFT, ${ }^{26,51,52}$ GC-PPCSAFT, ${ }^{53}$ sPC-SAFT, ${ }^{54}$ eSAFT-HR, ${ }^{55}$ and ePC-SAFT ${ }^{56-58}$ have been applied many times for thermodynamic modeling of alkanolamine mixtures.

This contribution investigates the performance of the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR, ${ }^{25}$ PC-SAFT, ${ }^{23}$ and SAFT-HR ${ }^{11}$ EOSs in modeling the thermodynamic properties of four pure alkanolamines, namely, MEA, DEA, MDEA, and AMP, and eight binary and five ternary mixtures containing these alkanolamines. In this regard, a wide range of $P \rho T$ data is used to estimate the purecompound parameters of the P $\rho$ T-SAFT-HR for MEA, DEA, MDEA, and AMP. Subsequently, the thermodynamic properties, including density ( $\rho$ ), isobaric heat capacity ( $C_{P}$ ), sound velocity ( $u$ ), isobaric thermal expansivity ( $\alpha_{P}$ ), isothermal compressibility ( $\kappa_{T}$ ), saturated vapor pressure ( $P^{\text {sat }}$ ), saturated liquid density ( $\rho_{\text {liq }}$ ), and critical point (CP) are calculated using P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs. Then, the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs are extended to mixtures, and the thermodynamic properties of eight binary mixtures and five ternary mixtures containing alkanolamines are predicted using them and the performance of P $\rho$ T-SAFT-HR EOS in predicting the thermodynamic properties of pure and mixed alkanolamines was compared with results obtained from SAFT-HR ${ }^{36}$ and PC-SAFT ${ }^{32}$ EOS calculations.

\section*{2. COMPUTATIONAL METHODS}
2.1. SAFT-HR. The Huang-Radosz ${ }^{11,59}$ variant of the statistical associating fluid theory EOS (SAFT-HR EOS) offers a robust framework for predicting the thermodynamic properties of fluids and mixtures. Unlike simpler models, such as cubic EOSs, SAFT-HR EOS delves deeper, representing molecules as segmented chains with distinct interaction sites. These sites embody specific functionalities such as hydrogen bonding, allowing for a more realistic portrayal of how molecules interact with each other.

The SAFT-HR EOS is generally formulated as a function of Helmholtz free energy:

$$
\begin{equation*}
a^{\text {res }}=a-a^{\text {ideal }}=a^{\text {seg }}+a^{\text {chain }}+a^{\text {assoc }} \tag{1}
\end{equation*}
$$

where $a, a^{\text {res }}, a^{\text {ideal }}, a^{\text {seg }}, a^{\text {chain }}$, and $a^{\text {assoc }}$ are total, residual, ideal, segment, chain, and association Helmholtz-free energy, respectively. The model parameters were traditionally determined by fitting the SAFT-HR EOS to saturated vapor pressure and liquid density data. ${ }^{11,36}$ The SAFT-HR EOS parameter values are presented in Table S1 of the Supporting Information.
2.2. PC-SAFT. Gross and Sadowski ${ }^{23,60}$ significantly advanced the SAFT EOS by modifying its dispersion contribution. To achieve this, they employed a hard-chain reference fluid and developed a perturbation theory for it. This modified EOS, known as the perturbed-chain SAFT (PCSAFT) EOS, has gained widespread popularity due to its improved accuracy in predicting thermodynamic properties. ${ }^{61}$ The PC-SAFT EOS can be written as

$$
\begin{equation*}
a^{\mathrm{res}}=a^{\mathrm{hc}}+a^{\mathrm{dis}}+a^{\mathrm{assoc}} \tag{2}
\end{equation*}
$$

where $a^{\text {hc }}$ stands for hard-chain and $a^{\text {dis }}$ represents the dispersion Helmholtz-free energy. The PC-SAFT EOS also requires five adjustable parameters. These parameters are determined by fitting the model to saturated vapor pressure and liquid density data, ${ }^{37,43,60}$ as detailed in Table S1 of the Supporting Information.
2.3. P $\rho$ T-SAFT-HR. P $\rho$ T-SAFT-HR EOS ${ }^{25}$ is a pressure-density-temperature ( $P \rho T$ ) reparameterization of the SAFTHR EOS, achieved by utilizing a more advanced computational method and fitting experimental $P \rho T$ data instead of VLE data for parametrization. Therefore, the structure of the P $\rho$ T-SAFTHR EOS resembles that of the SAFT-HR EOS, but their specific pure component parameters differ.

The P $\rho$ T-SAFT-HR EOS requires five adjustable parameters (three nonassociating parameters and two associating parameters) to calculate the thermodynamic properties of pure associating fluids, which are estimated from $P \rho T$ data over a wide range of pressure and temperature. ${ }^{25}$ In order to estimate the adjustable parameters of the P $\rho$ T-SAFT-HR EOS, the following objective function is optimized:

$$
\begin{align*}
& \mathrm{OF}=\mathrm{OF}_{P}+\mathrm{OF}_{\rho}+\mathrm{OF}_{T}  \tag{3}\\
& \mathrm{OF}_{Y}=\frac{1}{N_{P}} \sum_{i=1}^{N_{p}}\left|\frac{Y_{i}^{\mathrm{cal}}-Y_{i}^{\exp }}{Y_{i}^{\exp }}\right| \tag{4}
\end{align*}
$$

where $N_{P}$ represents the number of data points, and $Y$ denotes the thermodynamic properties (pressure $P$, density $\rho$, and temperature $T$ ), and "cal" and "exp" refer to calculated and experimental data, respectively. In this study, the $P \rho T$ data required to estimate the adjustable parameters of the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR EOS for alkanolamines have been collected from

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1. P $\rho$ T-SAFT-HR EOS Parameters for the Four Studied Alkanolamines}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|l|}
\hline compound & MM, g/mol & $T$ range, $\mathbf{K}$ & $P$ range, MPa & $m$ & $\boldsymbol{u} / k_{b}, \mathbf{K}$ & $10^{-6} v^{00}$, $\mathrm{m}^{3} / \mathrm{mol}$ & $\boldsymbol{\varepsilon}^{A B} / k_{b}, \mathbf{K}$ & $\mathbf{1 0}^{\mathbf{2}} \boldsymbol{\boldsymbol { \kappa } ^ { A B }}$ & \%OF & data source & ref. \\
\hline MEA (2B) & 61.083 & 293-423 & 5-90 & 2.2228 & 462.409 & 16.8457 & 1136.95 & 4.69057 & 2.31 & 62 & This work \\
\hline AMP (2B) & 89.136 & 313-362 & 1-21 & 3.6614 & 357.020 & 15.4111 & 1754.68 & 3.73451 & 3.47 & 64 & This work \\
\hline DEA (3B) & 105.136 & 313-423 & 5-90 & 3.5012 & 476.205 & 17.4258 & 2226.43 & 0.71632 & 2.32 & 62 & This work \\
\hline MDEA (3B) & 119.162 & 313-362 & 1-20 & 4.2022 & 410.174 & 16.7847 & 575.91 & 25.2412 & 1.86 & 63 & This work \\
\hline water (2B) & 18.015 & 273-1373 & 0.1-1000 & 1.0007 & 330.107 & 10.500 & 3145.72 & 4.0285 & 12.33 & 73 & 25 \\
\hline methanol (2B) & 32.042 & 275-615 & 0.1-800 & 1.4856 & 248.185 & 15.000 & 3187.65 & 0.77045 & 12.74 & 73 & 25 \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2. Results of Predicting the Thermodynamic Properties of the Investigated Alkanolamines Using PpT-SAFT-HR, PCSAFT, and SAFT-HR EOSs}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[b]{2}{*}{compound} & \multirow[b]{2}{*}{equation of state} & \multirow[b]{2}{*}{A. S. ${ }^{a}$} & \multicolumn{9}{|c|}{\%AAD} & \multirow[b]{2}{*}{data source} \\
\hline & & & $\rho$ & $\boldsymbol{C}_{\boldsymbol{P}}$ & $u$ & $\boldsymbol{\alpha}_{p}$ & $\boldsymbol{\kappa}_{T}$ & $P^{\text {sat }}$ & $\boldsymbol{\rho}_{\text {liq }}$ & CP ${ }^{b}$ & ave ${ }^{c}$ & \\
\hline \multirow[t]{3}{*}{MEA} & P $\rho$ T-SAFT-HR & 2B & 0.027 & 9.96 & 1.17 & 1.52 & 2.68 & 2.54 & 0.53 & 14.00 & 4.05 & 62,77,79-85 \\
\hline & SAFT-HR & 2B & 0.769 & 6.05 & 6.91 & 7.04 & 12.66 & 3.02 & 0.37 & 17.11 & 6.74 & \\
\hline & PC-SAFT & 4C & 1.956 & 16.18 & 0.55 & 34.20 & 9.95 & 2.58 & 0.46 & 11.31 & 9.65 & \\
\hline \multirow[t]{2}{*}{DEA} & P $\rho$ T-SAFT-HR & 3B & 0.028 & 5.23 & 0.30 & 1.26 & 3.52 & 3.42 & 0.79 & & 2.08 & 62,77,82-86 \\
\hline & PC-SAFT & 4C & 1.000 & 3.47 & 20.00 & 47.20 & 62.56 & 2.72 & 0.89 & & 19.69 & \\
\hline \multirow[t]{2}{*}{MDEA} & P $\rho$ T-SAFT-HR & 3B & 0.007 & 9.91 & 0.60 & 0.71 & 1.14 & 3.92 & 1.02 & 18.6 & 4.49 & \multirow[t]{2}{*}{63,77,79,80,84,85,87,88} \\
\hline & PC-SAFT & 3B & 1.001 & 2.23 & 4.92 & 4.57 & 8.26 & 2.48 & 1.00 & 10.25 & 4.34 & \\
\hline \multirow[t]{2}{*}{AMP} & P $\rho$ T-SAFT-HR & 2B & 0.014 & 4.85 & 0.91 & 0.83 & 2.36 & 1.57 & & & 1.76 & 64,78,80,84-86,89,90 \\
\hline & PC-SAFT & 2B & 0.730 & 15.93 & 20.92 & 10.19 & 47.60 & 1.47 & & & 16.14 & \\
\hline
\end{tabular}
\end{table}
${ }^{a}$ A. S.: association scheme. ${ }^{b}$ CP: critical point. ${ }^{c}$ Ave: average \%AAD for EOS.
the literature. ${ }^{62-64}$ Exploratory data analysis (EDA) ${ }^{65}$ has been employed to examine and validate all experimental data. The details of the experimental data selection technique, including collection, classification, comparison, validation, and weights, are described in our previous work. ${ }^{25}$

Due to the complexity of calculations for associating fluids such as alkanolamines, the association term of the SAFT-HR EOS is developed by applying some approximations. ${ }^{11}$ These approximations lead to different association schemes, ${ }^{11}$ and consequently, using each of the association schemes to estimate the pure-compound parameters will result in a different set of parameters. For the studied alkanolamines, namely, MEA, DEA, MDEA, and AMP, three association schemes ( $2 \mathrm{~B}, 3 \mathrm{~B}$, and $4 \mathrm{C}^{11}$ ) can be used for thermodynamic modeling using P $\rho$ T-SAFT-HR EOS. Therefore, to calculate the adjustable parameters of the P $\rho$ T-SAFT-HR EOS for MEA, DEA, MDEA, and AMP, the pressure objective function, as the dominant objective function in the parametrization of the P $\rho$ T-SAFT-HR EOS, ${ }^{25,66-71}$ has been calculated for each of these association schemes. Based on the pressure objective function $\left(O F_{P}\right)$ values presented in Table S2 of Supporting Information, the 2B association scheme was chosen for MEA and AMP , while the 3 B scheme was found most suitable for DEA and MDEA. After determining the appropriate association scheme for each alkanolamine, the parametrization process was carried out based on the calculation of pressure $\left(\mathrm{OF}_{p}\right)$, density $\left(\mathrm{OF}_{\rho}\right)$, temperature $\left(\mathrm{OF}_{T}\right)$, and total $(\mathrm{OF})$ objective functions for each compound. The parameter set that resulted in the minimum value of the total objective function was identified as the P $\rho$ T-SAFT-HR EOS parameters. A detailed description of the optimization methods and objective function calculation process can be found in our previous work. ${ }^{25}$ The numerical values of the P $\rho$ T-SAFT-HR EOS parameters for MEA, DEA, MDEA, and AMP are listed in Table 1. Having the P $\rho$ T-SAFT-HR EOS parameters for pure alkanolamines makes it possible to calculate the thermody-
namic properties of pure fluids and their binary and ternary mixtures over a wide range of temperatures and pressures and to compare their accuracy with experimental data.

The one-fluid van der Waals (vdWl) mixing rules ${ }^{59}$ and the Lorentz-Berthelot combining rules have been used to extend all three EOSs to mixtures and to perform calculations of binary and ternary mixtures: ${ }^{72}$

$$
\begin{align*}
& \overline{m^{2} u \sigma^{3}}=\sum_{i} \sum_{j} x_{i} x_{j} m_{i} m_{j}\left(\frac{u_{i j}}{k_{b} T}\right) \sigma_{i j}^{3}  \tag{5}\\
& \overline{m^{2} u^{2} \sigma^{3}}=\sum_{i} \sum_{j} x_{i} x_{j} m_{i} m_{j}\left(\frac{u_{i j}}{k_{b} T}\right)^{2} \sigma_{i j}^{3}  \tag{6}\\
& u_{i j}=\left(1-k_{i j}\right) \sqrt{u_{i i} u_{j j}}  \tag{7}\\
& \sigma_{i j}=\frac{\sigma_{i}+\sigma_{j}}{2} \tag{8}
\end{align*}
$$

where $k_{b}$ is Boltzmann constant; $m, u$, and $\sigma$ are EOS parameters; $u_{i j}$ and $\sigma_{i j}$ are cross-interaction parameters; and $k_{i j}$ is the binary interaction parameter and can be determined from experimental data.

\section*{3. RESULTS AND DISCUSSION}

Precise thermodynamic modeling of pure alkanolamines and mixtures containing them are an essential tool for the development of several industrial processes. ${ }^{35}$ To assess its suitability for this purpose, the performances of P $\rho$ T-SAFTHR, PC-SAFT, and SAFT-HR EOSs in predicting the thermodynamic properties of pure alkanolamines as well as binary and ternary mixtures containing alkanolamines are evaluated. The results are compared with the experimental data.

Predicting the thermodynamic properties of fluids with acceptable accuracy is one of the challenges of any equation of

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-04.jpg?height=846&width=1472&top_left_y=204&top_left_x=317}
\captionsetup{labelformat=empty}
\caption{Figure 1. Comparison of vapor pressure ( $P^{\text {sat }}$ ) predicted by the P $\rho$ T-SAFT-HR (solid lines), PC-SAFT (dashed lines), and SAFT-HR (dash-dotted lines) EOSs with literature experimental data ${ }^{77,78}$ for MEA (filled circle), DEA (filled square), MDEA (filled triangle), and AMP (filled diamond).}
\end{figure}
state. ${ }^{14,74}$ Therefore, based on the availability of experimental data, thermodynamic properties including density ( $\rho$ ), vaporliquid equilibrium (VLE), critical point (CP), and secondorder thermodynamic derivative properties have been calculated in this section. The Secant method was chosen as the numerical method for calculating roots of the EOS to determine properties such as density, except for the density calculations of ternary mixtures, where the Brent method ${ }^{75}$ was used to increase accuracy. The average absolute deviation percentage (\%AAD) is used to compare EOS results with experimental data:

$$
\begin{equation*}
\% \mathrm{AAD}=\frac{100}{N_{P}} \sum_{i=1}^{N_{p}}\left|\frac{Y_{i}^{\mathrm{cal}}-Y_{i}^{\exp }}{Y_{i}^{\exp }}\right| \tag{9}
\end{equation*}
$$

3.1. Pure Components. The results of predicting the thermodynamic properties of MEA, DEA, MDEA, and AMP, including density ( $\rho$ ), isobaric heat capacity ( $C_{P}$ ), sound velocity ( $u$ ), isobaric thermal expansivity ( $\alpha_{P}$ ) and isothermal compressibility ( $\kappa_{T}$ ), saturated vapor pressure ( $P^{\text {sat }}$ ), saturated liquid density ( $\rho_{\text {liq }}$ ), and CP using the P $\rho$ T-SAFT-HR, PCSAFT, and SAFT-HR EOSs are given in Table 2 and Tables S4 to S12 of the Supporting Information. Additionally, Table S3 summarizes the temperature and pressure ranges of the thermodynamic properties studied. As can be seen, the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR EOS has shown superior performance in predicting the thermodynamic properties of the studied alkanolamines compared to the other EOSs. These findings are consistent with previous studies that have demonstrated the effectiveness of $P \rho T$ versions of SAFT-type EOSs. ${ }^{25,45,67-71,76}$ Figure 1 and Tables S8 and S9 of the Supporting Information show the MEA, DEA, MDEA, and AMP vapor pressure prediction using the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT HR EOSs. The results show that all three EOSs accurately model the vapor pressure of the studied alkanolamines, with good agreement between the predicted values and the experimental data. ${ }^{77,78}$ These results for the P $\rho$ T-SAFT-HR EOS are interesting,
because no VLE data were used in the calculation of its parameters.

To assess the accuracy of the P $\rho$ T-SAFT-HR EOS predictions, the thermodynamic properties of the studied alkanolamines were also calculated using the SAFT-HR and PC-SAFT EOSs, and the results are reported in Table 2. As MEA is the primary absorbent in acid gas removal, more studies have been conducted to parametrize the SAFT-type equations and the pure-compound parameters of several versions of the SAFT models are available for MEA. Hence, the results of thermodynamic modeling using the P $\rho$ T-SAFTHR, PC-SAFT, ${ }^{32}$ and the SAFT-HR ${ }^{36}$ EOSs for MEA are compared with experimental data. The results of predicting the thermodynamic properties using P $\rho$ T-SAFT-HR and PCSAFT for DEA, MDEA, and AMP are also compared to the experimental data. As can be seen in Table 2, the results of the P $\rho$ T-SAFT-HR and PC-SAFT equations for predicting the thermodynamic properties of MEA, DEA, MDEA, and AMP show that they performed similarly in predicting density, saturated vapor pressure, saturated liquid density, and CP; however, in predicting the sound velocity, isobaric thermal expansivity, and isothermal compressibility, the $\mathrm{P} \rho \mathrm{T}$-SAFT EOS produced more accurate results. In predicting isobaric heat capacity, although the P $\rho$ T-SAFT-HR EOS has had acceptable results, the PC-SAFT EOS has demonstrated variable performance, yielding better results for DEA and MDEA but considerably poorer results for MEA and AMP. Also, comparing the performance of $\mathrm{P} \rho$ T-SAFT-HR and SAFT-HR equations in predicting the thermodynamic properties of MEA demonstrates that except for isobaric heat capacity, P $\rho$ T-SAFT-HR EOS has a better performance than SAFT-HR EOS in predicting other thermodynamic properties. In general, considering all the thermodynamic properties investigated in this section, it can be concluded that the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR EOS is not only able to properly predict thermodynamic properties for alkanolamines but also performs better than other versions of the SAFT EOS.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3. Results of Predicting the Thermodynamic Properties of the Investigated Alkanolamine Binary Mixtures Using P $\rho$ T-SAFT-HR, ${ }^{25}$ PC-SAFT, ${ }^{32}$ and SAFT-HR ${ }^{11}$ EOSs.}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[b]{2}{*}{binary mixtures} & \multirow[b]{2}{*}{EOS} & \multicolumn{6}{|c|}{\%AAD} & \multirow[b]{2}{*}{ave} & \multirow[b]{2}{*}{data source} \\
\hline & & $\rho$ & $u$ & $\boldsymbol{\alpha}_{P}$ & $\boldsymbol{\kappa}_{T}$ & VLE ( $\boldsymbol{x}_{\mathbf{2}}$ ) & VLE ( $\boldsymbol{y}_{\mathbf{2}}$ ) & & \\
\hline \multirow[t]{3}{*}{water (1) + MEA (2)} & P $\rho$ T-SAFT-HR & 0.645 & 2.59 & 18.53 & 10.98 & 1.84 & 0.16 & 5.79 & \multirow[t]{3}{*}{93-95} \\
\hline & SAFT-HR & 0.987 & 35.20 & 24.52 & 47.29 & 1.83 & 0.01 & 18.31 & \\
\hline & PC-SAFT & 1.288 & 33.43 & 26.03 & 49.48 & 1.15 & 0.01 & 18.56 & \\
\hline \multirow[t]{2}{*}{water (1) + MDEA (2)} & P $\rho$ T-SAFT-HR & 0.367 & 3.14 & 34.21 & 13.35 & & & 12.77 & \multirow[t]{2}{*}{63,94} \\
\hline & PC-SAFT & 1.010 & 31.32 & 21.43 & 48.69 & & & 25.61 & \\
\hline \multirow[t]{2}{*}{water (1) + DEA (2)} & P $\rho$ T-SAFT-HR & 0.833 & 4.13 & 9.24 & 44.13 & & & 14.58 & \multirow[t]{2}{*}{94,96} \\
\hline & PC-SAFT & 0.222 & 25.98 & 58.82 & 32.56 & & & 29.40 & \\
\hline \multirow[t]{2}{*}{water (1) + AMP (2)} & P $\rho$ T-SAFT-HR & 0.775 & & 15.89 & 10.76 & 1.24 & 0.03 & 5.74 & \multirow[t]{2}{*}{64,97} \\
\hline & PC-SAFT & 1.010 & & 32.61 & 47.07 & 0.76 & 0.04 & 16.30 & \\
\hline \multirow[t]{2}{*}{MEA (1) + MDEA (2)} & P $\rho$ T-SAFT-HR & 0.391 & 0.91 & & & & & 0.65 & \multirow[t]{2}{*}{80} \\
\hline & PC-SAFT & 1.498 & 6.66 & & & & & 4.08 & \\
\hline \multirow[t]{2}{*}{MEA (1) + AMP (2)} & P $\rho$ T-SAFT-HR & 0.390 & 0.63 & & & & & 0.51 & \multirow[t]{2}{*}{80} \\
\hline & PC-SAFT & 0.149 & 14.09 & & & & & 7.12 & \\
\hline \multirow[t]{3}{*}{MEA (1) + methanol (2)} & P $\rho$ T-SAFT-HR & 0.715 & & & & & & 0.72 & \multirow[t]{3}{*}{98} \\
\hline & SAFT-HR & 1.078 & & & & & & 1.08 & \\
\hline & PC-SAFT & 0.420 & & & & & & 0.42 & \\
\hline \multirow[t]{2}{*}{DEA (1) + methanol (2)} & P $\rho$ T-SAFT-HR & 0.600 & & & & & & 0.60 & \multirow[t]{2}{*}{99} \\
\hline & PC-SAFT & 0.565 & & & & & & 0.57 & \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-05.jpg?height=737&width=1491&top_left_y=1112&top_left_x=306}
\captionsetup{labelformat=empty}
\caption{Figure 2. Comparison of VLE predicted by the P $\rho$ T-SAFT-HR (solid lines), PC-SAFT (dashed lines), and SAFT-HR (dash-dotted lines) EOSs with literature experimental data ${ }^{95,97}$ for (a) water (1) + MEA (2) and (b) water (1) + AMP (2) binary mixtures.}
\end{figure}
3.2. Binary Mixtures. In recent years, a wide range of aqueous and nonaqueous alkanolamine solutions have been investigated and applied for the acid gas removal processes. Therefore, a practical thermodynamic model should be able to predict the thermodynamic properties such as phase behavior, density, and second-order thermodynamic derivative properties with acceptable accuracy. ${ }^{35,91}$ Due to the ability of generalization to mixtures using the pure-compound parameters and the relative independence of the experimental data of mixtures, ${ }^{92}$ EOSs are proper models for predicting the thermodynamic properties of alkanolamine mixtures. Previously, the performance of the P $\rho$ T-SAFT-HR EOS showed that it has good efficiency in predicting the thermodynamic properties of pure and binary mixtures of a wide range of systems. ${ }^{25,66,76}$ In this section, the performances of the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR, PC-SAFT, and SAFT-HR EOSs have been investigated in predicting the thermodynamic properties of
aqueous and nonaqueous alkanolamine binary mixtures including MEA + MDEA, MEA + AMP, MEA + methanol, DEA + methanol, and aqueous solutions of MEA, DEA, MDEA, and AMP. The studied thermodynamic properties are density ( $\rho$ ), sound velocity ( $u$ ), isobaric thermal expansivity ( $\alpha_{P}$ ) and isothermal compressibility ( $\kappa_{T}$ ), and VLE. These thermodynamic properties have been selected based on the availability of experimental data in the literature. To assess the relative performance of P $\rho$ T-SAFT-HR, PC-SAFT, and SAFTHR EOSs, the results are also compared to experimental data. For all mixture calculations, the vdW1 mixing rules without the binary interaction parameter ( $k_{i j}=0$ ) were applied to achieve fair comparisons in predictions. The results are reported in Table 3 and Tables S13-S21 of the Supporting Information. Furthermore, Table S3 provides an overview of the $T$ and $P$ ranges for the thermodynamic properties examined.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-06.jpg?height=1057&width=1579&top_left_y=199&top_left_x=262}
\captionsetup{labelformat=empty}
\caption{Figure 3. Comparison of sound velocity $(u)$ predicted by the P $\rho$ T-SAFT-HR (solid lines), PC-SAFT (dashed lines), and SAFT-HR (dash-dotted lines) EOSs with literature experimental data ${ }^{94}$ for (a) water (1) + MEA (2) and (b) water (1) + MDEA (2) binary mixtures at 298.15 (filled circle), 308.15 (filled square), and 318.15 K (filled triangle) and atmospheric pressure.}
\end{figure}

A brief comparison of the results in Table 3 shows that the P $\rho$ T-SAFT-HR EOS predicts the studied thermodynamic properties with the appropriate accuracy. The performances of P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs in modeling density and VLE have been in good agreement with the experimental data. Figure 2 presents the results of the EOSs for predicting the VLE of the binary mixtures. As can be seen in this figure, all three EOSs have shown good performance in predicting the VLE of aqueous solutions of MEA and AMP. Also, similar to the previous section, the performance of the P $\rho$ T-SAFT-HR EOS in predicting the sound velocity of binary systems was significantly better than those of PC-SAFT and SAFT-HR EOSs. This is significant because, on the one hand, sound velocity is calculated using the partial derivative of the Helmholtz free energy with respect to density and temperature, which is challenging for EOSs. On the other hand, highprecision measurement techniques are used for experimental sound velocity data, making it a valuable benchmark for evaluating thermodynamic models. ${ }^{25,100}$ Conversely, the SAFT-HR and PC-SAFT equations exhibited poor performance in predicting sound velocity for these binary mixtures. Figure 3 compares the predictions of $\mathrm{P} \rho$ T-SAFT-HR, SAFTHR, and PC-SAFT (Tables S17 and S18 of the Supporting Information) with experimental data ${ }^{94}$ for the sound velocity of water + MEA and water + DEA at various temperatures. As the figure shows, the P $\rho$ T-SAFT-HR EOS well predicted numerical values and the trend of changes in sound velocity with respect to the temperature and composition of aqueous MEA and DEA, and its results have good agreement with experimental data. On the other hand, SAFT-HR and PC-

SAFT equations exhibited poor performance in predicting sound velocity for these binary mixtures.
3.3. Ternary Mixtures. The aqueous solutions of MEA, DEA, MDEA, and AMP are currently the common industrial solvent for the acid gas removal process. ${ }^{101}$ However, there are challenges to the industrial application of these solvents. ${ }^{102}$ Therefore, achieving a higher-quality solvent is one of the important needs of industries related to the acid gas removal processes, so in addition to investigating the thermodynamic behavior of binary mixtures containing alkanolamines, thermodynamic modeling of their ternary mixtures is also one of the most up-to-date and practical research fields. ${ }^{103}$

Aqueous solutions of primary and tertiary alkanolamines or secondary and tertiary alkanolamines can combine the high reaction rate of primary and secondary alkanolamines with the high-equilibrium capacity of tertiary alkanolamines and improve the performance of the solvents. ${ }^{104}$ On the other hand, the use of other solvents along with water can be another suitable solution to improve the properties of alkanolaminebased solvents. One of the appropriate for use with water is methanol, and ternary mixtures of water, methanol, and alkanolamines are other developing absorbents for industrial use. This is because the presence of methanol as a physical solvent can improve the solubility capacity of the mixture. ${ }^{99}$

Experimental data on ternary mixtures of alkanolamines are more limited than for binary mixtures, particularly for properties other than density. ${ }^{99,103-105}$ This may be due to the importance of density data in industrial processes. ${ }^{106}$ Therefore, in this section, the performances of the P $\rho$ T-SAFTHR and PC-SAFT EOSs in the modeling of the density for five and VLE for one ternary mixture containing alkanolamines are

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4. Results of Predicting the Density of the Investigated Alkanolamine Ternary Mixtures Using the P $\boldsymbol{\rho} \mathbf{T}$-SAFT-HR ${ }^{\mathbf{2 5}}$ and PC-SAFT ${ }^{23}$ EOSs}
\begin{tabular}{|l|l|l|l|l|l|l|l|}
\hline \multirow[b]{2}{*}{ternary mixture} & \multirow[b]{2}{*}{EOS} & \%AAD & \multirow[b]{2}{*}{$\% w_{1}$} & \multirow[b]{2}{*}{$\% w_{2}$} & \multirow[b]{2}{*}{$T$ range, $\mathbf{K}$} & \multirow[b]{2}{*}{$P$ range, MPa} & \multirow[b]{2}{*}{data source} \\
\hline & & $\_\_\_\_$ & & & & & \\
\hline \multirow[t]{2}{*}{MDEA (1) + MEA (2) + water (3)} & P $\rho$ T-SAFT-HR & 0.892 & \multirow[t]{2}{*}{0-30} & \multirow[t]{2}{*}{0-30} & \multirow[t]{2}{*}{293-323} & \multirow[t]{2}{*}{0.1} & \multirow[t]{2}{*}{104} \\
\hline & PC-SAFT & 1.184 & & & & & \\
\hline \multirow[t]{2}{*}{AMP (1) + MEA (2) + water (3)} & P $\rho$ T-SAFT-HR & 1.223 & \multirow[t]{2}{*}{21-30} & \multirow[t]{2}{*}{0-9} & \multirow[t]{2}{*}{293-323} & \multirow[t]{2}{*}{0.1} & \multirow[t]{2}{*}{104,110} \\
\hline & PC-SAFT & 2.074 & & & & & \\
\hline \multirow[t]{2}{*}{MDEA (1) + DEA (2) + water (3)} & P $\rho$ T-SAFT-HR & 0.525 & \multirow[t]{2}{*}{10-30} & \multirow[t]{2}{*}{10-30} & \multirow[t]{2}{*}{293-393} & \multirow[t]{2}{*}{0.1-140} & \multirow[t]{2}{*}{103} \\
\hline & PC-SAFT & 0.980 & & & & & \\
\hline \multirow[t]{2}{*}{AMP (1) + DEA (2) + water (3)} & P $\rho$ T-SAFT-HR & 1.100 & \multirow[t]{2}{*}{21-28.5} & \multirow[t]{2}{*}{1.5-9} & \multirow[t]{2}{*}{293-323} & \multirow[t]{2}{*}{0.1} & \multirow[t]{2}{*}{104} \\
\hline & PC-SAFT & 1.947 & & & & & \\
\hline \multirow[t]{2}{*}{DEA (1) + methanol (2) + water (3)} & P $\rho$ T-SAFT-HR & 0.685 & \multirow[t]{2}{*}{20-50} & \multirow[t]{2}{*}{20-60} & \multirow[t]{2}{*}{283-333} & \multirow[t]{2}{*}{0.1} & \multirow[t]{2}{*}{99} \\
\hline & PC-SAFT & 2.913 & & & & & \\
\hline
\end{tabular}
\end{table}
studied and the results are compared with experimental data. Similar to the previous section, the binary interaction parameter is not applied in the ternary mixture calculations. Table 4 and Tables S22-S24 of the Supporting Information present the results for predicting the density of ternary mixtures using P $\rho$ T-SAFT-HR and PC-SAFT. As can be seen, the P $\rho$ T-SAFT-HR EOS has also performed well in predicting the density of ternary mixtures and the P $\rho$ T-SAFT-HR EOS appropriately predicted the numerical values of density as well as the trend of its changes with respect to temperature, pressure, and composition. Figures $4-6$ compare the predicted densities of ternary mixtures (Tables S22 to S24 of the Supporting Information) with experimental data. It is evident from these figures that the P $\rho$ T-SAFT-HR EOS exhibits good performance in predicting the trend of density changes with respect to temperature, pressure, and composition of ternary mixtures, resembling that of pure components and binary mixtures, and following the same trend. Moreover, results have shown that due to the increased complexity of the association term for ternary mixtures, ${ }^{107}$ the numerical methods used to calculate their density can also affect the accuracy and precision of the results. Although the secant method provides better numerical values for density, it exhibits variations in calculations and does not accurately predict the trend of density changes (Figure S1 of the Supporting Information). Therefore, the results of three other numerical root-finding methods, namely, Newton-Raphson, ${ }^{108}$ affine covariant Newton, ${ }^{109}$ and Brent, ${ }^{75}$ were investigated for a sample ternary mixture (MEA + AMP + water). The Brent method not only maintains computational accuracy but also accurately predicts the trend of density changes (Table S25 in the Supporting Information). Therefore, the Brent method was selected to calculate the density of ternary mixtures by using EOSs. However, although the P $\rho$ T-SAFT-HR EOS systematically performs better than the PC-SAFT EOS in predicting density, it still tends to overestimate the density. The accuracy of the results could be improved by incorporating binary interaction parameters.

These results demonstrate the capability of $\mathrm{P} \rho$ T-SAFT-HR EOS as a reliable tool for modeling the density of alkanolamine-based mixtures, including ternary systems, even without the need for binary interaction parameters. The improved accuracy in predicting mixture densities can be attributed to the incorporation of density data during the parametrization of the $\mathrm{P} \rho$ T-SAFT-HR EOS. This aligns with previous research highlighting the superior performance of $P \rho T$ variants of SAFT-type EOSs. ${ }^{25,45,67-71,76}$

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-07.jpg?height=1352&width=857&top_left_y=808&top_left_x=1084}
\captionsetup{labelformat=empty}
\caption{Figure 4. Comparison of density ( $\rho$ ) predicted by the P $\rho$ T-SAFT-HR (solid lines) and PC-SAFT (dashed lines) EOSs with literature experimental data ${ }^{104}$ for (a) MDEA (1) + MEA (2) + water (3), (b) AMP (1) + MEA (2) + water (3), and (c) AMP (1) + DEA (2) + water (3) ternary mixtures at 293.15 (filled circle), 298.15 (filled square), 303.15 (filled trianlge), 308.15 (filled diamond), 313.15 (open circle), 318.15 (open square), and 323.15 (open triangle) K and atmospheric pressure The mass fraction of water in all mixtures was constant $\left(\% w_{3}=70\right)$.}
\end{figure}

Figure 7 and Table 5 and Table S26 present the prediction results of the P $\rho$ T-SAFT-HR and PC-SAFT EOSs for the VLE

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-08.jpg?height=448&width=846&top_left_y=204&top_left_x=173}
\captionsetup{labelformat=empty}
\caption{Figure 5. Comparison of density ( $\rho$ ) predicted by the P $\rho$ T-SAFT-HR (solid lines) and PC-SAFT (dashed lines) EOSs with literature experimental data ${ }^{99}$ for DEA (1) + methanol (2) + water (3) ternary mixture at 283.15 (filled circle), 293.15 (filled square), 303.15 (filled triangle), 313.15 (filled diamond), 323.15 (open circle), and 333.15 (open square) K and atmospheric pressure. The mass fraction of DEA in all mixtures was constant $\left(\% w_{1}=20\right)$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-08.jpg?height=1146&width=846&top_left_y=955&top_left_x=173}
\captionsetup{labelformat=empty}
\caption{Figure 6. Comparison of density ( $\rho$ ) predicted by the P $\rho$ T-SAFT-HR (solid lines) and PC-SAFT (dashed lines) EOSs with literature experimental data ${ }^{103}$ for MDEA (1) + DEA (2) + water (3) ternary mixtures (a) $\% w_{1}=30$ and $\% w_{2}=10$, and (b) $\% w_{1}=10$ and $\% w_{2}=30$ at 293.15 (filled circle), 313.15 (filled square), 333.15 (filled triangle), 353.15 (filled diamond), 373.15 (open circle), and 393.15 (open square) K . The mass fraction of water in all of the mixtures was constant $\left(\% w_{3}=60\right)$.}
\end{figure}
of the MDEA + MEA + water ternary mixture. In Figure 7, the experimental K-factors ( $K_{F_{\mathrm{i}}}=y_{i} / x_{i}$ ) are compared with the predictions from the EOSs. As observed, both EOSs demonstrate good performance in predicting the VLE of the
ternary mixture. Considering that VLE data were not used in the parametrization process of the P $\rho$ T-SAFT-HR EOS, its superior performance compared to PC-SAFT EOS is noteworthy.

Consistent with its performance for pure components and binary mixtures, as can be seen in Figure 4, P $\rho$ T-SAFT-HR EOS accurately predicts the density of the ternary aqueous solutions of alkanolamines across varying temperatures, compositions, and even in the presence of cosolvents like methanol (Figure 5). Figure 6 further demonstrates this capability for the MDEA-DEA-water system, where the model effectively predicts the density over a wide pressure range ( $0.1-140 \mathrm{MPa}$ ) in addition to temperature and composition variations. Accurate prediction of the density of ternary aqueous solutions containing alkanolamines can be used in the design and development of new solvents for the acid gas removal process because the first step in this way is to have a model that predicts the thermodynamic properties of various mixtures with acceptable accuracy.

Overall, the P $\rho$ T-SAFT-HR EOS demonstrates remarkable capability in predicting a wide range of thermodynamic properties for pure, binary, and ternary mixtures of alkanolamines, as evident from the low overall \%AAD values in Figure 8. This figure shows the total average of all of the \%AAD values for the thermodynamic properties of all pure, binary, and ternary mixtures of alkanolamines predicted using the $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR, PC-SAFT, and SAFT-HR EOSs. Since the industrial use of alkanolamines is usually in aqueous or methanolic solutions, the promising results of the P $\rho$ T-SAFTHR EOS in the thermodynamic modeling of alkanolamine mixtures can help in the design and development of new solutions for acid gas removal processes.

\section*{4. CONCLUSIONS}

Due to the many industrial applications of alkanolamines and the importance of developing thermodynamic models for them, in this study, the performance of the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs in predicting the thermodynamic properties of pure alkanolamines and binary and ternary mixtures containing them was investigated. Pure-compound parameters for P $\rho$ T-SAFT-HR EOS were first determined for MEA, DEA, MDEA, and (AMP) applying $P \rho T$ data across a wide temperature and pressure range. Based on the parametrization results, the association scheme 2B for MEA and AMP and the association scheme 3 B for DEA and MDEA were selected. Then, based on the availability of experimental data, the thermodynamic properties of these pure alkanolamines, including density ( $\rho$ ), isobaric heat capacity ( $C_{P}$ ), sound velocity ( $u$ ), isobaric thermal expansivity ( $\alpha_{P}$ ) and isothermal compressibility ( $\kappa_{T}$ ), saturated vapor pressure ( $P^{\text {sat }}$ ), saturated liquid density ( $\rho_{\text {liq }}$ ), and CP, were modeled using the P $\rho \mathrm{T}$ -SAFT-HR, PC-SAFT, and SAFT-HR EOSs. The results of the calculations were then compared to the experimental data. The results demonstrated the superior performance of P $\rho$ T-SAFTHR for pure alkanolamine thermodynamic modeling. In the next step, the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs are extended to binary mixtures, and the thermodynamic properties of eight binary mixtures containing alkanolamines are modeled by applying them. In this section, the P $\rho$ T-SAFTHR EOS predicted the thermodynamic properties of eight binary mixtures containing alkanolamines (without applying the binary interaction parameter), and the results were reasonably accurate. Comparing the results of $\mathrm{P} \rho \mathrm{T}$-SAFT-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-09.jpg?height=759&width=1517&top_left_y=191&top_left_x=295}
\captionsetup{labelformat=empty}
\caption{Figure 7. Comparison of K-factor ( $K_{F}$ ) predicted by the P $\rho$ T-SAFT-HR (solid lines) and PC-SAFT (dashed lines) EOSs with literature experimental data ${ }^{105}$ for MDEA (1) + MEA (2) + water (3) ternary mixtures (a) MDEA and (b) MEA.}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5. Results of Predicting the VLE of MDEA + MEA + Water Ternary Mixtures Using the P $\rho$ T-SAFT-HR ${ }^{25}$ and PCSAFT ${ }^{23}$ EOSs}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[b]{2}{*}{ternary mixture} & \multirow[b]{2}{*}{EOS} & \multicolumn{5}{|c|}{\%AAD} & \multirow[b]{2}{*}{$T$ range, $\mathbf{K}$} & \multirow[b]{2}{*}{$P$ range, $\mathbf{k P a}$} & \multirow[b]{2}{*}{data source} \\
\hline & & $x_{1}$ & $\boldsymbol{x}_{\mathbf{2}}$ & $y_{1}$ & $y_{2}$ & ave & & & \\
\hline \multirow[t]{2}{*}{MDEA (1) + MEA (2) + water (3)} & P $\rho$ T-SAFT-HR & 1.16 & 0.84 & 0.0029 & 0.0108 & 0.50 & 313-473 & 5.98-90.30 & \multirow[t]{2}{*}{105} \\
\hline & PC-SAFT & 1.72 & 0.96 & 0.0565 & 0.0083 & 0.69 & & & \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-09.jpg?height=516&width=853&top_left_y=1375&top_left_x=169}
\captionsetup{labelformat=empty}
\caption{Figure 8. Total average \%AAD for predicting the thermodynamic properties of all investigated systems: four pure components, eight binary mixtures, and five ternary mixtures containing the alkanolamines, using the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR (based on the availability of parameters) EOSs.}
\end{figure}

HR, PC-SAFT, and SAFT-HR EOSs in predicting the thermodynamic properties of several binary mixtures also indicates the superiority of the P $\rho$ T-SAFT-HR EOS.

Finally, the density of five ternary mixtures containing alkanolamines, water, and methanol was predicted using $\mathrm{P} \rho \mathrm{T}$ -SAFT-HR and PC-SAFT. Additionally, the VLE of one ternary mixture was predicted using these models. The P $\rho$ T-SAFT-HR EOS demonstrated superior performance in predicting the properties of all five ternary mixtures compared to the PCSAFT EOS.

Overall, the P $\rho$ T-SAFT-HR EOS demonstrates the promising potential for the thermodynamic modeling of pure alkanolamines and their binary and ternary mixtures. Our
future work will focus on comparing P $\rho$ T-SAFT-HR with other models like SAFT-VR Mie, modeling the solubility of acid gases in aqueous and nonaqueous solutions of alkanolamines and extending the $\mathrm{P} \rho$ T-SAFT-HR EOS to other alkanolamine mixtures.
- ASSOCIATED CONTENT
(5) Supporting Information

The Supporting Information is available free of charge at https://pubs.acs.org/doi/10.1021/acs.jced.4c00390.

PC-SAFT and SAFT-HR EOSs parameters for the studied compounds; calculated pressure objective function $\left(O F_{P}\right)$ for $\mathrm{P} \rho$ T-SAFT-HR EOS applied to MEA, DEA, MDEA, and AMP with 2B, 3B, and 4C association schemes; temperature and pressure ranges of the thermodynamic properties studied; calculated thermodynamic properties for pure, binary, and ternary mixtures using the P $\rho$ T-SAFT-HR, PC-SAFT, and SAFT-HR EOSs; comparison of density predicted by the EOSs using secant method with other methods and literature experimental data for ternary mixtures (PDF)
- AUTHOR INFORMATION

Corresponding Author
Arash Pakravesh - Department of Physical Chemistry, Faculty of Chemistry and Petroleum Science, Bu-Ali Sina University, Hamedan 6517838695, Iran; © orcid.org/0000-0002-2860-504X; Phone: +98 8138282807;
Email: a.pakravesh@che.basu.ac.ir

\section*{Author}

Hosseinali Zarei - Department of Physical Chemistry, Faculty of Chemistry and Petroleum Science, Bu-Ali Sina University, Hamedan 6517838695, Iran; © orcid.org/0000-0001-6781-9019

Complete contact information is available at:
https://pubs.acs.org/10.1021/acs.jced.4c00390

\section*{Notes}

The authors declare no competing financial interest.

\section*{- ACKNOWLEDGMENTS}

The authors would like to thank Bu-Ali Sina University for providing the necessary facilities to carry out this research work.

\section*{REFERENCES}
(1) Jones, C.; Edens, M. R.; Lochary, J. F., Alkanolamines from Olefin Oxides and Ammonia. In Kirk-Othmer Encyclopedia of Chemical Technology; Wiley: 2004. doi: .
(2) Li, Y.; Luo, Y.; Wang, Z.; Zou, S.; Meng, X.; Liu, X. Enhancement of carbon bio-fixation and lipid accumulation in Coccomyxa subellipsoidea with triethanolamine CO 2 absorbent manipulation. Biochem. Eng. J. 2023, 198, No. 109018.
(3) Boro, M.; Verma, A. K.; Chettri, D.; Yata, V. K.; Verma, A. K. Strategies involved in biofuel production from agro-based lignocellulose biomass. Environmental Technology \& Innovation 2022, 28, No. 102679.
(4) Achinivu, E. C.; Frank, S.; Baral, N. R.; Das, L.; Mohan, M.; Otoupal, P.; Shabir, E.; Utan, S.; Scown, C. D.; Simmons, B. A.; Gladden, J. Alkanolamines as Dual Functional Solvents for Biomass Deconstruction and Bioenergy Production. Green Chem. 2021, 23 (21), 8611-8631.
(5) Hendriks, E.; Kontogeorgis, G. M.; Dohrn, R.; de Hemptinne, J.C.; Economou, I. G.; Zilnik, L. F.; Vesovic, V. Industrial Requirements for Thermodynamics and Transport Properties. Ind. Eng. Chem. Res. 2010, 49 (22), 11131-11141.
(6) Pahlavanzadeh, H.; Fakouri Baygi, S. Modeling CO2 solubility in Aqueous Methyldiethanolamine Solutions by Perturbed Chain-SAFT Equation of State. J. Chem. Thermodyn. 2013, 59, 214-221.
(7) MacDowell, N.; Florin, N.; Buchard, A.; Hallett, J.; Galindo, A.; Jackson, G.; Adjiman, C. S.; Williams, C. K.; Shah, N.; Fennell, P. An overview of CO2 capture technologies. Energy Environ. Sci. 2010, 3 (11), 1645-1669.
(8) Pereira, L. M. C.; Vega, L. F. A systematic approach for the thermodynamic modelling of CO 2 -amine absorption process using molecular-based models. Appl. Energy 2018, 232, 273-291.
(9) Chapman, W. G.; Gubbins, K. E.; Jackson, G.; Radosz, M. SAFT: Equation-of-state solution model for associating fluids. Fluid Phase Equilib. 1989, 52, 31-38.
(10) Chapman, W. G.; Gubbins, K. E.; Jackson, G.; Radosz, M. New reference equation of state for associating liquids. Ind. Eng. Chem. Res. 1990, 29 (8), 1709-1721.
(11) Huang, S. H.; Radosz, M. Equation of state for small, large, polydisperse, and associating molecules. Ind. Eng. Chem. Res. 1990, 29 (11), 2284-2294.
(12) Economou, I. G. Statistical Associating Fluid Theory: A Successful Model for the Calculation of Thermodynamic and Phase Equilibrium Properties of Complex Fluid Mixtures. Ind. Eng. Chem. Res. 2002, 41 (5), 953-962.
(13) Kontogeorgis, G. M.; Folas, G. K. Thermodynamic models for industrial applications: from classical and advanced mixing rules to association theories. John Wiley \& Sons 2009.
(14) Kontogeorgis, G. M.; Liang, X.; Arya, A.; Tsivintzelis, I. Equations of state in three centuries. Are we closer to arriving to a single model for all applications? Chem. Eng. Sci.: X 2020, 7, No. 100060.
(15) Cardenas, H.; Müller, E. A. Extension of the SAFT-VR-Mie equation of state for adsorption. J. Mol. Liq. 2019, 294, No. 111639.
(16) Polishuk, I.; Garrido, J. M. Comparison of SAFT-VR-Mie and CP-PC-SAFT in predicting phase behavior of associating systems I. Ammonia-water, methanol, ethanol and hydrazine. J. Mol. Liq. 2018, 265, 639-653.
(17) Wertheim, M. S. Fluids with highly directional attractive forces. I. Statistical thermodynamics. J. Stat. Phys. 1984, 35 (1), 19-34.
(18) Wertheim, M. S. Fluids with highly directional attractive forces. II. Thermodynamic perturbation theory and integral equations. J. Stat. Phys. 1984, 35 (1), 35-47.
(19) Wertheim, M. S. Fluids with highly directional attractive forces. III. Multiple attraction sites. J. Stat. Phys. 1986, 42 (3), 459-476.
(20) Wertheim, M. S. Fluids with highly directional attractive forces. IV. Equilibrium polymerization. J. Stat. Phys. 1986, 42 (3), 477-492.
(21) Blas, F. J.; Vega, L. F. Thermodynamic behaviour of homonuclear and heteronuclear Lennard-Jones chains with association sites from simulation and theory. Mol. Phys. 1997, 92 (1), 135150.
(22) Chen, J.; Mi, J.-g. Equation of state extended from SAFT with improved results for non-polar fluids across the critical point. Fluid Phase Equilib. 2001, 186 (1), 165-184.
(23) Gross, J.; Sadowski, G. Perturbed-Chain SAFT: An Equation of State Based on a Perturbation Theory for Chain Molecules. Ind. Eng. Chem. Res. 2001, 40 (4), 1244-1260.
(24) Lafitte, T.; Apostolakou, A.; Avendaño, C.; Galindo, A.; Adjiman, C. S.; Müller, E. A.; Jackson, G. Accurate statistical associating fluid theory for chain molecules formed from Mie segments. J. Chem. Phys. 2013, 139 (15), No. 154504.
(25) Pakravesh, A.; Zarei, F.; Zarei, H. P $\rho \mathrm{T}$ parameterization of SAFT equation of state: developing a new parameterization method for equations of state. Fluid Phase Equilib. 2021, 538, No. 113024.
(26) Bahamon, D.; Alkhatib, I. I. I.; Alkhatib, N.; Builes, S.; Sinnokrot, M.; Vega, L. F. A Comparative Assessment of Emerging Solvents and Adsorbents for Mitigating CO2 Emissions From the Industrial Sector by Using Molecular Modeling Tools. Front. Energy Res. 2020, 8 (165), 165.
(27) Button, J. K.; Gubbins, K. E. SAFT prediction of vapour-liquid equilibria of mixtures containing carbon dioxide and aqueous monoethanolamine or diethanolamine. Fluid Phase Equilib. 1999, 158-160, 175-181.
(28) Sengers, J. V.; Kayser, R. F.; Peters, C. J.; White, H. J., Jr. Equations of state for fluids and fluid mixtures. Elsevier: 2000.
(29) Moine, E.; Piña-Martinez, A.; Jaubert, J.-N.; Sirjean, B.; Privat, R. I-PC-SAFT: An Industrialized Version of the Volume-Translated PC-SAFT Equation of State for Pure Components, Resulting from Experience Acquired All through the Years on the Parameterization of SAFT-Type and Cubic Models. Ind. Eng. Chem. Res. 2019, 58 (45), 20815-20827.
(30) Polishuk, I. Standardized Critical Point-Based Numerical Solution of Statistical Association Fluid Theory Parameters: The Perturbed Chain-Statistical Association Fluid Theory Equation of State Revisited. Ind. Eng. Chem. Res. 2014, 53 (36), 14127-14141.
(31) Liang, X.; Maribo-Mogensen, B.; Thomsen, K.; Yan, W.; Kontogeorgis, G. M. Approach to Improve Speed of Sound Calculation within PC-SAFT Framework. Ind. Eng. Chem. Res. 2012, 51 (45), 14903-14914.
(32) Nasrifar, K.; Tafazzol, A. H. Vapor-Liquid Equilibria of Acid Gas-Aqueous Ethanolamine Solutions Using the PC-SAFT Equation of State. Ind. Eng. Chem. Res. 2010, 49 (16), 7620-7630.
(33) Mac Dowell, N.; Llovell, F.; Adjiman, C. S.; Jackson, G.; Galindo, A. Modeling the Fluid Phase Behavior of Carbon Dioxide in Aqueous Solutions of Monoethanolamine Using Transferable Parameters with the SAFT-VR Approach. Ind. Eng. Chem. Res. 2010, 49 (4), 1883-1899.
(34) Rodriguez, J.; Mac Dowell, N.; Llovell, F.; Adjiman, C. S.; Jackson, G.; Galindo, A. Modelling the fluid phase behaviour of aqueous mixtures of multifunctional alkanolamines and carbon
dioxide using transferable parameters with the SAFT-VR approach. Mol. Phys. 2012, 110 (11-12), 1325-1348.
(35) Pereira, L. M. C.; Llovell, F.; Vega, L. F. Thermodynamic characterisation of aqueous alkanolamine and amine solutions for acid gas processing by transferable molecular models. Appl. Energy 2018, 222, 687-703.
(36) Najafloo, A.; Zarei, S. Modeling solubility of CO2 in aqueous monoethanolamine (MEA) solution using SAFT-HR equation of state. Fluid Phase Equilib. 2018, 456, 25-32.
(37) Ayad, A.; Belabbaci, A.; Negadi, A.; Hernández, A.; Kabane, B.; Bahadur, I.; Mohammad, F.; Soleiman, A. A.; Negadi, L. Measurements and Modeling of Thermodynamic Properties of Binary Systems Comprising (2-Amino-2-methyl-1-propanol with Acetonitrile, Toluene, 1-Pentanol or 1-Hexanol) at Different Temperatures. J. Chem. Eng. Data 2023, 68 (11), 2789-2806.
(38) Zhang, Y.; Chen, C.-C. Thermodynamic Modeling for CO2 Absorption in Aqueous MDEA Solution with Electrolyte NRTL Model. Ind. Eng. Chem. Res. 2011, 50 (1), 163-175.
(39) Fakouri Baygi, S.; Pahlavanzadeh, H. Application of the perturbed chain-SAFT equation of state for modeling CO2 solubility in aqueous monoethanolamine solutions. Chem. Eng. Res. Des. 2015, 93, 789-799.
(40) Esmaeili, A.; Liu, Z.; Xiang, Y.; Yun, J.; Shao, L. Modeling and validation of carbon dioxide absorption in aqueous solution of piperazine + methyldiethanolamine by PC-SAFT and E-NRTL models in a packed bed pilot plant: Study of kinetics and thermodynamics. Process Saf. Environ. Prot. 2020, 141, 95-109.
(41) Moosavi, M.; Sisco, C. J.; Rostami, A. A.; Vargas, F. M. Thermodynamic properties and CO2 solubility of monoethanolamine + diethylenetriamine/aminoethylethanolamine mixtures: Experimental measurements and thermodynamic modeling. Fluid Phase Equilib.
2017, 449, 175-185.
(42) Yazdi, A.; Najafloo, A.; Sakhaeinia, H. A method for thermodynamic modeling of H2S solubility using PC-SAFT equation of state based on a ternary solution of water, methyldiethanolamine and hydrogen sulfide. J. Mol. Liq. 2020, 299, No. 112113.
(43) Tafazzol, A. H.; Nasrifar, K. Thermophysical properties of associating fluids in natural gas industry using PC-SAFT equation of state. Chem. Eng. Commun. 2011, 198 (10), 1244-1262.
(44) Gharehzadeh Shirazi, S.; Shahabadi, S.; Shekaari, H.; Golmohammadi, B. Thermodynamic Properties of Binary Mixtures Containing Ionic Liquid 1-Butyl-3-methylimidazolium Thiocyanate and Ethanolamines at Different Temperatures: Measurement and PCSAFT Modeling. J. Chem. Eng. Data 2023, 68 (12), 3126-3134.
(45) Mokhtari, Z.; Najafi, M.; Zarei, H. P $\rho$ T Measurements of 3-aminopropan-1-ol and N-(2-hydroxyethyl)morpholine from (293.15 to 473.15 ) K and up to 40 MPa and modeling with modified Tait and PC-SAFT Equations. Fluid Phase Equilib. 2024, 584, No. 114141.
(46) Mac Dowell, N.; Samsatli, N. J.; Shah, N. Dynamic modelling and analysis of an amine-based post-combustion CO2 capture absorption column. Int. J. Greenh. Gas Control 2013, 12, 247-258.
(47) Chremos, A.; Forte, E.; Papaioannou, V.; Galindo, A.; Jackson, G.; Adjiman, C. S. Modelling the phase and chemical equilibria of aqueous solutions of alkanolamines and carbon dioxide using the SAFT- $\gamma$ SW group contribution approach. Fluid Phase Equilib. 2016, 407, 280-297.
(48) Haslam, A. J.; González-Pérez, A.; Di Lecce, S.; Khalit, S. H.; Perdomo, F. A.; Kournopoulos, S.; Kohns, M.; Lindeboom, T.; Wehbe, M.; Febra, S.; Jackson, G.; Adjiman, C. S.; Galindo, A. Expanding the Applications of the SAFT- $\gamma$ Mie Group-Contribution Equation of State: Prediction of Thermodynamic Properties and Phase Behavior of Mixtures. J. Chem. Eng. Data 2020, 65 (12), 58625890.
(49) Perdomo, F. A.; Khalit, S. H.; Graham, E. J.; Tzirakis, F.; Papadopoulos, A. I.; Tsivintzelis, I.; Seferlis, P.; Adjiman, C. S.; Jackson, G.; Galindo, A. A predictive group-contribution framework for the thermodynamic modelling of CO2 absorption in cyclic amines, alkyl polyamines, alkanolamines and phase-change amines: New data
and SAFT- $\gamma$ Mie parameters. Fluid Phase Equilib. 2023, 566, No. 113635.
(50) Schulze-Hulbe, A.; Shaahmadi, F.; Burger, A. J.; Cripwell, J. T. Toward Nonaqueous Alkanolamine-Based Carbon Capture Systems: Parameterizing Amines, Secondary Alcohols, and Carbon DioxideContaining Systems in s-SAFT- $\gamma$ Mie. Ind. Eng. Chem. Res. 2023, 62 (35), 14061-14083.
(51) Alkhatib, I. I. I.; Pereira, L. M. C.; Vega, L. F. 110th Anniversary: Accurate Modeling of the Simultaneous Absorption of H 2 S and CO 2 in Aqueous Amine Solvents. Ind. Eng. Chem. Res. 2019, 58 (16), 6870-6886.
(52) Lloret, J. O.; Vega, L. F.; Llovell, F. A consistent and transferable thermodynamic model to accurately describe CO 2 capture with monoethanolamine. J. CO2 Util. 2017, 21, 521-533.
(53) Rozmus, J.; de Hemptinne, J.-C.; Ferrando, N.; Mougin, P. Long chain multifunctional molecules with GC-PPC-SAFT: Limits of data and model. Fluid Phase Equilib. 2012, 329, 78-85.
(54) Avlund, A. S.; Eriksen, D. K.; Kontogeorgis, G. M.; Michelsen, M. L. Application of association models to mixtures containing alkanolamines. Fluid Phase Equilib. 2011, 306 (1), 31-37.
(55) Najafloo, A.; Zoghi, A. T.; Feyzi, F. Measuring solubility of carbon dioxide in aqueous blends of N -methyldiethanolamine and 2-((2-aminoethyl)amino)ethanol at low CO2 loadings and modelling by electrolyte SAFT-HR EoS. J. Chem. Thermodyn. 2015, 82, 143155.
(56) Bülow, M.; Gerek Ince, N.; Hirohama, S.; Sadowski, G.; Held, C. Predicting Vapor-Liquid Equilibria for Sour-Gas Absorption in Aqueous Mixtures of Chemical and Physical Solvents or Ionic Liquids with ePC-SAFT. Ind. Eng. Chem. Res. 2021, 60 (17), 6327-6336.
(57) Uyan, M.; Sieder, G.; Ingram, T.; Held, C. Predicting CO2 solubility in aqueous N-methyldiethanolamine solutions with ePCSAFT. Fluid Phase Equilib. 2015, 393, 91-100.
(58) Wangler, A.; Sieder, G.; Ingram, T.; Heilig, M.; Held, C. Prediction of CO2 and H2S solubility and enthalpy of absorption in reacting N-methyldiethanolamine /water systems with ePC-SAFT. Fluid Phase Equilib. 2018, 461, 15-27.
(59) Huang, S. H.; Radosz, M. Equation of state for small, large, polydisperse, and associating molecules: extension to fluid mixtures. Ind. Eng. Chem. Res. 1991, 30 (8), 1994-2005.
(60) Gross, J.; Sadowski, G. Application of the Perturbed-Chain SAFT Equation of State to Associating Systems. Ind. Eng. Chem. Res. 2002, 41 (22), 5510-5515.
(61) Ramírez-Vélez, N.; Piña-Martinez, A.; Jaubert, J.-N.; Privat, R. Parameterization of SAFT Models: Analysis of Different Parameter Estimation Strategies and Application to the Development of a Comprehensive Database of PC-SAFT Molecular Parameters. J. Chem. Eng. Data 2020, 65 (12), 5920-5932.
(62) Scholz, C. W.; Span, R. Measurement of the ( $\mathrm{p}, \rho, \mathrm{T}$ ) Behavior of Liquid MEA and DEA at Temperatures from (293.15 to 423.15) K and Pressures up to 90 MPa . Int. J. Thermophys. 2021, 42 (5), 70.
(63) Zúniga-Moreno, A.; Galicia-Luna, L. A.; Bernal-García, J. M.; Iglesias-Silva, G. A. Densities, Excess Molar Volumes, Isothermal Compressibilities, and Isobaric Thermal Expansivities of the NMethyldiethanolamine (1) + Water (2) System at Temperatures between ( 313 and 363) K and Pressures up to 20 MPa . J. Chem. Eng. Data 2007, 52 (5), 1988-1995.
(64) Zúñiga-Moreno, A.; Galicia-Luna, L. A.; Bernal-García, J. M.; Iglesias-Silva, G. A. Densities and Derived Thermodynamic Properties of 2-Amino-2-methyl-1-propanol + Water Mixtures at Temperatures from ( 313 to 363) K and Pressures up to 24 MPa . J. Chem. Eng. Data 2008, 53 (1), 100-107.
(65) NIST/SEMATECH e-handbook of statistical methods. 2012. doi:
(66) Pakravesh, A.; Zarei, H. On the Effect of the Hard-sphere Term on the Statistical Associating Fluid Theory Equation of State. Phys. Chem. Res. 2022, 10 (1), 45-56.
(67) Paknejad, A.; Mohammadkhani, R.; Zarei, H. Experimental High-Temperature, High-Pressure Density Measurement and Per-turbed-Chain Statistical Associating Fluid Theory Modeling of

Dimethyl Sulfoxide, Isoamyl Acetate, and Benzyl Alcohol. J. Chem. Eng. Data 2019, 64 (12), 5174-5184.
(68) Zarei, H.; Asl, S. M. Thermodynamic properties and sPC-SAFT modeling of 2-ethoxyethanol, 2-propoxyethanol and 2-butoxyethanol from $\mathrm{T}=(293.15-413.15) \mathrm{K}$ and pressure up to 30 MPa . Fluid Phase Equilib. 2018, 457, 52-61.
(69) Mohammadkhani, R.; Paknejad, A.; Zarei, H. Thermodynamic Properties of Amines under High Temperature and Pressure: Experimental Results Correlating with a New Modified Tait-like Equation and PC-SAFT. Ind. Eng. Chem. Res. 2018, 57 (49), 1697816988.
(70) Zarei, H.; Keley, V. P $\rho \mathrm{T}$ measurement and PC-SAFT modeling of N,N-dimethyl formamide, N -methyl formamide, N,N-dimethyl acetamide, and ethylenediamine from $\mathrm{T}=(293.15-423.15) \mathrm{K}$ and pressures up to 35 MPa . Fluid Phase Equilib. 2016, 427, 583-593.
(71) Mokhtari, Z.; Pakravesh, A.; Zarei, H. High-pressure densities of 2-(dimethylamino) ethanol and 2-(diethylamino) ethanol: Measurement and modeling with new modified Tait and PC-SAFT equations of state. Fluid Phase Equilib. 2023, 572, No. 113825.
(72) Yan, W.; Varzandeh, F.; Stenby, E. H. PVT modeling of reservoir fluids using PC-SAFT EoS and Soave-BWR EoS. Fluid Phase Equilib. 2015, 386, 96-124.
(73) Linstrom, P. J.; Mallard, W. G. NIST chemistry WebBook, NIST standard reference database number 69; National Institute of Standards and Technology: Gaithersburg MD, 20899. In 2023.
(74) Wilhelmsen, Ø.; Aasen, A.; Skaugen, G.; Aursand, P.; Austegard, A.; Aursand, E.; Gjennestad, M. A.; Lund, H.; Linga, G.; Hammer, M. Thermodynamic Modeling with Equations of State: Present Challenges with Established Methods. Ind. Eng. Chem. Res. 2017, 56 (13), 3503-3515.
(75) Brent, R. P. Algorithms for Minimization Without Derivatives. Dover Publications Inc., 2013.
(76) Pakravesh, A.; Zarei, H. Prediction of Joule-Thomson coefficients and inversion curves of natural gas by various equations of state. Cryogenics 2021, 118, No. 103350.
(77) Avlund, A. S.; Kontogeorgis, G. M.; Michelsen, M. L. Modeling Systems Containing Alkanolamines with the CPA Equation of State. Ind. Eng. Chem. Res. 2008, 47 (19), 7441-7446.
(78) Klepáčová, K.; Huttenhuis, P. J. G.; Derks, P. W. J.; Versteeg, G. F. Vapor Pressures of Several Commercially Used Alkanolamines. J. Chem. Eng. Data 2011, 56 (5), 2242-2248.
(79) Mundhwa, M.; Henni, A. Molar Heat Capacity of Various Aqueous Alkanolamine Solutions from 303.15 to 353.15 K. J. Chem. Eng. Data 2007, 52 (2), 491-498.
(80) Álvarez, E.; Cerdeira, F.; Gómez-Diaz, D.; Navaza, J. M. Density, Speed of Sound, Isentropic Compressibility, and Excess Volume of (Monoethanolamine + 2-Amino-2-methyl-1-propanol), (Monoethanolamine + Triethanolamine), and (Monoethanolamine + N-Methyldiethanolamine) at Temperatures from (293.15 to 323.15) K. J. Chem. Eng. Data 2010, 55 (2), 994-999.
(81) Wang, X.; Yang, F.; Gao, Y.; Liu, Z. Volumetric properties of binary mixtures of dimethyl sulfoxide with amines from ( 293.15 to 363.15)K. J. Chem. Thermodyn. 2013, 57, 145-151.
(82) Blanco, A.; García-Abuín, A.; Gómez-Díaz, D.; Navaza, J. M.; Villaverde, Ó. L. Density, Speed of Sound, Viscosity, Surface Tension, and Excess Volume of N-Ethyl-2-pyrrolidone + Ethanolamine (or Diethanolamine or Triethanolamine) from $\mathrm{T}=(293.15$ to 323.15$) \mathrm{K}$. J. Chem. Eng. Data 2013, 58 (3), 653-659.
(83) García-Abuín, A.; Gómez-Díaz, D.; La Rubia, M. D.; Navaza, J. M. Density, Speed of Sound, Viscosity, Refractive Index, and Excess Volume of N-Methyl-2-pyrrolidone + Ethanol (or Water or Ethanolamine) from $\mathrm{T}=(293.15$ to 323.15$)$ K. J. Chem. Eng. Data 2011, 56 (3), 646-651.
(84) Chiu, L.-F.; Liu, H.-F.; Li, M.-H. Heat Capacity of Alkanolamines by Differential Scanning Calorimetry. J. Chem. Eng. Data 1999, 44 (3), 631-636.
(85) Haynes, W. M.; Lide, D. R.; Bruno, T. J. CRC Handbook of Chemistry and Physics, 97th edn, Vol. 2016-2017. CRC Press: 2016. DOI:
(86) Álvarez, E.; Cerdeira, F.; Gómez-Diaz, D.; Navaza, J. M. Density, Speed of Sound, Isentropic Compressibility, and Excess Volume of Binary Mixtures of 1-Amino-2-propanol or 3-Amino-1propanol with 2-Amino-2-methyl-1-propanol, Diethanolamine, or Triethanolamine from ( 293.15 to 323.15 ) K. J. Chem. Eng. Data 2010, 55 (7), 2567-2575.
(87) Chen, Y.-J.; Shih, T.-W.; Li, M.-H. Heat Capacity of Aqueous Mixtures of Monoethanolamine with N-Methyldiethanolamine. J. Chem. Eng. Data 2001, 46 (1), 51-55.
(88) García-Abuín, A.; Gómez-Díaz, D.; La Rubia, M. D.; Navaza, J. M.; Pacheco, R. Density, Speed of Sound, and Isentropic Compressibility of Triethanolamine (or N-Methyldiethanolamine) + Water + Ethanol Solutions from $\mathrm{t}=\left(15\right.$ to 50) ${ }^{\circ}$ C. J. Chem. Eng. Data 2009, 54 (11), 3114-3117.
(89) Zhang, K.; Hawrylak, B.; Palepu, R.; Tremaine, P. R. Thermodynamics of aqueous amines: excess molar heat capacities, volumes, and expansibilities of \{water+ methyldiethanolamine (MDEA)\} and \{water + 2-amino-2-methyl-1-propanol (AMP)\}. J. Chem. Thermodyn. 2002, 34 (5), 679-710.
(90) Chen, Y.-J.; Li, M.-H. Heat Capacity of Aqueous Mixtures of Monoethanolamine with 2-Amino-2-methyl-1-propanol. J. Chem. Eng. Data 2001, 46 (1), 102-106.
(91) Rochelle, G. T. Amine Scrubbing for CO2 Capture. Science 2009, 325 (5948), 1652-1654.
(92) Goodwin, A. R.; Sengers, J.; Peters, C. J.; Browarzik, D.; Trusler, J. P. M.; Economou, I. G.; Ely, J.; McCabe, C.; Galindo, A.; Anisimov, M. A.; Koon, M. C.; Lemmon, E.; Bottini, S.; Brignole, E.; Pereda, S.; Kjelstrup, S.; Bedeaux, D.; Sandler, S. I.; Letcher, T. M.; Weir, R.; Renner, T. Applied thermodynamics of fluids. Royal Society of Chemistry: Cambridge, UK, 2010.
(93) Sobrino, M.; Concepción, E. I.; Gómez-Hernández, Á.; Martín, M. C.; Segovia, J. J. Viscosity and density measurements of aqueous amines at high pressures: MDEA-water and MEA-water mixtures for CO2 capture. J. Chem. Thermodyn. 2016, 98, 231-241.
(94) Hawrylak, B.; Burke, S. E.; Palepu, R. Partial Molar and Excess Volumes and Adiabatic Compressibilities of Binary Mixtures of Ethanolamines with Water. J. Solution Chem. 2000, 29 (6), 575-594.
(95) Cai, Z.; Xie, R.; Wu, Z. Binary Isobaric Vapor-Liquid Equilibria of Ethanolamines + Water. J. Chem. Eng. Data 1996, 41 (5), 1101-1103.
(96) Concepción, E. I.; Gómez-Hernández, Á.; Martín, M. C.; Segovia, J. J. Density and viscosity measurements of aqueous amines at high pressures: DEA-water, DMAE-water and TEA-water mixtures. J. Chem. Thermodyn. 2017, 112, 227-239.
(97) Pappa, G. D.; Anastasi, C.; Voutsas, E. C. Measurement and thermodynamic modeling of the phase equilibrium of aqueous 2-amino-2-methyl-1-propanol solutions. Fluid Phase Equilib. 2006, 243 (1), 193-197.
(98) Yang, F.; Wang, X.; Wang, W.; Liu, Z. Densities and Excess Properties of Primary Amines in Alcoholic Solutions. J. Chem. Eng. Data 2013, 58 (3), 785-791.
(99) Yang, F.; Wang, X.; Liu, Z. Volumetric properties of binary and ternary mixtures of bis(2-hydroxyethyl)amine with water, methanol, ethanol from ( 278.15 to 353.15 )K. Thermochim. Acta 2012, 533, 1-9.
(100) Polishuk, I.; Perel, A. Implementation of PC-SAFT and SAFT +Cubic for modeling thermodynamic properties of eight 1-alkenes and their mixtures. J. Chem. Thermodyn. 2012, 54, 155-164.
(101) Aghel, B.; Sahraie, S.; Heidaryan, E. Carbon dioxide desorption from aqueous solutions of monoethanolamine and diethanolamine in a microchannel reactor. Sep. Purif. Technol. 2020, 237, No. 116390.
(102) Adeosun, A.; Abu-Zahra, M. R. M. Evaluation of amine-blend solvent systems for $\mathrm{CO2}$ post-combustion capture applications. Energy Procedia 2013, 37, 211-218.
(103) Concepción, E. I.; Moreau, A.; Carmen Martín, M.; VegaMaza, D.; Segovia, J. J. Density and viscosity of aqueous solutions of Methyldiethanolamine (MDEA) + Diethanolamine (DEA) at high pressures. J. Chem. Thermodyn. 2020, 148, No. 106141.
(104) Mandal, B. P.; Kundu, M.; Bandyopadhyay, S. S. Density and Viscosity of Aqueous Solutions of (N-Methyldiethanolamine + Monoethanolamine), (N-Methyldiethanolamine + Diethanolamine), (2-Amino-2-methyl-1-propanol + Monoethanolamine), and (2-Amino-2-methyl-1-propanol + Diethanolamine). J. Chem. Eng. Data 2003, 48 (3), 703-707.
(105) Kim, I.; Svendsen, H. F.; Børresen, E. Ebulliometric Determination of Vapor-Liquid Equilibria for Pure Water, Monoethanolamine, N-Methyldiethanolamine, 3-(Methylamino)-propylamine, and Their Binary and Ternary Solutions. J. Chem. Eng. Data 2008, 53 (11), 2521-2531.
(106) Fehlauer, H.; Wolf, H. Density reference liquids certified by the Physikalisch-Technische Bundesanstalt. Meas. Sci. Technol. 2006, 17 (10), 2588-2592.
(107) Tan, S. P.; Adidharma, H.; Radosz, M. Generalized Procedure for Estimating the Fractions of Nonbonded Associating Molecules and Their Derivatives in Thermodynamic Perturbation Theory. Ind. Eng. Chem. Res. 2004, 43 (1), 203-208.
(108) Abramowitz, M.; Stegun, I. A. Handbook of mathematical functions with formulas, graphs, and mathematical tables. US Government printing office, 1968; Vol. 55.
(109) Deuflhard, P. Newton methods for nonlinear problems: affine invariance and adaptive algorithms. Springer Science \& Business Media 2011; Vol. 35.
(110) Karunarathne, S. S.; Eimer, D. A.; Øi, L. E. Density, viscosity and free energy of activation for viscous flow of CO2 loaded 2-amino-2-methyl-1-propanol (AMP), monoethanol amine (MEA) and H 2 O mixtures. J. Mol. Liq. 2020, 311, No. 113286.
![](https://cdn.mathpix.com/cropped/de80abf0-d2ba-47ba-8fce-765b7bba28a8-13.jpg?height=1129&width=841&top_left_y=1503&top_left_x=1095)