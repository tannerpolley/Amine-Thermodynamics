\title{
Prediction of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ solubility and enthalpy of absorption in reacting N-methyldiethanolamine / water systems with ePC-SAFT
}

\author{
Anton Wangler ${ }^{\mathrm{a}}$, Georg Sieder ${ }^{\mathrm{b}}$, Thomas Ingram ${ }^{\mathrm{b}}$, Manfred Heilig ${ }^{\mathrm{b}}$, Christoph Held ${ }^{\mathrm{a}, *}$ \\ ${ }^{\mathrm{a}}$ Laboratory of Thermodynamics, Department of Biochemical and Chemical Engineering, Technische Universität Dortmund, Emil-Figge-Str. 70, 44227 Dortmund, Germany \\ ${ }^{\mathrm{b}}$ BASF SE, GCP/TD-L540, 67056 Ludwigshafen, Germany
}

\section*{ARTICLE INFO}

\section*{Article history:}

Received 24 June 2017
Received in revised form 8 December 2017
Accepted 23 December 2017
Available online 29 December 2017

\section*{Keywords:}

Electrolytes
Thermodynamics
Activity coefficients
Reaction equilibrium
MDEA

\begin{abstract}
The major goal of this work was the prediction of the solubility of $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ in aqueous methyldiethanolamine (MDEA) reacting systems using the electrolyte equation of state ePC-SAFT with focus on MDEA weight fractions $\mathrm{w}_{\text {MDEA }}>0.3$ (related to the binary water/MDEA system). Predictions in this work mean that no parameters were adjusted to the experimental gas solubility data in aqueous MDEA solutions. In order to obtain improved prediction results compared to state-of-the-art literature models, binary interaction parameters $\mathrm{k}_{\mathrm{ij}}$ between water- $\mathrm{MDEAH}^{+}$, water- $\mathrm{HCO}_{3}^{-}$, and water- $\mathrm{HS}^{-}$were introduced; these $\mathrm{k}_{\mathrm{ij}}$ values were fitted to osmotic-coefficient data measured in this work and from literature. This new possibility to access these $\mathrm{k}_{\mathrm{ij}}$ parameters allowed improved predictions of $\mathrm{CO}_{2}$ solubility, and the predictions were validated by new experimental data at $\mathrm{w}_{\text {MDEA }}=0.6$. Even more, the influence of the inert gas $\mathrm{CH}_{4}$ on $\mathrm{CO}_{2}$ solubility was predicted reasonably correct. Further, the solubility of $\mathrm{H}_{2} \mathrm{~S}$ in aqueous MDEA solutions was accurately predicted in the temperature range $298 \mathrm{~K}<\mathrm{T}<393 \mathrm{~K}$ at $\mathrm{w}_{\text {MDEA }}=0.32$ and 0.48 . In the final part of this work enthalpy of absorption was predicted for $353 \mathrm{~K}<\mathrm{T}<393 \mathrm{~K}$ at $\mathrm{w}_{\text {MDEA }}=0.3$ for varying gas loadings. In summary, prediction results were satisfying considering the fact that ePC-SAFT parameters were fitted only to experimental data of pure fluids or binary systems.
\end{abstract}
© 2018 Elsevier B.V. All rights reserved.

\section*{1. Introduction}

Global-warming-induced new challenges have arisen for the reduction of carbon dioxide ( $\mathrm{CO}_{2}$ ) in the atmosphere over the past decade [1,2]. While the removal of $\mathrm{CO}_{2}$ is the main goal of newly developed methods in process engineering, many exhaust gas streams in chemical engineering consist of more than just one hazardous gas. Hydrogen sulfide ( $\mathrm{H}_{2} \mathrm{~S}$ ) for example is a toxic gas, which is a byproduct during the ammonium and petroleum production [3]. Additionally, inert gases such as methane $\left(\mathrm{CH}_{4}\right)$ are known to interfere with the $\mathrm{CO}_{2}$ absorption [4,5]. A method well suited for $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ absorption is the use of water-amine based systems [6]. These systems provide a wide variety of different applications in gas-absorption processes. Concerning the single amine systems, monoethanolamine (MEA), diethanolamine (DEA) and methyldiethanolamine (MDEA) are commonly used for $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ absorption processes. For the single amine absorption systems,

\footnotetext{
* Corresponding author.

E-mail address: christoph.held@tu-dortmund.de (C. Held).
}

MDEA is the most commonly used amine, due to its advantages in regard to its high capacity of $\mathrm{CO}_{2} / \mathrm{H}_{2} \mathrm{~S}$ loading per mole amine and a low enthalpy of absorption [7]. An increased interest in MDEA-based absorption systems [8] leads to the challenge of developing models that are capable of predicting the vapor liquid equilibrium (VLE) of the water-amine-gas system in combination with the enthalpy of absorption to reduce development, plant and operating costs [1,9,10].

Literature proposes a number of models that are focused on modeling the ternary water-amine-gas systems based on experimental data for the temperature range of $313-413 \mathrm{~K}$ and amine weight fractions between 0.19 and 0.6 (related to the binary water/ amine system) [11-14]. Most of the models proposed in literature are of empirical nature. They require a large number of experimental data and furthermore neglect speciation caused by reaction equilibrium and only focus on describing the VLE [15,16]. In contrast, some models were successfully combined with reaction equilibria, e.g., electrolyte Non-Random Two Liquid (eNRTL) [17] and Universal Quasichemical model (UNIQUAC) [18]. Especially good modeling results of the VLE of water-amine-gas systems for a wide range of temperature, pressure and amine weight fractions
were achieved with the equations of Pitzer [13,19]. While such activity-coefficient models allow a good interpolation between experimental data, it is well-known that they require a lot of parameters that are fit to experimental data of the ternary amine-gaswater system. These parameters are system-specific and depend on temperature and composition. Thus, these parameters do not allow for de novo predictions [12,17,18]. A reduction of experimental effort can be achieved by the use of equations of state such as Cubic Plus Association equation of state (CPA) [20], Statistical Associating Fluid Theory (SAFT) [21], the SAFT-VR [22] or Perturbed-Chain SAFT (PC-SAFT) [23]. These models do not necessarily require experimental data of the ternary system, if the physics of the systems under investigation is described correctly.

In a first attempt of predicting the VLE of the ternary system water-MDEA- $\mathrm{CO}_{2}$, Uyan et al. [24] proposed a model based on the electrolyte PC-SAFT (ePC-SAFT) equation of state. Compared to Pahlavanzadeh et al. [23], the activities of all species in the solution were explicitly considered. This new approach allowed good predictions of $\mathrm{CO}_{2}$ solubility at MDEA weight fractions $\mathrm{w}_{\text {MDEA }}<0.32$. The VLE of the ternary system water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ was predicted by Nasrifar and Tafazzol [25] using classical PC-SAFT for $\mathrm{w}_{\text {MDEA }}<0.48$.

The influence of inert components (e.g. $\mathrm{CH}_{4}$ ) on VLE of water-MDEA- $\mathrm{CO}_{2}$ was modeled with eNRTL and extended UNIQUAC [26]; the application of equations of state has not yet been reported. Further, enthalpies of absorption of water-MDEA-CO2 were correlated using the equations of Pitzer [27] and eNRTL [17]. The computational chemistry continuum solvation model in combination with the quantum mechanical DFT model [9] was used to predict enthalpies of absorption in water-MDEA- $\mathrm{CO}_{2}$, however, quantitative predictions were not possible. The use of equations of state or other predictive models to obtain results that strife from a qualitative to a more quantitative prediction has not been reported in the literature so far and are the attempt of this work.

This work focuses on predicting $\mathrm{CO}_{2}$ and $\mathrm{H}_{2} \mathrm{~S}$ solubility in aqueous MDEA solutions, the influence of $\mathrm{CH}_{4}$ thereon, and enthalpy of absorption. ePC-SAFT as proposed by Uyan et al. [24] was used for all these calculations. Compared to the work from Uyan et al., binary interaction parameters were introduced that were fit to new osmotic-coefficient data. This allows predictions of the VLE of the water-MDEA-CO2 system for MDEA weight fractions up to 0.6 with improved accuracy compared to [24]. Using ePCSAFT as proposed in this work means a significantly reduced experimental effort for the development costs of amine-based gas absorption systems.

\section*{2. Materials and methods}

Chemicals used in this work were $\mathrm{CO}_{2}$ from basi Schöberl, MDEA from BASF SE and hydrogen chloride from Merck. All samples were prepared using HPLC grade water from J.T. Baker or millipore water from the MilliQ system provided by Merck Millipore. A list of all chemicals used can be found in Table 1.

For the new $\mathrm{CO}_{2}$ solubility data in an aqueous solution of MDEA with an MDEA weight fraction of $0.6 \pm 0.001$, an experimental method and device was applied comparable to one of Kuranov at al.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1
Sample provenance table. $\mathrm{M}=$ Merck Deutschland KGaA, B = BASF SE Ludwigshafen, $\mathrm{JT}=\mathrm{J} . \mathrm{T}$. Baker- Thermo Fisher Scientific, $\mathrm{S}=$ basi Schöberl GmbH \& Co. KG.}
\begin{tabular}{|l|l|l|l|}
\hline Compound & Purity & CAS & Supplier \\
\hline Carbon dioxide & >99\% & 124-38-9 & S \\
\hline N-Methyldiethanolamine & >99\% & 105-59-9 & B \\
\hline Hydrogen chloride & >95\% & 7647-01-0 & M \\
\hline HPLC grade water & >99\% & 7732-18-5 & JT \\
\hline
\end{tabular}
\end{table}
[13], therefore only a short outline is given here. The core part of the device is a high-pressure view cell (volume of about $30 \mathrm{~cm}^{3}$ ) with sapphire windows.

The aqueous solution of MDEA has to be inert-gas free. Therefore, the gravimetrically prepared mixture was cooled down and degassed by removal of the vapor phase for several times. The prepared MDEA solution was filled into a displacer afterwards.

In the evacuated cell a desired amount of $\mathrm{CO}_{2}$ was added to the solution. The mass of $\mathrm{CO}_{2}$ was calculated by the known volume of the cell, the measured temperature, and the pressure in the cell. By using the EOS for $\mathrm{CO}_{2}$ of Span and Wagner [28] the mass of $\mathrm{CO}_{2}$ was calculated with an uncertainty of $0.02 \mathrm{~g}( \pm 0.3 \%)$. After that, $\mathrm{CO}_{2}$ was filled into the cell and the solvent was added step by step by the calibrated high-pressure displacer, until $\mathrm{CO}_{2}$ was completely dissolved. The boiling point was determined by removing a small amount of the liquid mixture until the first bubble appears. The amount of required solvent was determined by the displacement of the piston and the density of the aqueous solution (uncertainty 0.2 wt.\%).

The applied pressure transducer (Sensotec, Model TJE, US) with a range of $0-100$ bar was calibrated with an uncertainty $0.1 \%$ of maximum reading, resulting in uncertainty of 0.3 bar caused by inaccuracies in pressure measurement and optical detection of the bubbles. The uncertainty in temperature measurement is estimated to be $\pm 0.1 \mathrm{~K}$.

Osmotic coefficients of the system water-MDEA-HCl were measured using a freezing-point depression OSMOMAT O10 from Gonotec (Germany). The measurement is based on the freezingpoint depression of the sample as a function of concentration of MDEA and HCl , which were present in the samples with equimolar concentration. After calibration with sodium chloride samples provided by Gonotec, the osmolality of the sample osm measured was directly related to the osmotic coefficient $\phi$ as shown in Equation (1):

$$
\begin{equation*}
\phi=\frac{\mathrm{osm}}{\mathrm{v} \cdot \mathrm{~m}} \tag{1}
\end{equation*}
$$


In Equation (1) $v$ and $m$ characterize the amount of ions in which the components may dissociate and the initial molality of $\mathrm{MDEA}+\mathrm{HCl}$, respectively.

Additional osmotic coefficients of the system water-MDEA-HCl were measured at 313 K using vapor-pressure osmometry data, measured with a vapor-pressure osmometer K-7000 from Knauer (Germany). In the K-7000, the resistance between two thermistors connected via a Wheatstone bridge is measured. First, water was dropped on the tip of both thermistors, which were located in a water-saturated measurement cell. After the addition of the sample on the tip of one thermistor, vapor-pressure differences between the droplets of both thermistors lead to a measurable current $\Delta \mathrm{I}$. With a calibration constant $\mathrm{k}_{\text {calib }}$ obtained from sodium chloride solutions of known osmolality purchased from Knauer, the osmotic coefficients were calculated with Equation (2).

$$
\begin{equation*}
\phi=\frac{\Delta \mathrm{I} \cdot \mathrm{k}_{\mathrm{calib}}}{v \cdot \mathrm{~m}} \tag{2}
\end{equation*}
$$


\section*{3. Phase equilibra and ePC-SAFT equation of state}

The prediction of the VLE for the ternary systems water-MDEA- $\mathrm{CO}_{2}$ and water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$, as well as for the quaternary system water-MDEA- $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ was based on the isofugacity criteria shown in Equation (3):

$$
\begin{equation*}
x_{i} \phi_{i}^{L}\left(T, p, \vec{x}^{L}\right)=y_{i} \phi_{i}^{V}\left(T, p, \vec{y}^{V}\right) \tag{3}
\end{equation*}
$$

wherex $x_{i}$ and $y_{i}$ denote the mole fractions of the component i (water, MDEA, $\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}, \mathrm{CH}_{4}$ ) in the liquid phase L and in the vapor phase V. $\phi_{i}$ are the fugacity coefficients of the component i , which can be calculated by Equation (4) using Equation (5):

$$
\begin{align*}
& \ln \left(\phi_{i}\right)=\frac{\mu_{i}^{\text {res }}}{k_{B} \cdot T}-\ln \left(1+\left(\frac{\partial\left(\frac{a^{\text {res }}}{k_{B} \cdot T}\right)}{\partial \rho}\right)_{T, V}\right)  \tag{4}\\
& \frac{\mu_{i}^{\text {res }}}{k_{B} \cdot T}=\frac{a^{\text {res }}}{k_{B} \cdot T}+Z-1+\left(\frac{\partial\left(\frac{a^{\text {res }}}{k_{B} \cdot T}\right)}{\partial x_{i}}\right)_{T, V, x_{k \neq i}}-\sum_{j=1}^{N}\left(\frac{\partial\left(\frac{a^{\text {res }}}{k_{B} \cdot T}\right)}{\partial x_{i}}\right)_{T, V, x_{k \neq j}} \tag{5}
\end{align*}
$$


In Equation (4) $\mu_{i}^{\text {res }}$ denotes the residual chemical potential, $k_{B}$ the Boltzmann constant, $a^{\text {res }}$ the residual Helmholtz energy, $Z$ to the compressibility factor and $\rho$ the number density of the system. The residual chemical potential of a component $i$ can be calculated by textbook thermodynamics, which requires the temperaturedependent segment diameter $d_{i}$. For all non-charged components, Equation (6) was used according to [29,30].

$$
\begin{equation*}
d_{i}=\sigma_{i} \cdot\left(1-0.12 \cdot \exp \left(-3 \cdot \frac{u_{i}}{k_{B} \cdot T}\right)\right) \tag{6}
\end{equation*}
$$


In contrast, for ions Equation (7) was applied [31-34] which leads to a temperature-independent value for $d_{i}$.

$$
\begin{equation*}
d_{i}=0.88 \cdot \sigma_{i} \tag{7}
\end{equation*}
$$


An expression for a $\mathrm{a}^{\text {res }}$ in Equation (4) was provided by the original ePC-SAFT publication [35].

$$
\begin{equation*}
\mathrm{a}^{\text {res }}=\mathrm{a}^{\text {hc }}+\mathrm{a}^{\text {disp }}+\mathrm{a}^{\text {assoc }}+\mathrm{a}^{\text {ion }} \tag{8}
\end{equation*}
$$


In this work, four contributions to $\mathrm{a}^{\text {res }}$ were considered, the hard-chain contribution $\mathrm{a}^{\mathrm{hc}}$, the dispersion contribution $\mathrm{a}^{\mathrm{disp}}$, the association contribution a ${ }^{\text {assoc }}$, and additionally the Debye-Hückel contribution $\mathrm{a}^{\text {ion }}$. Uncharged components are described with five PC-SAFT parameters, the segment number $m_{\text {seg }}$ and the segment diameter $\sigma$, the dispersion-energy parameter $u / k_{B}$, as well as two association parameters $\varepsilon^{A_{i} B_{i}} / k_{B}$ and $\kappa^{A_{i} B_{i}}$ in case of associating components. In contrast, ions are most commonly modeled as spherical non-associating species [35]. In this work this was applied to all inorganic ions, while MDEAH ${ }^{+}$and $\mathrm{HS}^{-}$were regarded as non-spherical species. MDEAH ${ }^{+}$was additionally allowed to crossassociate to water or MDEA [24], while $\mathrm{HS}^{-}$was considered as nonassociating species [25]. Ions of equal charge sign were not allowed to interact via cross dispersion, while dispersion between ions of different charge sign was allowed. Additionally, the calculation of $\mathrm{a}^{\text {ion }}$ requires the dielectric constant $\varepsilon$, which was assumed a function of water-MDEA composition, temperature, and independent of any ions present in the solution [24,36].

To predict mixture properties with increased precision [31,37], combining rules of Berthelot and Lorenz [38,39] and WolbachSandler [40] have been applied to the segment diameter, dispersion and association energy parameter and the association volume, introducing a binary interaction parameter $\mathrm{k}_{\mathrm{ij}}$ for the dispersion energy and $\mathrm{l}_{\mathrm{ij}}^{\mathrm{hb}}$ for the association volume.

$$
\begin{equation*}
\sigma_{i j}=\frac{1}{2} \cdot\left(\sigma_{i}+\sigma_{j}\right) \tag{9}
\end{equation*}
$$


$$
\begin{equation*}
\varepsilon^{A_{i} B_{j}}=\frac{1}{2} \cdot\left(\varepsilon^{A_{i} B_{i}}+\varepsilon^{A_{j} B_{j}}\right) \tag{10}
\end{equation*}
$$


$$
\begin{equation*}
u_{i j}=\sqrt{u_{i} \times u_{j}} \times\left(1-k_{i j}\right) \tag{11}
\end{equation*}
$$


$$
\begin{equation*}
\kappa^{A_{i} B_{j}}=\sqrt{\kappa^{A_{i} B_{i}} \cdot \kappa} A_{j} B_{j} \cdot\left(\frac{\sqrt{\sigma_{i} \cdot \sigma_{j}}}{\sigma_{i j}}\right)^{3} \cdot\left(1-l_{i j}^{h b}\right) ~ \tag{12}
\end{equation*}
$$


\section*{4. Chemical reaction equilibrium}

Besides the physical solubility of $\mathrm{CO}_{2}, \mathrm{H}_{2} \mathrm{~S}$ and $\mathrm{CH}_{4}$ in the water-MDEA system, the following chemical reactions that take place in the liquid phase were accounted for:

$$
\begin{aligned}
\mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{H}^{+}+\mathrm{OH}^{-} \cdot \mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{HCO}_{3}^{-}+\mathrm{H}^{+} \cdot \mathrm{HCO}_{3}^{-} \rightleftharpoons \mathrm{CO}_{3}^{2-} & \\
& +\mathrm{H}^{+} \cdot \mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{HCO}_{3}^{-}+\mathrm{H}^{+} \cdot \mathrm{MDEAH}^{+} \rightleftharpoons \mathrm{MDEA} \\
& +\mathrm{H}^{+} \cdot \mathrm{H}_{2} \mathrm{~S} \rightleftharpoons \mathrm{HS}^{-}+\mathrm{H}^{+}
\end{aligned}
$$


As seen in Scheme $1 \mathrm{CH}_{4}$ is not included in any chemical reaction, and it is regarded as an inert component [4,41].

The thermodynamic equilibrium constant $K_{a}$ for each of the reactions shown in Scheme 1 can be expressed as:

$$
\begin{equation*}
K_{a}(T)=\prod_{i}\left(x_{i} \cdot \gamma_{i}\right)^{\nu_{i}} \tag{13}
\end{equation*}
$$

where $x_{i}$ denotes the mole fraction and $\gamma_{i}$ the activity coefficient of component $i$. This leads to the following expressions for the reactions shown in Scheme 1:

$$
\begin{equation*}
\mathrm{K}_{\mathrm{a}, 1}=\frac{\mathrm{x}_{\mathrm{H}^{+}} \cdot \mathrm{x}_{\mathrm{OH}^{-}}}{\mathrm{x}_{\mathrm{H}_{2} \mathrm{O}}} \cdot \frac{\gamma_{\mathrm{H}^{+}}^{*} \cdot \gamma_{\mathrm{OH}^{-}}^{*}}{\gamma_{\mathrm{H}_{2} \mathrm{O}}^{0}} \tag{14}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{K}_{\mathrm{a}, 2}=\frac{\mathrm{x}_{\mathrm{H}^{+}} \cdot \mathrm{x}_{\mathrm{HCO}_{3}^{-}}}{\mathrm{x}_{\mathrm{H}_{2} \mathrm{O}} \cdot \mathrm{x}_{\mathrm{CO}_{2}}} \cdot \frac{\gamma_{\mathrm{H}^{+}}^{*} \cdot \gamma_{\mathrm{HCO}_{3}^{-}}^{*}}{\gamma_{\mathrm{H}_{2} \mathrm{O}}^{0} \cdot \gamma_{\mathrm{CO}_{2}}^{*}} \tag{15}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{K}_{\mathrm{a}, 3}=\frac{\mathrm{x}_{\mathrm{H}^{+}} \cdot \mathrm{x}_{\mathrm{CO}_{3}^{2-}}}{\mathrm{x}_{\mathrm{HCO}_{3}^{-}}} \cdot \frac{\gamma_{\mathrm{H}^{+}}^{*} \cdot \gamma_{\mathrm{CO}_{3}^{2-}}^{*}}{\gamma_{\mathrm{HCO}_{3}^{-}}^{*}} \tag{16}
\end{equation*}
$$


$$
\begin{gathered}
\mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{H}^{+}+\mathrm{OH}^{-} \\
\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{HCO}_{3}^{-}+\mathrm{H}^{+} \\
\mathrm{HCO}_{3}^{-} \rightleftharpoons \mathrm{CO}_{3}^{2-}+\mathrm{H}^{+} \\
\mathrm{CO}_{2}+\mathrm{H}_{2} \mathrm{O} \rightleftharpoons \mathrm{HCO}_{3}^{-}+\mathrm{H}^{+} \\
\mathrm{MDEAH}^{+} \rightleftharpoons \mathrm{MDEA}+\mathrm{H}^{+} \\
\mathrm{H}_{2} \mathrm{~S} \rightleftharpoons \mathrm{HS}^{-}+\mathrm{H}^{+}
\end{gathered}
$$


Scheme 1. Overview of the reactions of the liquid water-MDEA-CO2, water-MDEA-$\mathrm{CO}_{2}-\mathrm{CH}_{4}$ and water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ system accounted for.

$$
\begin{equation*}
\mathrm{K}_{\mathrm{a}, 4}=\frac{\mathrm{x}_{\mathrm{H}^{+}} \cdot \mathrm{x}_{\mathrm{MDEA}}}{\mathrm{x}_{\mathrm{MDEAH}^{+}}} \cdot \frac{\gamma_{\mathrm{H}^{+}}^{*} \cdot \gamma_{\mathrm{MDEA}}^{*}}{\gamma_{\mathrm{MDEAH}^{+}}^{*}} \tag{17}
\end{equation*}
$$


$$
\begin{equation*}
\mathrm{K}_{\mathrm{a}, 5}=\frac{\mathrm{x}_{\mathrm{H}^{+}} \cdot \mathrm{x}_{\mathrm{HS}^{-}}}{\mathrm{x}_{\mathrm{H}_{2} \mathrm{~S}}} \cdot \frac{\gamma_{\mathrm{H}^{+}}^{*} \cdot \gamma_{\mathrm{HS}^{-}}^{*}}{\gamma_{\mathrm{H}_{2} \mathrm{~S}}^{*}} \tag{18}
\end{equation*}
$$


Besides being calculated with Equations ( $14-18$ ), $K_{a}$-values can be taken directly from literature data (e.g. correlation to the enthalpy of reaction) as a function of temperature, as shown in Equation (19):

$$
\begin{equation*}
\ln K_{a}(T)=c_{1}+\frac{c_{2}}{T / K}+c_{3} \cdot \ln (T / K)+c_{4} \cdot(T / K) \tag{19}
\end{equation*}
$$


The constants $\mathrm{c}_{1}-\mathrm{c}_{4}$ for Equation (19) are listed in Table 2.
For the application of Equations (14-18) activity coefficients of each reacting agent were required. These can be calculated with ePC-SAFT based on the fugacity coefficient of each component from Equation (4). The relations between the fugacity coefficient and the generic activity coefficient $\gamma^{0}$ and the rational activity coefficient $\gamma^{*}$ are as follows:

$$
\begin{equation*}
\gamma_{i}^{0}=\frac{\phi_{i}(T, p, \vec{x})}{\phi_{0 i}\left(T, p, x_{i}=1\right)} \tag{20}
\end{equation*}
$$


$$
\begin{equation*}
\gamma_{i}^{*}=\frac{\phi_{i}(T, p, \vec{x})}{\phi_{i}^{\infty}\left(T, p, x_{i}=0\right)} \tag{21}
\end{equation*}
$$


In Equation (20) the subscript 0i refers to the reference state of the "pure component", while the superscript $\infty$ refers to the state of infinite-dilution. In order to calculate the mole-fraction-based composition $\overrightarrow{\mathrm{x}}$, the K-value method was used according to [24,45].

\section*{5. Enthalpy of absorption}

The enthalpy of absorption $\Delta \mathrm{H}^{\text {abs }}$ caused by absorbing $\mathrm{CO}_{2}$ into the water-MDEA liquid phase can be divided into three different contributions [17]. The contribution of the enthalpy of reaction $\Delta H_{i}^{R}$ with the reaction coordination number $\lambda$, the physical dissolution of the gas in the liquid phase $\Delta \mathrm{H}^{\mathrm{dis}}$ and the excess enthalpy $\Delta \mathrm{H}^{\mathrm{ex}}$. All these contributions were treated additively and are related to the moles of absorbed $\mathrm{CO}_{2}$

$$
\begin{equation*}
\Delta H^{a b s}\left[\frac{J}{m o l ~ C O_{2}^{\text {absorbed }}}\right]=\sum_{i} \frac{\lambda_{i}}{n_{C O_{2}^{\text {absorbed }}}} \cdot \Delta H_{i}^{R}+\Delta H^{\text {dis }}+\Delta H^{\text {ex }} \tag{22}
\end{equation*}
$$


The enthalpy of reaction i $\Delta H_{i}^{R}$ was calculated with the van't Hoff equation, as shown in Equation (23).

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2
Constants $\mathrm{c}_{1}-\mathrm{c}_{4}$ used for the mole-based calculation of equilibrium constants $\boldsymbol{K}_{\boldsymbol{a}}$ in Equations (14-18).}
\begin{tabular}{|l|l|l|l|l|l|}
\hline Eq. constant & c1 & c2 & c3 & $\mathrm{c}_{4}$ & Ref. \\
\hline $\mathrm{K}_{\mathrm{a}, 1}$ & $1.329 \cdot 10^{2}$ & $-1.345 \cdot 10^{4}$ & $-2.248 \cdot 10^{1}$ & 0 & [19] \\
\hline $\mathrm{K}_{\mathrm{a}, 2}$ & $2.127 \cdot 10^{2}$ & $-1.133 \cdot 10^{4}$ & $-3.384 \cdot 10^{1}$ & $-1.815 \cdot 10^{-3}$ & [42] \\
\hline $\mathrm{K}_{\mathrm{a}, 3}$ & $2.874 \cdot 10^{2}$ & $-1.365 \cdot 10^{4}$ & $-4.888 \cdot 10^{1}$ & $3.023 \cdot 10^{-2}$ & [43] \\
\hline $\mathrm{K}_{\mathrm{a}, 4}$ & $-8.349 \cdot 10^{1}$ & $-8.197 \cdot 10^{2}$ & $1.098 \cdot 10^{1}$ & 0 & [44] \\
\hline $\mathrm{K}_{\mathrm{a}, 5}$ & $2.146 \cdot 10^{2}$ & $-1.299 \cdot 10^{4}$ & $-3.355 \cdot 10^{1}$ & 0 & [12] \\
\hline
\end{tabular}
\end{table}

$$
\begin{equation*}
\Delta H_{i}^{R}(T)=R T^{2} \cdot\left(\frac{d \ln K_{a, i}}{d T}\right) \tag{23}
\end{equation*}
$$


To calculate the enthalpy of dissolution $\Delta \mathrm{H}^{\text {dis }}$, the difference between the enthalpy of 1 mol of $\mathrm{CO}_{2}$ in the gas phase $\mathrm{H}_{\mathrm{CO}_{2}}^{\mathrm{V}}$ and the enthalpy of $1 \mathrm{~mol} \mathrm{CO}_{2}$ in the liquid phase at infinite dilution $\mathrm{H}_{\mathrm{CO}_{2}}^{\mathrm{L}, \infty}$ is required [17]. This is shown in Equation (24).

$$
\begin{equation*}
\Delta H^{\text {dis }}(T)=H_{\mathrm{CO}_{2}}^{V}-H_{\mathrm{CO}_{2}}^{L, \infty} \tag{24}
\end{equation*}
$$


The enthalpy of $\mathrm{CO}_{2}$ in the gas phase can be calculated as the sum of the residual enthalpy $\mathrm{H}_{\mathrm{CO}_{2}}^{\mathrm{V} \text {,res }}$ and the enthalpy of the ideal gas $\mathrm{H}_{\mathrm{CO}_{2}}^{\mathrm{V}, \mathrm{ig}}$, as shown in Equation (25).

$$
\begin{equation*}
H_{\mathrm{CO}_{2}}^{V}(T)=H_{\mathrm{CO}_{2}}^{V, \text { res }}+H_{\mathrm{CO}_{2}}^{V, \text { ig }} \tag{25}
\end{equation*}
$$


The residual part of the enthalpy in Equation (25) was calculated with ePC-SAFT [46], while the ideal-gas contribution was calculated according to [47]. Assuming the discrete energy level to be zero and accounting only for the ground state of the electrons [48] results in Equation (26). The parameters $\mathrm{A}_{1}$ to $\mathrm{A}_{6}$ were simultaneously fit to experimental pure-component data [47,48] and are listed in Table 3. It is noteworthy that ions have not been accounted for, due to a lack of literature data.

$$
\begin{align*}
\frac{\mathrm{H}^{\mathrm{ig}}(\mathrm{~T})}{\mathrm{n}}= & \mathrm{A}_{2}+\mathrm{A}_{3} \cdot\left(\frac{\mathrm{~A}_{4}}{\mathrm{~T} / \mathrm{K}}\right) \cdot \frac{1}{\tanh \left(\frac{\mathrm{~A}_{4}}{\mathrm{~T} / \mathrm{K}}\right)}-\mathrm{A}_{5} \cdot\left(\frac{\mathrm{~A}_{6}}{\mathrm{~T} / \mathrm{K}}\right) \tanh \left(\frac{\mathrm{A}_{6}}{\mathrm{~T} / \mathrm{K}}\right) \\
& +\frac{\mathrm{A}_{1}}{\mathrm{~T} / \mathrm{K}} \tag{26}
\end{align*}
$$


In order to calculate $\Delta \mathrm{H}^{\text {dis }}$, the enthalpy of 1 mol of $\mathrm{CO}_{2}$ in the liquid phase at infinite dilution $\mathrm{H}_{\mathrm{CO}_{2}}^{\mathrm{L}, \infty}$ is required as shown in Equation (24). It can be calculated with the enthalpy of formation $\Delta_{\mathrm{f}} \mathrm{H}_{\mathrm{CO}_{2}}^{\mathrm{ig}}$, which is reported in literature [17] and the Henry coefficient of $\mathrm{CO}_{2}$ in water $\mathrm{H}_{\mathrm{CO}_{2}, \mathrm{w}}$.

$$
\begin{equation*}
H_{C O_{2}}^{L, \infty}(T)=\Delta_{f} H_{C O_{2}}^{i g}-R T^{2} \cdot\left(\frac{\partial \ln H_{C O_{2}, w}}{\partial T}\right)_{p, x_{j \neq C_{2}}} \tag{27}
\end{equation*}
$$

$\ln H_{C O 2, W}(T)=91.34-\frac{5,876}{T / K}-8.598 \cdot \ln (T / K)$

$$
\begin{equation*}
-1.24 \cdot 10^{-4} \cdot(T / K) \tag{28}
\end{equation*}
$$


The coefficients in Equation (28) were taken from Yan and Chen [49].

Finally the excess enthalpy $\Delta \mathrm{H}^{\mathrm{ex}}$ was calculated as the

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3
Parameters for the calculation of the ideal gas enthalpy $\mathrm{H}^{\mathrm{ig}}$ with Equation (26) for the components $\mathrm{H}_{2} \mathrm{O}, \mathrm{CO}_{2}$ and MDEA.}
\begin{tabular}{|l|l|l|l|}
\hline Parameter & $\mathrm{H}_{2} \mathrm{O}$ & $\mathrm{CO}_{2}$ & MDEA \\
\hline $\mathrm{A}_{1}$ & $-3.113 \cdot 10^{5}$ & $-4.367 \cdot 10^{5}$ & $-7.748 \cdot 10^{5}$ \\
\hline $\mathrm{A}_{2}$ & $3.336 \cdot 10^{1}$ & $2.937 \cdot 10^{1}$ & $1.192 \cdot 10^{2}$ \\
\hline $\mathrm{A}_{3}$ & $2.679 \cdot 10^{1}$ & $3.454 \cdot 10^{1}$ & $3.349 \cdot 10^{2}$ \\
\hline $\mathrm{A}_{4}$ & $2.611 \cdot 10^{3}$ & $1.428 \cdot 10^{3}$ & $1.585 \cdot 10^{3}$ \\
\hline $\mathrm{A}_{5}$ & $8.896 \cdot 10^{0}$ & $2.640 \cdot 10^{1}$ & $2.372 \cdot 10^{2}$ \\
\hline $\mathrm{A}_{6}$ & $1.169 \cdot 10^{3}$ & $5.880 \cdot 10^{2}$ & $-7.347 \cdot 10^{2}$ \\
\hline
\end{tabular}
\end{table}
difference between the real enthalpy of the solution $\mathrm{H}^{\text {real }}$ and the ideal mixing enthalpy of the solution $\mathrm{H}^{\text {mix }}$ as shown in Equations (29)-(31).

$$
\begin{align*}
& \Delta H^{e x}(T)=H^{r e a l}(T)-H^{m i x}(T)  \tag{29}\\
& H^{m i x}(T)=\sum_{i} H_{i}(T) \cdot x_{i}  \tag{30}\\
& H^{r e a l}(T)=H^{r e s}(T)+\sum_{i} x_{i} \cdot H_{i}^{i d}(T) \tag{31}
\end{align*}
$$


\section*{6. Results and discussion}

The main goal of this work was an improvement in prediction of the VLE water-MDEA- $\mathrm{CO}_{2}$ for MDEA weight fractions $\mathrm{w}_{\text {MDEA }} \geq$ 0.32 , the prediction of the VLE water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$, the prediction of the influence of $\mathrm{CH}_{4}$ on the VLE water-MDEA- $\mathrm{CO}_{2}$ and the prediction of the enthalpy of absorption for the VLE of water-MDEA- $\mathrm{CO}_{2}$.

All ePC-SAFT predictions were compared to experimental data in terms of the absolute relative deviation ARD:

$$
\begin{equation*}
A R D=\frac{100}{r} \cdot \sum_{i=1}^{r}\left|1-\frac{e_{i}^{c a l}}{e_{i}^{\exp }}\right| \tag{32}
\end{equation*}
$$

where $\mathrm{e}_{\mathrm{i}}^{\text {cal }}$ and $e_{i}^{\text {exp }}$ denote the ePC-SAFT predicted and the experimentally determined values for an amount of available experimental data points r.

\subsection*{6.1. Pure-component and binary ePC-SAFT parameters}

In a first step ePC-SAFT pure-component parameters for all components regarded in this work were collected from literature as listed in Table 4 and Table 5.

In a second step available binary interactions parameters were collected from literature, while the $k_{i j}$ values between water- $\mathrm{HCO}_{3}^{-}$, water-MDEA, water- $\mathrm{H}_{2} \mathrm{~S}$, water- $\mathrm{CH}_{4}, \mathrm{CO}_{2}-\mathrm{CH}_{4}$, water- $\mathrm{MDEAH}^{+}$and water- $\mathrm{HS}^{-}$have been fitted in this work. Furthermore, $l_{i j}^{h b}$ values between water-MDEA were introduced, and binary parameters between water-MDEAH ${ }^{+}$were fit to new experimental data. The parameter fit was performed with a Levenberg-Marquardt algorithm (damped least-squares method). The objective function OF3 is given in Equation (33), with $y_{m}^{m o d}$ denoting to the modeled and $y_{m}^{\text {exp }}$ to the experimental value.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4
Pure-component ePC-SAFT parameters for all uncharged components considered in this work.}
\begin{tabular}{|l|l|l|l|l|l|}
\hline Parameter & $\mathrm{H}_{2} \mathrm{O}$ & MDEA & $\mathrm{CO}_{2}$ & $\mathrm{H}_{2} \mathrm{~S}$ & $\mathrm{CH}_{4}$ \\
\hline $\mathrm{m}_{\text {seg }}[-]$ & 1.2046 & 3.6750 & 2.0729 & 1.6686 & 1.0000 \\
\hline $\sigma[\AA]$ & * & 3.5630 & 2.7852 & 3.0349 & 3.7039 \\
\hline $\frac{u_{i}}{k_{B}}[K]$ & 353.94 & 228.71 & 169.21 & 229.00 & 150.03 \\
\hline $N[-]$ & 1:1 & 2:2 & - & - & - \\
\hline $\frac{\varepsilon^{A_{i} B_{i}}}{k_{B}}[K]$ & 2425.6 & 2046.6 & - & - & - \\
\hline $\kappa^{A_{i} B_{i}}[-]$ & 0.0450 & 0.1238 & - & - & - \\
\hline Ref. & [50] & [23] & [51] & [25] & [9] \\
\hline \multicolumn{4}{|c|}{${ }^{*} . \sigma=2.7927+\left(10.11 \cdot \mathrm{e}^{-0.01775 \mathrm{~T}}-1.417 \cdot \mathrm{e}^{-0.01146 \mathrm{~T}}\right)$.} & & \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5
ePC-SAFT pure-component parameter for the ions considered in this work.}
\begin{tabular}{|l|l|l|l|l|}
\hline Ion & $\sigma[\AA]$ & $\frac{u_{i}}{k_{B}}[K]$ & $\mathrm{z}_{\mathrm{i}}$ [-] & Ref. \\
\hline $\mathrm{H}^{+}$ & 3.4654 & 500.00 & +1 & [36] \\
\hline $\mathrm{OH}^{-}$ & 2.0177 & 650.00 & -1 & [36] \\
\hline $\mathrm{HCO}_{3}^{-}$ & 2.9296 & 70.00 & -1 & [36] \\
\hline $\mathrm{CO}_{3}^{2-}$ & 2.4422 & 249.26 & -2 & [36] \\
\hline $\mathrm{HS}^{-}$ & 3.0349 & 229.00 & -1 & * \\
\hline MDEAH ${ }^{+}$ & 3.5630 & 228.71 & +1 & * \\
\hline
\end{tabular}
\end{table}
*Pure-component parameters transferred from $\mathrm{H}_{2} \mathrm{~S}$ and MDEA respectively.

$$
\begin{equation*}
O F 3=\sum_{m=1}^{y_{m}} \sum_{k=1}^{N P_{y_{m}}}\left(1-\left(\frac{y_{m}^{\bmod }}{y_{m}^{\exp }}\right)_{k}\right)^{2} \tag{33}
\end{equation*}
$$


The binary interaction parameters were considered to be a function of temperature as shown in Equations (34) and (35).

$$
\begin{align*}
k_{i j}(T)= & k_{i j, a}+k_{i j, T} \cdot\left(T-T^{+}\right)+k_{i j, T^{2}} \cdot\left(T-T^{+}\right) \\
& +k_{i j, T^{3}} \cdot\left(T-T^{+}\right) \tag{34}
\end{align*}
$$


$$
\begin{equation*}
\mathrm{l}_{\mathrm{ij}}^{\mathrm{hb}}(\mathrm{~T})=\mathrm{l}_{\mathrm{ij}, \mathrm{a}}^{\mathrm{hb}}+\mathrm{l}_{\mathrm{ij}, \mathrm{~T}}^{\mathrm{hb}} \cdot\left(\mathrm{~T}-\mathrm{T}^{+}\right)+\mathrm{l}_{\mathrm{ij}, \mathrm{~T}^{2}}^{\mathrm{hb}} \cdot\left(\mathrm{~T}-\mathrm{T}^{+}\right) \tag{35}
\end{equation*}
$$


Where $T^{+}$is 298.15 K , and all parameters are listed in Table 6 and Table 7.

\subsection*{6.1.1. Binary systems: water-MDEA, water- $\mathrm{H}_{2} \mathrm{~S}$, water- $\mathrm{CH}_{4}$ and $\mathrm{CO}_{2}-\mathrm{CH}_{4}$}

Binary interaction parameters $\mathrm{k}_{\mathrm{ij}}$ and $\mathrm{l}_{\mathrm{ij}}^{\mathrm{hb}}$ for the binary systems water-MDEA, water- $\mathrm{H}_{2} \mathrm{~S}$, water- $\mathrm{CH}_{4}$ and $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ have been fit to experimental VLE data of the respective systems. The results of the parameter fit are shown in Figs. 1-6.

\subsection*{6.1.2. Binary pair water- $\mathbf{H C O}_{3}^{-}$}

The $\mathrm{k}_{\mathrm{ij}}$ between water- $\mathrm{HCO}_{3}^{-}$was assumed to be zero in literature [36] and thus was used in Ref. [24]. However, in the present work the $\mathrm{k}_{\mathrm{ij}}$ between water- $\mathrm{HCO}_{3}^{-}$was found to be sensitive for VLE prediction results of the system water-MDEA- $\mathrm{CO}_{2}$, which can be explained by the high concentration of $\mathrm{HCO}_{3}^{-}$in these solutions. In this work the $\mathrm{k}_{\mathrm{ij}}$ between water- $\mathrm{HCO}_{3}^{-}$was adjusted to experimental osmotic coefficients $\phi$ of the system water- $\mathrm{NaHCO}_{3}$ for temperatures $278 \mathrm{~K}<\mathrm{T}<318 \mathrm{~K}$ and ambient pressure. The $\mathrm{k}_{\mathrm{ij}}$ values for the pairs water- $\mathrm{Na}^{+}$and $\mathrm{Na}^{+}-\mathrm{HCO}_{3}^{-}$were inherited from Ref. [36].

As Fig. 7 clearly shows, a newly determined expression for the $\mathrm{k}_{\mathrm{ij}}$ between water- $\mathrm{HCO}_{3}^{-}$allows highly accurate description of the osmotic coefficients of the system water- $\mathrm{NaHCO}_{3}$.

\subsection*{6.1.3. Binary pair water- $\mathbf{H S}^{-}$}

The $\mathrm{k}_{\mathrm{ij}}$ of water- $\mathrm{HS}^{-}$was adjusted to experimental data (freezing-point depression [57] and boiling-point elevation [58]) of the system water- $\mathrm{Na}_{2} \mathrm{~S}$. According to Bialik et al. [58] the dissociation of $\mathrm{Na}_{2} \mathrm{~S}$ in water can be described by Equation (36), and $\mathrm{Na}_{2} \mathrm{~S}$ can be regarded as fully dissociated in the molality range shown in Fig. 8 and Fig. 9 [57-59].

$$
\begin{equation*}
\mathrm{Na}_{2} \mathrm{~S}+\mathrm{H}_{2} \mathrm{O} \rightleftharpoons 2 \mathrm{Na}^{+}+\mathrm{HS}^{-}+\mathrm{OH}^{-} \tag{36}
\end{equation*}
$$


Figs. 8 and 9 illustrate that accurate modeling results were obtained using the ePC-SAFT parameters from Table 4 - Table 7.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 6
Parameters used for Equation (34) to calculate binary interaction parameters $\mathrm{k}_{\mathrm{ij}}$. Please note that these are validated in the considered temperature range in this work (293413 K ).}
\begin{tabular}{|l|l|l|l|l|l|}
\hline Binary System & $\mathrm{k}_{\mathrm{ij}, \mathrm{a}}$ & $\mathrm{k}_{\mathrm{ij}, \mathrm{T}}$ & $\mathrm{k}_{\mathrm{ij}, \mathrm{T}^{2}}$ & $\mathrm{k}_{\mathrm{ij}, \mathrm{T}^{3}}$ & Ref. \\
\hline water-MDEA & $-1.84 \cdot 10^{-1}$ & $-1.21 \cdot 10^{-3}$ & $2.70 \cdot 10^{-6}$ & $1.53 \cdot 10^{-7}$ & * \\
\hline water- $\mathrm{CO}_{2}$ & $-2.15 \cdot 10^{-2}$ & $4.20 \cdot 10^{-4}$ & $-1.70 \cdot 10^{-6}$ & 0 & [24] \\
\hline MDEA- $\mathrm{CO}_{2}$ & 0 & 0 & 0 & 0 & - \\
\hline water- $\mathrm{H}_{2} \mathrm{~S}$ & 0 & 0 & 0 & 0 & \\
\hline MDEA- $\mathrm{H}_{2} \mathrm{~S}$ & 0 & 0 & 0 & 0 & ** \\
\hline water- $\mathrm{CH}_{4}$ & $-5.97 \cdot 10^{-2}$ & $1.28 \cdot 10^{-3}$ & $-2.00 \cdot 10^{-5}$ & 0 & * \\
\hline $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ & $7.32 \cdot 10^{-2}$ & $2.43 \cdot 10^{-4}$ & 0 & 0 & * \\
\hline water $-\mathrm{H}^{+}$ & $2.50 \cdot 10^{-1}$ & 0 & 0 & 0 & [36] \\
\hline water $-\mathrm{OH}^{-}$ & $-2.50 \cdot 10^{-1}$ & 0 & 0 & 0 & [36] \\
\hline water $-\mathrm{HCO}_{3}^{-}$ & $-7.65 \cdot 10^{-2}$ & $-6.25 \cdot 10^{-4}$ & $-6.25 \cdot 10^{-5}$ & 0 & * \\
\hline water $-\mathrm{CO}_{3}^{2-}$ & $-2.50 \cdot 10^{-1}$ & 0 & 0 & 0 & [36] \\
\hline water -MDEAH ${ }^{+}$ & $-1.84 \cdot 10^{-1}$ & $-1.21 \cdot 10^{-3}$ & $2.70 \cdot 10^{-6}$ & $1.53 \cdot 10^{-7}$ & * \\
\hline water -HS ${ }^{-}$ & $1.60 \cdot 10^{-1}$ & $-3.60 \cdot 10^{-3}$ & 0 & 0 & * \\
\hline
\end{tabular}
\end{table}
*This work ** No literature or experimental data available.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 7
Parameters used for Equation (34) to calculate binary interaction parameters. $\boldsymbol{\boldsymbol { l } _ { \boldsymbol { i } \boldsymbol { j } }}$}
\begin{tabular}{lllll}
\hline Binary System & $\mathrm{l}_{\mathrm{ij}, \mathrm{a}}^{\mathrm{hb}}$ & $\mathrm{l}_{\mathrm{ij}, \mathrm{T}}^{\mathrm{hb}}$ & $\mathrm{l}_{\mathrm{ij}, \mathrm{T}^{2}}^{\mathrm{hb}}$ & Ref. \\
\hline water-MDEA & $6.00 \cdot 10^{-1}$ & $-2.57 \cdot 10^{-3}$ & $-1.70 \cdot 10^{-5}$ & $*$ \\
water -MDEAH $^{+}$ & $3.72 \cdot 10^{-1}$ & $1.07 \cdot 10^{-3}$ & 0 & $*$ \\
\hline
\end{tabular}
\end{table}
*This work.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-06.jpg?height=501&width=839&top_left_y=1246&top_left_x=133}
\captionsetup{labelformat=empty}
\caption{Fig. 1. p-x diagram of the system water-MDEA with experimental data taken from Kim et al. [52] ( 313 K : diamonds, 333 K : circles, 353 K : squares, 373 K : triangles ) and modeling results with ePC-SAFT (lines). ARD $=8.85 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-06.jpg?height=500&width=812&top_left_y=1970&top_left_x=144}
\captionsetup{labelformat=empty}
\caption{Fig. 2. p-y diagram of the system water-MDEA with experimental data taken from Kim et al. [52] ( 313 K : diamonds, 333 K :circles, 353 K : squares and 373 K : triangles ) and modeling results with ePC-SAFT (lines). ARD $=10.85 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-06.jpg?height=520&width=832&top_left_y=940&top_left_x=1070}
\captionsetup{labelformat=empty}
\caption{Fig. 3. $\mathrm{p}-\mathrm{x}$ diagram of the system water- $\mathrm{CH}_{4}$ with experimental data taken from Chapoy et al. [53] ( 275 K : diamonds, 283 K : circles, 298 K : squares and 313 K : triangles ) and modeling results with ePC-SAFT (lines). ARD $=4.76 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-06.jpg?height=518&width=847&top_left_y=1644&top_left_x=1061}
\captionsetup{labelformat=empty}
\caption{Fig. 4. $\mathrm{p}-\mathrm{x}, \mathrm{y}$ diagram of the system water- $\mathrm{H}_{2} \mathrm{~S}$ with experimental data taken from Lee and Mather [54] ( 311 K : squares, 344 K : circles and 377 K : triangles ) and modeling results with ePC-SAFT (lines). ARD $=19.08 \%$.}
\end{figure}

\subsection*{6.1.4. Binary pair: water-MDEAH ${ }^{+}$}

As the mixture water-MDEA was correlated with the binary parameters $\mathrm{k}_{\mathrm{ij}}$ and $\mathrm{l}_{\mathrm{ij}}^{\mathrm{hb}}$, this procedure was also applied to the pair water-MDEAH ${ }^{+}$. Thus, $\mathrm{k}_{\mathrm{ij}}$ and $\mathrm{l}_{\mathrm{ij}}^{\mathrm{hb}}$ between water and MDEAH ${ }^{+}$ were adjusted to experimentally determined osmotic coefficients $\phi$

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-07.jpg?height=507&width=843&top_left_y=228&top_left_x=163}
\captionsetup{labelformat=empty}
\caption{Fig. 5. $\mathrm{p}-\mathrm{x}$ diagram of the system $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ with experimental data from Neumann and Walch [55] ( 223 K : triangles, 259 K : circles, 271 K : squares) and modeling results with ePC-SAFT (lines). ARD $=4.80 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-07.jpg?height=498&width=817&top_left_y=917&top_left_x=176}
\captionsetup{labelformat=empty}
\caption{Fig. 6. p-y diagram of the system $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ with experimental data from Neumann and Walch [55] ( 223 K : triangles, 259 K : circles, 271 K : squares) and modeling results with ePC-SAFT (lines). ARD $=8.71 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-07.jpg?height=550&width=798&top_left_y=1597&top_left_x=191}
\captionsetup{labelformat=empty}
\caption{Fig. 7. Osmotic coefficients of the system water- $\mathrm{NaHCO}_{3}$ for different molalities of $\mathrm{NaHCO}_{3} m_{\mathrm{NaHCO}_{3}, 0}$ and experimental data from Peiper and Pitzer [56] ( 287 K : circles and 318 K : squares) at ambient pressure with the $\mathrm{k}_{\mathrm{ij}}$ between water- $\mathrm{HCO}_{3}^{-}$shown in Table 6. $\mathrm{ARD}=1.05 \%$.}
\end{figure}
of the system water-MDEA-HCl at the temperatures 273 and 313 K and ambient pressure. These aqueous solutions contained equal molalities of HCl and MDEA resulting in a $\mathrm{pH}<2$. At these acidic conditions, more than $99 \mathrm{~mol} \%$ of initial MDEA is present as MDEAH ${ }^{+}$species [60]. The osmotic coefficients measured with freezing-point osmometer are listed in Table 8, those with vapor-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-07.jpg?height=440&width=710&top_left_y=226&top_left_x=1166}
\captionsetup{labelformat=empty}
\caption{Fig. 8. Absolute freezing-point depression data for the system water- $\mathrm{Na}_{2} \mathrm{~S}$ as a function of the initial molality of $\mathrm{Na}_{2} \mathrm{~S} m_{\mathrm{Na}_{2} \mathrm{~S}, 0}$ with experimental data from Pöschl [57] (triangles) and ePC-SAFT modeling results (line) with the parameters from Table 4 Table 7. $\mathrm{ARD}=1.39 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-07.jpg?height=502&width=808&top_left_y=889&top_left_x=1113}
\captionsetup{labelformat=empty}
\caption{Fig. 9. Boiling-point elevation data for the system water- $\mathrm{Na}_{2} \mathrm{~S}$ as a function of the initial molality of $\mathrm{Na}_{2} \mathrm{~S} m_{\mathrm{Na}_{2} \mathrm{~S}, \mathrm{O}}$ with experimental data from Bialik et al. [58] (squares) and ePC-SAFT modeling results (line) with the parameters from Table 4 - Table 7. $\mathrm{ARD}=16.63 \%$.}
\end{figure}
pressure osmometer are listed in Table 9. In the fitting procedure, the $\mathrm{k}_{\mathrm{ij}}$ of $\mathrm{MDEAH}^{+}-\mathrm{Cl}^{-}$was set to zero and the $\mathrm{k}_{\mathrm{ij}}$ of water- $\mathrm{Cl}^{-}$was taken from a previous work [36], yielding the binary parameters as listed in Tables 6 and 7. Applying these parameters yields the correlation result as shown in Fig. 10.

\section*{6.2. $\mathrm{CO}_{2}$ solubilites in reacting systems}

The VLE of the systems water-MDEA- $\mathrm{CO}_{2}$, water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ and water-MDEA- $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ were predicted using ePC-SAFT by accounting for the reaction equilibria and the resulting species distribution including electrolyte species. The pure-component parameters and binary interaction parameters (Table 4 to Table 7) were taken from literature or were determined in this work as shown in Section 6.1. The predictions of the VLEs are based on the composition of the liquid phase at a constant temperature (isothermal) and a fixed MDEA weight fraction $\mathrm{w}_{\text {MDEA }}$ in relation to the water/MDEA system using the isofugacity criteria as shown in Section 3 Equation (3). The model predictions are based on speciation predictions. We observed an increase in the mole fraction of $\mathrm{H}^{+}$from $3.80 \cdot 10^{-11}$ up to $3.32 \cdot 10^{-9}$ in the gas loading range of 0.02 $<\alpha<1.4 \mathrm{~mol} \mathrm{CO}_{2} / \mathrm{mol}$ MDEA. This decrease in pH was accompanied by an increase in the mole fraction of MDEAH ${ }^{+}$from $9.80 \cdot 10^{-4}$ to $3.37 \cdot 10^{-2}$ at $\mathrm{T}=313 \mathrm{~K}$ and $\mathrm{w}_{\text {MDEA }}=0.23$. Additionally, the mole fraction of the species MDEA, MDEAH ${ }^{+}, \mathrm{HCO}_{3}^{-}$and $\mathrm{CO}_{3}^{2-}$ was found to be in very good agreement to experimental speciation data

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 8
Osmotic coefficients of the system water-MDEA- HCl with equal molalities of MDEA and $\mathrm{HCl}\left(\mathrm{m}_{\text {MDEA }}=\mathrm{m}_{\mathrm{HCl}}\right)$ measured in this work at 273 K and ambient pressure.}
\begin{tabular}{|l|l|l|}
\hline $\mathrm{m}_{\text {MDEA }}=\mathrm{m}_{\mathrm{HCl}}$ & mol $\mathrm{kg}_{\text {water }}$ & $\phi$ \\
\hline \multicolumn{2}{|l|}{0.411} & $0.835 \pm 0.0030$ \\
\hline 0.546 & & $0.845 \pm 0.0005$ \\
\hline 0.676 & & $0.838 \pm 0.0007$ \\
\hline 0.784 & & $0.839 \pm 0.0006$ \\
\hline 0.957 & & $0.854 \pm 0.0034$ \\
\hline 1.023 & & $0.860 \pm 0.0012$ \\
\hline 1.093 & & $0.861 \pm 0.0028$ \\
\hline
\end{tabular}
\end{table}

Standard uncertainties u are $\mathrm{u}(\mathrm{T})=0.1 \mathrm{~K}$ and $\mathrm{u}(\phi)=0.005$.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 9
Osmotic coefficients of the system water-MDEA- HCl with equal molalities of MDEA and $\mathrm{HCl}\left(\mathrm{m}_{\text {MDEA }}=\mathrm{m}_{\mathrm{HCl}}\right)$ measured in this work at 313 K and ambient pressure.}
\begin{tabular}{l|l|l}
\hline $\mathrm{m}_{\text {MDEA }}=\mathrm{m}_{\mathrm{HCl}}$ & $\frac{\mathrm{mol}}{\mathrm{kg}_{\text {water }}}$ & $\phi$ \\
\hline 0.403 & $0.869 \pm 0.0178$ \\
0.677 & $0.861 \pm 0.0003$ \\
1.141 & $0.874 \pm 0.0031$ \\
\hline
\end{tabular}
\end{table}

Standard uncertainties u are $\mathrm{u}(\mathrm{T})=0.1 \mathrm{~K}$ and $\mathrm{u}(\phi)=0.005$.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-08.jpg?height=535&width=804&top_left_y=1132&top_left_x=150}
\captionsetup{labelformat=empty}
\caption{Fig. 10. Osmotic coefficients $\phi$ of the system water-MDEA- HCl with equal molalities of MDEA and HCl as a function of the initial molality of MDEA $\mathrm{m}_{\text {MDEA, } 0}$ at 273 K (circles) and 313 K (triangles) at ambient pressure and the ePC-SAFT modeling results calculated with the parameters from Table 4 - Table 7. ARD = 5.05\%.}
\end{figure}
available in the literature. These results are not shown here because they do not differ much compared to the results in the previous publication by Uyan et al.

\subsection*{6.2.1. VLE water-MDEA-CO2}

Since the relevant mole fraction of MDEA in a water- MDEA absorption system for industrial processes is about $\mathrm{w}_{\text {MDEA }} \geq 0.32$ [61,62] predictions of the VLE water-MDEA- $\mathrm{CO}_{2}$ were performed for MDEA weight fractions of $0.32,0.48$ and 0.6 . For the MDEA weight fraction $\mathrm{w}_{\text {MDEA }}=0.32$ predictions by Uyan et al. have already been reported in literature [24]. These predictions were compared to the experimental data from Kuranov et al. [13] for temperatures between $313 \mathrm{~K}<\mathrm{T}<413 \mathrm{~K}$ and $\mathrm{CO}_{2}$ loadings of up to 1.4 mol CO 2 per mole MDEA. Uyan et al. [24] were capable of predicting the VLE with an ARD of approximately $26 \%$, while the predictions of this work, using newly determined binary interaction parameters not fitted to the experimental data of the ternary system, show an ARD of approximately $19 \%$. Especially predictions at the low temperature region $\leq 333 \mathrm{~K}$ could be improved. The results

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-08.jpg?height=497&width=823&top_left_y=236&top_left_x=1070}
\captionsetup{labelformat=empty}
\caption{Fig. 11. Isothermal VLE of the system water-MDEA- $\mathrm{CO}_{2}$ at $\mathrm{w}_{\text {MDEA }}=0.32$. Experimental data from Kurvanov et al. [13]. ( 313 K : reversed triangles, 333 K : circles, 373 K : triangles, 393 K : squares and 413 K : diamonds). ePC-SAFT predictions (parameters from Table 4 to Table 7) are represented by lines and yield $\mathrm{ARD}=19.44 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-08.jpg?height=501&width=835&top_left_y=955&top_left_x=1067}
\captionsetup{labelformat=empty}
\caption{Fig. 12. Isothermal VLE of the system water-MDEA- $\mathrm{CO}_{2}$ at $\mathrm{w}_{\text {MDEA }}=0.48$. Experimental data taken from Kurvanov et al. [13]. ( 313 K : reversed triangles and 353 K : triangles). ePC-SAFT predictions (parameters from Table 4 to Table 7) are represented by lines and yield $\mathrm{ARD}=34.96 \%$.}
\end{figure}
of the predictions as well as the experimental data are shown in Fig. 11.

In the following, ePC-SAFT predictions were performed for the ternary VLE water-MDEA- $\mathrm{CO}_{2}$ at $\mathrm{w}_{\text {MDEA }}=0.48$. Compared to the experimental data from Kuranov et al. [13]. between 313 K and 353 K yields an ARD of about $35 \%$, caused by an overestimation of the $\mathrm{CO}_{2}$ absorption for the low gas loading region $\alpha \leq 0.5 \mathrm{~mol} \mathrm{CO}_{2} /$ mole MDEA at 353 K . It is noteworthy that the absolute deviation is small compared to the relative value, due to the low partial pressure of $\mathrm{CO}_{2}$ measured in this region. The results of the ePCSAFT predicted $\mathrm{CO}_{2}$ solubilities are compared to experimental literature data presented in Fig. 12.

Another comparison between experimental data [14] and predictions with ePC-SAFT for mixed MDEA weight fractions and temperatures is shown in Fig. 13.

Due to unavailable experimental data concerning the VLE water-MDEA- $\mathrm{CO}_{2}$ for MDEA weight fraction above 0.48 experimental data for $\mathrm{w}_{\text {MDEA }}=0.6$ were measured in this work at 303 K . The experimental values are shown in Table 10.
ePC-SAFT allowed a prediction of the experimental data with an ARD of $10 \%$ for a temperature of 303 K in the gas loading region of $0.9 \leq \alpha \leq 1.1$. The results of the prediction and the experimental data are shown in Fig. 14.

As shown in Figs. 11-14, ePC-SAFT allows predicting the VLE of water-MDEA- $\mathrm{CO}_{2}$ for MDEA weight fractions up to 0.6 in

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-09.jpg?height=505&width=843&top_left_y=232&top_left_x=159}
\captionsetup{labelformat=empty}
\caption{Fig. 13. Isothermal VLE of the system water-MDEA- $\mathrm{CO}_{2}$ for different MDEA weight fractions and temperatures. Experimental data taken from Sidi-Boumedine et al. ( 298 K and $\mathrm{w}_{\text {mdea }}=0.38$ : reverse triangles, 348 K and $\mathrm{w}_{\text {MDEA }}=0.42$ : squares, 313 K and $\mathrm{w}_{\text {MDEA }}=0.47$ : diamonds). ePC-SAFT predictions (parameters from Table 4 to Table 7) are represented by lines ( 298 K and $\mathrm{w}_{\text {MDEA }}=0.38$ ©, 348 K and $\mathrm{w}_{\text {MDEA }}=0.42$ \&c, 313 K and $\mathrm{w}_{\text {MDEA }}=0.47$ © ) and yield $\mathrm{ARD}=34.96$.}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 10
Experimental data for the VLE of water-MDEA- $\mathrm{CO}_{2}$ for MDEA weight fraction of 0.6 and a temperature of 303 K . ${ }^{\text {a }}$}
\begin{tabular}{ll}
\hline$\alpha\left[\frac{\mathrm{mol} \mathrm{CO}}{\mathrm{mol} \mathrm{MDEA}, 0}\right]$ & $\mathrm{p}[\mathrm{bar}]$ \\
\hline 0.9374 & 9.2 \\
0.9973 & 14.2 \\
1.0448 & 24.5 \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}}$ Standard uncertainties u are $\mathrm{u}(\mathrm{T})=0.1 \mathrm{~K}, \mathrm{u}(\mathrm{p})=0.3$ bar, $\mathrm{u}(\alpha)=0.001$.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-09.jpg?height=490&width=819&top_left_y=1433&top_left_x=174}
\captionsetup{labelformat=empty}
\caption{Fig. 14. Isothermal VLE of the system water-MDEA- $\mathrm{CO}_{2}$ at $\mathrm{w}_{\text {MDEA }}=0.6$. Experimental data measured in this work ( 303 K : circles). ePC-SAFT predictions (parameters from Table 4 to Table 7) are represented by line and yield ARD $=10.25 \%$.}
\end{figure}
reasonable to good agreement to experimental data since no parameters where fit to the ternary system. An overview of the ARD of the predicted results for the VLE water-MDEA-CO2 in the MDEA weight fraction interval between 0.19 and 0.48 in comparison to Uyan et al. and other models in the literature is given in Table 11.

This work highlights the importance of acquiring reliable experimental data especially of the binary subsystems involved in the complex reaction mixture existing in the reacting system wa-ter-MDEA- $\mathrm{CO}_{2}$. In this work, eight binary parameters were fit to new osmotic-coefficient data in the subsystems water-MDEAH ${ }^{+}$ and water- $\mathrm{HCO}_{3}^{-}$. This was necessary to improve the VLE prediction results of the system water-MDEA- $\mathrm{CO}_{2}$. The prediction of Uyan et al.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 11
Comparison of the ARD of the prediction of the VLE water-MDEA-CO2 for the MDEA weight fraction between $19 \%$ and $48 \%$, using different models from literature, the work of Uyan et al. and this work for a temperature region of $313 \mathrm{~K}-413 \mathrm{~K}$ and a gas loading of up to $1.2 \mathrm{~mol} \mathrm{CO}_{2} /$ mole MDEA.}
\begin{tabular}{|l|l|l|l|}
\hline Model & Fit parameters ${ }^{\text {a }}$ & Data points & ARD/\% \\
\hline Electrolyte Peng-Robinson [20] & 5 & 81 & 10.1 \\
\hline Fürst and Renon EOS [63] & 4 & 81 & 17.8 \\
\hline Electrolyte Soave-Redlich-Kwong [41] & 5 & 64 & 20.0 \\
\hline Uyan et al. [24] & 0 & 82 & $34.4{ }^{\text {b }}$ \\
\hline This work & 0 & 82 & 19.7 \\
\hline
\end{tabular}
\end{table}
${ }^{\mathrm{a}}$ Number of binary interaction parameters fit to experimental data of the ternary system water-MDEA- $\mathrm{CO}_{2}$.
${ }^{\text {b }}$ Please note that the ARD in the work of Uyan et al. [24] has been re-determined. The ARD in the publication [24] was incorrect, and the value given in this table has to be used.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-09.jpg?height=518&width=832&top_left_y=848&top_left_x=1104}
\captionsetup{labelformat=empty}
\caption{Fig. 15. Isothermal VLE of the system water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ at $\mathrm{w}_{\text {MDEA }}=0.32$. Experimental data from Jou et al. [64] ( 298 K : reversed triangles, 313 K : circles, 343 K : triangles, 373 K : squares and 393 K : diamonds). ePC-SAFT predictions (parameters from Table 4 to Table 7) are represented by lines and yield $\mathrm{ARD}=13.48 \%$.}
\end{figure}
[24] could be strongly improved and even extended to higher MDEA concentrations. This is important as especially the region of $\mathrm{w}_{\text {MDEA }} \geq 0.32$ is relevant industrially. An overall deviation of ARD $<20 \%$ for $0.19 \leq \mathrm{w}_{\text {MDEA }} \leq 0.6$ and $313 \mathrm{~K}<\mathrm{T}<413 \mathrm{~K}$ means a good approach away from purely qualitative, towards quantitative predictions. This is important in systems of high MDEA concentrations, in which increased viscosity of the water-MDEA absorption system causes experimental difficulties [61,62] and first reliable approximations prove to be useful.

\subsection*{6.2.2. VLE water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$}

As mentioned in the introduction, water-MDEA mixtures systems are not only used for the absorption of $\mathrm{CO}_{2}$ but are also used for the absorption of the acid gas $\mathrm{H}_{2} \mathrm{~S}$. ePC-SAFT was used to predict VLE of the system water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ at $\mathrm{w}_{\text {MDEA }}=\{0.32 ; 0.48\}$. Data for higher MDEA weight fraction were not available in literature. The predictions were based on the pure-component ePC-SAFT parameters for water, MDEA, and $\mathrm{H}_{2} \mathrm{~S}$ and $\mathrm{HS}^{-}$according to Table 4 to Table 7. Fig. 15 compares the ePC-SAFT prediction results for $\mathrm{w}_{\text {MDEA }}=0.32$ with experimental data from Jou et al. [64] for temperatures between 298 K and 393 K and $\mathrm{H}_{2} \mathrm{~S}$ loadings $\alpha$ up to $1.8 \mathrm{~mol} \mathrm{H}_{2} \mathrm{~S} / \mathrm{mol}$ MDEA.

Fig. 15 shows an good agreement between ePC-SAFT predicted and experimental data. The key to this prediction result is the good description of the binary subsystems and points to the importance of osmotic-coefficient data of electrolyte solutions. For the VLE of

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-10.jpg?height=505&width=854&top_left_y=232&top_left_x=124}
\captionsetup{labelformat=empty}
\caption{Fig. 16. Isothermal VLE of the system water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ at $\mathrm{w}_{\text {MDEA }}=0.48$. Experimental data from Sidi-Boumedine et al. [65] ( 313 K : reversed triangles, 373 K : squares) and Kamps et al. [19] ( 393 K : diamonds). ePC-SAFT predictions (parameters from Table 4 to Table 7) are represented by lines and yield ARD $=27.36 \%$.}
\end{figure}
the system water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ at $\mathrm{w}_{\text {MDEA }}=0.48$ experimental data from Sidi-Boumedine et al. [65] for the temperature of 313 K and 373 K and experimental data from Kamps et al. [19] for 393 K were available.

Fig. 16 illustrates the limit of the model for the VLE of the system water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ at $\mathrm{w}_{\text {MDEA }}=0.48$ between 313 K and 373 K . While a good prediction for the temperature of 313 K is observed, predictions of the higher temperatures show a more significant deviation from experimental data. A comparison of the predicted VLE water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ with ePC-SAFT and other models from literature is given in Table 12, showing that ePC-SAFT is able to predict $\mathrm{H}_{2} \mathrm{~S}$ solubilities in water/MDEA solutions with an accuracy that is comparable to other models that are used correlatively instead of predictively.

\subsection*{6.2.3. VLE water-MDEA- $\mathrm{CO}_{2}-\mathrm{CH}_{4}$}

Until here it was shown that ePC-SAFT allows reasonable predictions of gas solubility in water-MDEA mixtures in broad ranges of temperature, gas loading, and MDEA concentration. In this section, the influence of the inert gas $\mathrm{CH}_{4}$ on the VLE of the system water-MDEA- $\mathrm{CO}_{2}$ was studied at $\mathrm{w}_{\text {MDEA }}=\{0.3$ and 0.5$\}$. In order to predict the VLEs of these systems, the initial ratio between $\mathrm{CO}_{2}$ and $\mathrm{CH}_{4}$ was given as input according to the experimental data (and initial $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ ratios) from Addicks and Owren [4]. The results for the prediction of the quaternary VLE in comparison with experimental data for the temperatures 313 K and 353 K for $\mathrm{w}_{\text {MDEA }}=\{0.3$ and 0.5\} are shown in Figs. 17 and 18.

As seen in Figs. 17 and 18, a good agreement for $\mathrm{w}_{\text {MDEA }}=0.3$ and only a qualitative agreement for $\mathrm{w}_{\text {MDEA }}=0.5$ for 353 K was found between ePC-SAFT predicted and experimental $\mathrm{CH}_{4}$ influence on the $\mathrm{CO}_{2}$ solubility. Unfortunately, there are no other experimental data for this system, and even more the uncertainty of the data is not known.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 12
Comparison of the ARD of the prediction of the VLE water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ for the MDEA weight fraction between $19 \%$ and $48 \%$, using different models from literature and this work for a temperature region of $298 \mathrm{~K}-393 \mathrm{~K}$ and a gas loading of up to $1.8 \mathrm{~mol} \mathrm{H}_{2} \mathrm{~S} / \mathrm{mol}$ MDEA.}
\begin{tabular}{|l|l|l|l|}
\hline Model & Fit parameters ${ }^{\text {a }}$ & NP & ARD \\
\hline Quasichemical hole model [66] & 1 & 61 & 13.7 \\
\hline Kamps et al. [67] & 6 & 105 & 45.0 \\
\hline This work & 0 & 114 & 19.1 \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-10.jpg?height=498&width=839&top_left_y=232&top_left_x=1063}
\captionsetup{labelformat=empty}
\caption{Fig. 17. Isothermal VLE of the system water-MDEA- $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ at an MDEA weight fraction of $\mathrm{w}_{\text {MDEA }}=0.3$ with experimental data taken from Addicks and Oeren [4] ( 313 K : reversed triangles and 353 K : triangles) and the predictions with ePC-SAFT using parameters from Table 4 to Table 6 (lines). ARD $=14.39 \%$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-10.jpg?height=495&width=835&top_left_y=1011&top_left_x=1067}
\captionsetup{labelformat=empty}
\caption{Fig. 18. Isothermal VLE of the system water-MDEA- $\mathrm{CO}_{2}-\mathrm{CH}_{4}$ at an MDEA weight fraction of $\mathrm{w}_{\text {MDEA }}=0.5$ with experimental data taken from Addicks and Oeren [4] ( 313 K : reversed triangles and 353 K : triangles) and the predictions with ePC-SAFT using parameters from Table 4 to Table 6 (lines). ARD $=56.10 \%$.}
\end{figure}

\subsection*{6.3. Enthalpy of absorption}

Additionally to gas solubility, the enthalpy of absorption for the system water-MDEA-CO2 was predicted with ePC-SAFT. For that purpose, the speciation of the system components was required. The results of the ePC-SAFT predictions were compared to experimental data from Arcis [68] at $\mathrm{w}_{\text {MDEA }}=0.3$ and $\mathrm{T}=322 \mathrm{~K}$ as well as from Mathonat [69] at $\mathrm{w}_{\text {MDEA }}=0.3$ and $\mathrm{T}=\{353 \mathrm{~K} ; 393 \mathrm{~K}\}$. The results are shown in Figs. 19-21.

It can be seen from the experimental data that the enthalpies of absorption decrease with temperature and with $\mathrm{CO}_{2}$ loading. Both effects can be predicted with ePC-SAFT, illustrated in the generally good agreement between experimental data from literature (Figs. 19-21) and prediction results. ePC-SAFT seems to overestimate the temperature influence at loadings lower than 1 mol $\mathrm{CO}_{2}$ per mole MDEA. Nevertheless, the results presented here are new in the manner that - as far as the authors know - no thermodynamic approach has been applied so far to predict enthalpy of absorption in gas-amine-water systems so far. Key to this success is a good prediction of the reaction equilibria as well as the correct description of concentration and temperature influences on the activity coefficients of the reacting agents.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-11.jpg?height=489&width=817&top_left_y=228&top_left_x=176}
\captionsetup{labelformat=empty}
\caption{Fig. 19. Comparison of the experimental enthalpy of absorption $\Delta \mathrm{H}^{\text {abs }}$ per mole $\mathrm{CO}_{2}$ in a water-MDEA system at $\mathrm{w}_{\text {MDEA }}=0.3$ at $\mathrm{T}=322 \mathrm{~K}$ from Arcis [68] (squares) with ePCSAFT predictions using the parameters from Table 3 to Table 7 (lines).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-11.jpg?height=500&width=835&top_left_y=900&top_left_x=167}
\captionsetup{labelformat=empty}
\caption{Fig. 20. Comparison of the experimental enthalpy of absorption $\Delta \mathrm{H}^{\text {abs }}$ per mole $\mathrm{CO}_{2}$ in a water-MDEA system at $\mathrm{w}_{\text {MDEA }}=0.3$ at $\mathrm{T}=353 \mathrm{~K}$ from Mathonat [69] (reversed triangles) with ePC-SAFT predictions using the parameters from Table 3 to Table 7 (lines).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7e08e019-aa37-471d-b326-ab095f65b576-11.jpg?height=500&width=832&top_left_y=1580&top_left_x=165}
\captionsetup{labelformat=empty}
\caption{Fig. 21. Comparison of the experimental enthalpy of absorption $\Delta \mathrm{H}^{\mathrm{abs}}$ per mole $\mathrm{CO}_{2}$ in a water-MDEA system at $\mathrm{w}_{\text {MDEA }}=0.3$ at $\mathrm{T}=393 \mathrm{~K}$ from Mathonat [69] (circles) with ePC-SAFT predictions using the parameters from Table 3 to Table 7 (lines).}
\end{figure}

\section*{7. Conclusions}

Literature proposes many models focused on modeling the VLE of water-MDEA- $\mathrm{CO}_{2} / \mathrm{H}_{2} \mathrm{~S}$ systems. The accuracy of these models varies due to the amount of parameters that were fit to experimental data of the system modeled, requiring experimental data of the ternary systems. The focus of this work was to predict gas
solubility in water-MDEA systems for broad ranges of MDEA weight fractions, temperature, and gas loading. It was found that ePC-SAFT allows a reasonable prediction of the two ternary VLE water-MDEA- $\mathrm{CO}_{2}$ and water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ without fitting ePC-SAFT parameters to experimental data of the respective ternary system. The predictions for the VLE water-MDEA- $\mathrm{CO}_{2}$ could be extended to a MDEA weight fraction up to 0.6 , while the prediction of the VLE water-MDEA- $\mathrm{H}_{2} \mathrm{~S}$ was limited by the lack of experimental data for MDEA weight fractions above 0.48 . The predictions, while still not always quantitatively correct, are significantly better than any prediction found in the literature. The key for that was to account for the activities of all reacting species and especially those of the charged species in the reaction and phase equilibrium calculations. To better describe the interactions, new binary parameters between water- $\mathrm{MDEAH}{ }^{+}$, water- $\mathrm{HCO}_{3}^{-}$, and water- $\mathrm{HS}^{-}$were found to be necessary, which were fit to osmotic-coefficient data from this work or from literature.

The availability of a predictive model for the speciation and phase equilibrium calculations in ternary water-MDEA-gas systems allowed studying the effect of the inert component $\mathrm{CH}_{4}$ on the $\mathrm{CO}_{2}$ solubility in water-MDEA systems as well as enthalpy of absorption. A reasonably good accuracy between ePC-SAFT predictions and experimental data was observed, which is an important step into the quantitative modeling of gas solubility in multi-component process streams with close-to-reality gas compositions. Besides gas solubility, enthalpy of absorption in the water-MDEA- $\mathrm{CO}_{2}$ system was predicted with ePC-SAFT by adding enthalpy of reaction, enthalpy of the physical dissolution of $\mathrm{CO}_{2}$ and the excess enthalpy. The predictions were found to be accurate both, in terms of dependencies on temperature and on gas loadings.

To conclude, this work shows that ePC-SAFT allows for reasonable to good predictions of gas solubilities in water-MDEA systems at broad ranges of temperature, MDEA concentration, and gas loading. Further, the influence of inert gas as well as enthalpy of absorption could be predicted. This is very relevant in terms of the application of an electrolyte equation of state to screen amines for gas absorption processes and will help to reduce the experimental effort behind by approximation to take a further step towards being quantitative.

\section*{Acknowledgment}

We thank our lab assistant Nicolette Keil for support and measurements with the vapor-pressure osmometry. CH thanks Gabriele Sadowski for all her valuable time for discussions!

\section*{References}
[1] Y. Zhang, H. Chen, C.-C. Chen, J.M. Plaza, R. Dugas, G.T. Rochelle, Rate-based process modeling study of $\mathrm{CO2}$ capture with aqueous monoethanolamine solution, Ind. Eng. Chem. Res. 48 (2009) 9233-9246.
[2] J. Hansen, S. Lebedeff, Global trends of measured surface air temperature, J. Geophys. Res. Atmos. 92 (1987) 13345-13372.
[3] L. Meng Hui, S. Keh Perng, Solubility of Hydrogen Sulfide in Aqueous Mixtures of Monoethanolamine with N-methyldiethanolamine, 1993.
[4] J. Addicks, G.A. Owren, A.O. Fredheim, K. Tangvik, Solubility of carbon dioxide and methane in aqueous methyldiethanolamine solutions, J. Chem. Eng. Data 47 (2002) 855-860.
[5] S.Z.S. Al Ghafri, E. Forte, G.C. Maitland, J.J. Rodriguez-Henríquez, J.P.M. Trusler, Experimental, Modeling, Study of the phase behavior of (methane $+\mathrm{CO} 2+$ water) mixtures, J. Phys. Chem. B 118 (2014) 14461-14478.
[6] Y.E. Kim, J.A. Lim, S.K. Jeong, Y.I. Yoon, S.T. Bae, S.C. Nam, Comparison of carbon dioxide absorption in aqueous MEA, DEA, TEA, and AMP solutions, Bull. Kor. Chem. Soc. 34 (2013) 783-787.
[7] H. Kierzkowska-Pawlak, Enthalpies of absorption and solubility of $\mathrm{CO2}$ in aqueous solutions of methyldiethanolamine, Separ. Sci. Technol. 42 (2007) 2723-2737.
[8] A.L. Kohl, R.B. Nielsen, Gas purification, Gulf Publishing Company, Houston, 1997.
[9] M. Gupta, E.F. da Silva, A. Hartono, H.F. Svendsen, Theoretical study of differential enthalpy of absorption of CO2 with MEA and MDEA as a function of temperature, J. Phys. Chem. B 117 (2013) 9457-9468.
[10] M.S. Jassim, G.T. Rochelle, Innovative absorber/stripper configurations for CO2 capture by aqueous monoethanolamine, Ind. Eng. Chem. Res. 45 (2006) 2465-2472.
[11] S.-W. Rho, K.-P. Yoo, J.S. Lee, S.C. Nam, J.E. Son, B.-M. Min, Solubility of CO2 in aqueous methyldiethanolamine solutions, J. Chem. Eng. Data 42 (1997) 1161-1164.
[12] D.M. Austgen, G.T. Rochelle, C.C. Chen, Model of vapor-liquid equilibria for aqueous acid gas-alkanolamine systems. 2. Representation of hydrogen sulfide and carbon dioxide solubility in aqueous MDEA and carbon dioxide solubility in aqueous mixtures of MDEA with MEA or DEA, Ind. Eng. Chem. Res. 30 (1991) 543-555.
[13] G. Kuranov, B. Rumpf, N.A. Smirnova, G. Maurer, Solusssbility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of N-Methyldiethanolamine in the temperature range $313-413 \mathrm{~K}$ at pressures up to 5 MPa, Ind. Eng. Chem. Res. 35 (1996) 1959-1966.
[14] R. Sidi-Boumedine, S. Horstmann, K. Fischer, E. Provost, W. Fürst, J. Gmehling, Experimental determination of carbon dioxide solubility data in aqueous alkanolamine solutions, Fluid Phase Equil. 218 (2004) 85-94.
[15] M.L. Posey, G.T. Rochelle, A thermodynamic model of Methyl-diethanolamine-CO2-H2S-Water, ind, Eng. Chem. Res. 36 (1997) 3944-3953.
[16] V.D. Pitsinigos, A.I. Lygeros, Predicting H/sub 2/S-MEA Equilibria, 1989.
[17] Y. Zhang, C.-C. Chen, Thermodynamic modeling for CO2 absorption in aqueous MDEA solution with electrolyte NRTL model, Ind. Eng. Chem. Res. 50 (2011) 163-175.
[18] U.E. Aronu, S. Gondal, E.T. Hessen, T. Haug-Warberg, A. Hartono, K.A. Hoff, H.F. Svendsen, Solubility of CO2 in 15, 30, 45 and 60 mass\% MEA from 40 to $120^{\circ} \mathrm{C}$ and model representation using the extended UNIQUAC framework, Chem. Eng. Sci. 66 (2011) 6393-6406.
[19] A.P.-S. Kamps, A. Balaban, M. Jödecke, G. Kuranov, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of N-Methyldiethanolamine at temperatures from 313 to 393 K and pressures up to 7.6 MPa : new experimental data and model extension, Ind. Eng. Chem. Res. 40 (2001) 696-706.
[20] A.T. Zoghi, F. Feyzi, M.R. Dehghani, Modeling CO2 solubility in aqueous Nmethyldiethanolamine solution by electrolyte modified peng-robinson Plus association equation of state, Ind. Eng. Chem. Res. 51 (2012) 9875-9885.
[21] J.K. Button, K.E. Gubbins, SAFT prediction of vapour-liquid equilibria of mixtures containing carbon dioxide and aqueous monoethanolamine or diethanolamine, Fluid Phase Equil. 158-160 (1999) 175-181.
[22] J. Rodriguez, N. Mac Dowell, F. Llovell, C.S. Adjiman, G. Jackson, A. Galindo, Modelling the fluid phase behaviour of aqueous mixtures of multifunctional alkanolamines and carbon dioxide using transferable parameters with the SAFT-VR approach, Mol. Phys. 110 (2012) 1325-1348.
[23] H. Pahlavanzadeh, S. Fakouri Baygi, Modeling CO2 solubility in aqueous methyldiethanolamine solutions by perturbed chain-SAFT equation of state, Zh. Khim. Termodin. Termokhim. 59 (2013) 214-221.
[24] M. Uyan, G. Sieder, T. Ingram, C. Held, Predicting CO2 solubility in aqueous Nmethyldiethanolamine solutions with ePC-SAFT, Fluid Phase Equil. 393 (2015) 91-100.
[25] K. Nasrifar, A.H. Tafazzol, Vapor-Liquid equilibria of acid Gas-Aqueous ethanolamine solutions using the PC-SAFT equation of state, Ind. Eng. Chem. Res. 49 (2010) 7620-7630.
[26] J. Addicks, Solubility of carbon dioxide and methane in aqueous N-methyldiethanol solutions at pressures between 100 and 200 bar, 2002.
[27] H. Arcis, L. Rodier, K. Ballerat-Busserolles, J.-Y. Coxam, Modeling of (vapor + liquid) equilibrium and enthalpy of solution of carbon dioxide (CO2) in aqueous methyldiethanolamine (MDEA) solutions, Zh. Khim. Termodin. Termokhim. 41 (2009) 783-789.
[28] R. Span, W. Wagner, A new equation of state for carbon dioxide covering the fluid region from the triple-point temperature to 1100 K at pressures up to 800 MPa , J. Phys. Chem. Ref. Data 25 (1996) 1509-1596.
[29] M. Kleiner, F. Tumakaka, G. Sadowski, Thermodynamic Modeling of Complex Systems, in, Springer Berlin Heidelberg, Berlin, Heidelberg, pp. 1-34.
[30] J.A. Barker, D. Henderson, Perturbation theory and equation of state for fluids: the square-well potential, J. Chem. Phys. 47 (1967) 2856-2861.
[31] C. Held, A. Prinz, V. Wallmeyer, G. Sadowski, Measuring and modeling alcohol/ salt systems, Chem. Eng. Sci. 68 (2012) 328-339.
[32] C. Held, T. Reschke, R. Müller, W. Kunz, G. Sadowski, Measuring and modeling aqueous electrolyte/amino-acid solutions with ePC-SAFT, Zh. Khim. Termodin. Termokhim. 68 (2014) 1-12.
[33] M. Sadeghi, C. Held, A. Samieenasab, C. Ghotbi, M.J. Abdekhodaie, V. Taghikhani, G. Sadowski, Thermodynamic properties of aqueous salt containing urea solutions, Fluid Phase Equil. 325 (2012) 71-79.
[34] C. Held, L.F. Cameretti, G. Sadowski, Modeling aqueous electrolyte solutions: Part 1. Fully dissociated electrolytes, Fluid Phase Equil. 270 (2008) 87-96.
[35] L.F. Cameretti, G. Sadowski, J.M. Mollerup, Modeling of aqueous electrolyte solutions with perturbed-chain statistical associated fluid theory, Ind. Eng. Chem. Res. 44 (2005) 3355-3362.
[36] C. Held, T. Reschke, S. Mohammad, A. Luza, G. Sadowski, ePC-SAFT revised, Chem. Eng. Res. Des. 92 (2014) 2884-2897.
[37] A. Nann, C. Held, G. Sadowski, Liquid-liquid equilibria of 1-butanol/water/IL systems, Ind. Eng. Chem. Res. 52 (2013) 18472-18481.
[38] H.A. Lorentz, Ueber die Anwendung des Satzes vom Virial in der kinetischen Theorie der Gase, Ann. Phys. 248 (1881) 127-136.
[39] D. Berthelot, Sur le mélange des gaz, Compt. Rendus 126 (1898) 1703-1706.
[40] J.P. Wolbach, S.I. Sandler, Using molecular orbital calculations to describe the phase behavior of cross-associating mixtures, Ind. Eng. Chem. Res. 37 (1998) 2917-2928.
[41] P.J.G. Huttenhuis, N.J. Agrawal, J.A. Hogendoorn, G.F. Versteeg, Gas solubility of H 2 S and CO 2 in aqueous solutions of N-methyldiethanolamine, J. Petrol. Sci. Eng. 55 (2007) 122-134.
[42] C.S. Patterson, G.H. Slocum, R.H. Busey, R.E. Mesmer, Carbonate equilibria in hydrothermal systems: first ionization of carbonic acid in NaCl media to $300^{\circ} \mathrm{C}$, Geochem. Cosmochim. Acta 46 (1982) 1653-1663.
[43] C.S. Patterson, R.H. Busey, R.E. Mesmer, Second ionization of carbonic acid in NaCl media to 250 C, J. Solut. Chem. 13 (1984) 647-661.
[44] Á. Pérez-Salado Kamps, G. Maurer, Dissociation constant of N-Methyldiethanolamine in aqueous solution at temperatures from 278 K to 368 K , J. Chem. Eng. Data 41 (1996) 1505-1513.
[45] M. Luckas, J. Krissmann, Thermodynamik der Elektrolytlösungen: eine einheitliche Darstellung der Berechnung komplexer Gleichgewichte, SpringerVerlag, 2013.
[46] M. Kleiner, Thermodynamic Modeling of Complex Systems: Polar and Associating Fluids and Mixtures, Verlag Dr. Hut, 2009.
[47] F.A. Aly, L.L. Lee, Self-consistent equations for calculating the ideal gas heat capacity, enthalpy, and entropy, Fluid Phase Equil. 6 (1981) 169-179.
[48] T.L. Hill, J. Gillis, An Introduction to Statistical Thermodynamics, AIP, 1961.
[49] Y. Yan, C.-C. Chen, Thermodynamic modeling of CO2 solubility in aqueous solutions of NaCl and Na2SO4, J. Supercrit. Fluids 55 (2010) 623-634.
[50] D. Fuchs, J. Fischer, F. Tumakaka, G. Sadowski, Solubility of amino Acids: influence of the pH value and the addition of alcoholic cosolvents on aqueous solubility, Ind. Eng. Chem. Res. 45 (2006) 6578-6584.
[51] J. Gross, G. Sadowski, Perturbed-chain SAFT: an equation of state based on a perturbation theory for chain molecules, Ind. Eng. Chem. Res. 40 (2001) 1244-1260.
[52] I. Kim, H.F. Svendsen, E. Børresen, Ebulliometric determination of Vapor--Liquid equilibria for pure water, monoethanolamine, N-Methyldiethanolamine, 3-(Methylamino)-propylamine, and their binary and ternary solutions, J. Chem. Eng. Data 53 (2008) 2521-2531.
[53] A. Chapoy, A.H. Mohammadi, D. Richon, B. Tohidi, Gas solubility measurement and modeling for methane-water and methane-ethane-n-butane-water systems at low temperature conditions, Fluid Phase Equil. 220 (2004) 111-119.
[54] J.I. Lee, A.E. Mather, Solubility of hydrogen sulfide in water, Ber. BunsenGesellschaft 81 (1977) 1020-1023.
[55] A. Neumann, W. Walch, Vapour/liquid equilibrium carbon dioxide/methane at low temperatures and in region of low carbon dioxide mole fractions, Chem. Ing. Tech. 40 (1968) 241.
[56] J.C. Peiper, K.S. Pitzer, Thermodynamics of aqueous carbonate solutions including mixtures of sodium carbonate, bicarbonate, and chloride, Zh. Khim. Termodin. Termokhim. 14 (1982) 613-638.
[57] K. Pöschl, Landolt-Börnstein. Zahlenwerte und Funktionen aus Physik, Chemie, Astronomie, Geophysik und Technik. 6, in: Auflage. Hrsg, von J. Bartels, P. Ten Bruggencate, H. Hausen, K.H. Hellwege (Eds.), Kl. Schäfer und E. Schmidt. Band IV Technik, Teil 3: Elektrotechnik - Lichttechnik Röntgentechnik. Hrsg. von Ernst Schmidt. XV, 1076 Seiten mit $2117 \mathrm{Abb} .4^{\circ}$, vol. 62, Springer-Verlag, Berlin-Göttingen-Heidelberg 1957. Preis: DM 396, 1958, p. 491. Ber. Bunsen-Ges.
[58] M. Bialik, P. Sedin, H. Theliander, Boiling point rise calculations in sodium salt solutions, Ind. Eng. Chem. Res. 47 (2008) 1283-1287.
[59] D. Lide, CRC handbook of chemistry and physics, J. Am. Chem. Soc. 129 (2007), 724-724.
[60] B. Hawrylak, R. Palepu, P.R. Tremaine, Thermodynamics of aqueous methyldiethanolamine (MDEA) and methyldiethanolammonium chloride (MDEAH+Cl-) over a wide range of temperature and pressure: apparent molar volumes, heat capacities, and isothermal compressibilities, Zh. Khim. Termodin. Termokhim. 38 (2006) 988-1007.
[61] S. Ma'mun, R. Nilsen, H.F. Svendsen, O. Juliussen, Solubility of carbon dioxide in 30 mass $\%$ monoethanolamine and 50 mass $\%$ methyldiethanolamine solutions, J. Chem. Eng. Data 50 (2005) 630-634.
[62] F. Pani, A. Gaunand, R. Cadours, C. Bouallou, D. Richon, Kinetics of absorption of $\mathrm{CO}_{2}$ in concentrated aqueous methyldiethanolamine solutions in the range 296 K to 343 K, J. Chem. Eng. Data 42 (1997) 353-359.
[63] P.W.J. Derks, J.A. Hogendoorn, G.F. Versteeg, Experimental and theoretical study of the solubility of carbon dioxide in aqueous blends of piperazine and N-methyldiethanolamine, Zh. Khim. Termodin. Termokhim. 42 (2010) 151-163.
[64] F.Y. Jou, A.E. Mather, F.D. Otto, Solubility of H/sub 2/S and CO/sub 2/in aqueous methyldiethanolamine solutions, Ind. Eng. Chem. Process Des. Dev. 21 (1982).
[65] R. Sidi-Boumedine, S. Horstmann, K. Fischer, E. Provost, W. Fürst, J. Gmehling, Experimental determination of hydrogen sulfide solubility data in aqueous alkanolamine solutions, Fluid Phase Equil. 218 (2004) 149-155.
[66] G. Kuranov, B. Rumpf, G. Maurer, N. Smirnova, VLE modelling for aqueous systems containing methyldiethanolamine, carbon dioxide and hydrogen sulfide, Fluid Phase Equil. 136 (1997) 147-162.
[67] Á.P.-S. Kamps, A. Balaban, M. Jödecke, G. Kuranov, N.A. Smirnova, G. Maurer, Solubility of single gases carbon dioxide and hydrogen sulfide in aqueous solutions of N-methyldiethanolamine at temperatures from 313 to 393 K and pressures up to 7.6 MPa : new experimental data and model extension, Ind. Eng. Chem. Res. 40 (2001) 696-706.
[68] H. Arcis, Etude thermodynamique de la dissolution du dioxyde de carbone dans des solutions aqueuses d'alcanolamines, PhD Thesis in Chemistry, Blaise Pascal University, Clermont-Ferrand II, 2008.
[69] C. Mathonat, Calorimétrie de mélange, à écoulement, à températures et pressions élevées. Application à l'étude de l'élimination du dioxyde de carbone à l'aide de solutions aqueuses d'alcanolamines, PhD Thesis in Chemistry, Blaise Pascal University, Clermont-Ferrand II, 1995.