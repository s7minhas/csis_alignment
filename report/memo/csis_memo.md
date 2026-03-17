# Dynamic Alignment Observatory

## Measuring Diplomatic Position-Taking Across 193 Countries

**Prepared for CSIS by Shahryar Minhas (Michigan State University)**
**March 2026**

---

### The Problem

Diplomatic alignment between states is one of the most consequential features of the international system, yet it remains difficult to measure systematically. Policymakers frequently invoke alignment and realignment in broad terms, but existing measures tend to rely on static categories (ally versus adversary) or isolated bilateral indicators. These approaches obscure the underlying structure of the diplomatic landscape: which states are converging, which are diverging, and how quickly.

The Dynamic Alignment Observatory addresses this measurement problem by applying a network-based statistical model to UN General Assembly voting records covering 193 countries from 1990 to 2024. The approach captures not only how often two states vote alike but how each state relates to the broader coalition structure of the General Assembly, producing a continuous alignment score for every country pair in every year. This allows analysts to track diplomatic repositioning as it unfolds rather than inferring it after the fact.

### How the Measure Works

The diplomatic alignment measure is built from the complete record of UNGA roll-call votes. Rather than simply counting agreement rates between pairs of countries, the model estimates a latent factor structure that characterizes each country's position in the broader voting network. A longitudinal additive and multiplicative effects model (LAME) with dynamic latent positions identifies the underlying configuration that best accounts for observed voting patterns across all dyads and years simultaneously. Countries that consistently participate in the same voting coalitions are estimated to occupy similar positions in this latent space, even on resolutions where one of them abstains. Because UNGA voting is symmetric (agreement between A and B is the same as agreement between B and A), the model estimates a single latent position per country in each year. The result is a set of country-year positions from which pairwise alignment scores, anchor-relative measures (distance to US and Chinese positions), and bloc-level summaries can be derived.

The same LAME framework is applied separately to directed bilateral trade flows (IMF Direction of Trade Statistics and World Bank WITS, 1990 to 2023). Because trade is inherently directed, with exports from A to B differing from exports from B to A, the model estimates two sets of latent positions for each country: sender positions capturing structural similarities in export profiles, and receiver positions capturing structural similarities in import profiles. As Minhas et al. argue in "Taking Dyads Seriously" (2022), properly modeling directed networks requires maintaining this distinction rather than collapsing sender and receiver roles into a single position. Countries with similar sender positions export to similar destinations; countries with similar receiver positions import from similar sources. This provides a second dimension of alignment that captures the structure of economic relationships in a way that raw trade shares cannot.

### Key Findings

BRICS and G7 diplomatic cohesion have moved in different directions. Average diplomatic alignment among BRICS members fell from 0.87 in 1990 to 0.75 in 2024, while G7 cohesion declined modestly from 0.87 to 0.86. The gap between the two blocs widened over the period. This pattern becomes visible only through a dynamic, dyad-level measure of the kind constructed here; snapshot or region-level summaries would not capture it.

South Korea's diplomatic alignment with the US rose from 0.61 in 1990 to 0.69 in 2024, a sustained shift that reflects Seoul's deepening integration into the US-led democratic alliance structure. While modest in absolute terms, this increase is notable because most countries' alignment with the US has been flat or declining over the same period.

The post-Soviet space illustrates how geographic neighbors can follow sharply divergent diplomatic trajectories. Since 2000, Ukraine shifted roughly half a point toward US positions, the single largest move in the dataset, while Kazakhstan shifted a comparable amount toward China. These opposing movements are not captured by region-level summaries or static alliance categories. They become visible only through a dynamic, country-level measure of the kind constructed here.

A pervasive structural feature of the UNGA is that the United States votes in small minorities on a large share of resolutions, typically joined only by Israel and a handful of other states. As a consequence, most countries in the world, including many close US security partners, appear diplomatically closer to China than to the US when measured through General Assembly voting. This pattern reflects genuine differences in diplomatic position-taking on issues such as Palestinian statehood, nuclear disarmament, and economic sovereignty. It does not indicate that these countries are Chinese allies, but it does mean that the tilt measure is most informative when used comparatively across countries and over time rather than as an absolute indicator.

India's voting record illustrates the gap between diplomatic position-taking and bilateral security relationships. India-China agreement at the UNGA (about 0.78) is nearly twice India-US agreement (about 0.41). Both India and China champion positions associated with the Global South on questions of sovereignty, development, and non-intervention, even as India maintains active border disputes with China and deepens security cooperation with the United States. This divergence between UNGA positioning and bilateral strategic relationships is precisely the kind of structure that analysts should be attentive to when interpreting alignment scores.

### Scope and Interpretation

The alignment scores capture one important dimension of interstate relations: public diplomatic position-taking at the United Nations. Trade relationships, military cooperation, intelligence sharing, summit diplomacy, and crisis behavior operate through separate channels and are not reflected here. Countries such as Japan, South Korea, and India maintain deep security and economic ties with the United States while voting differently at the General Assembly. The measure is therefore most useful as one input into a broader assessment of alignment rather than a standalone indicator.

Scores are normalized within each year, meaning that a given value reflects a country's relative position in that year's alignment distribution rather than an absolute threshold. Large movements over time are substantively meaningful, but small year-to-year fluctuations may reflect changes in the composition of the voting agenda rather than genuine diplomatic shifts. Because the United States occupies an outlier position in UNGA voting, the tilt measure differentiates more effectively among Western-aligned countries than among the many Global South states that cluster at similar distances from the US.

### The Dashboard

The interactive dashboard provides several views of the data. A world map with a toggle between diplomatic alignment and trade alignment displays either dimension for any year from 1990 to 2024, along with a scatter plot showing where the two dimensions diverge. The country explorer produces a full profile for any state, combining diplomatic and trade alignment scores relative to the US, China, the G7, and BRICS, with combined trajectory charts showing both dimensions over time. The dyad comparison tool tracks diplomatic alignment between any two countries over time with reference benchmarks. The bloc dashboard presents within-group cohesion and member-level scores for G7, BRICS, BRICS+, NATO, ASEAN, and the Global South. The diplomatic alignment space displays the two-dimensional latent positions underlying the UNGA voting scores on a circular layout, with an option to color countries by trade alignment or diplomacy-trade divergence. The trade alignment space applies the same circular layout to the directed trade network, placing each country twice: once as an exporter (outer ring) and once as an importer (inner ring), so that countries with similar export or import profiles cluster together.

### Planned Extensions

Event-level data from the Integrated Crisis Early Warning System (ICEWS), which records government-to-government cooperative and conflictual interactions, could produce higher-frequency measures of alignment at monthly or quarterly intervals. This would capture acute shifts in relations that annual UNGA voting necessarily misses.

A second extension would decompose alignment by issue area. UNGA resolutions address distinct topics, including Middle East affairs, human rights, nuclear policy, climate, and sovereignty. Running separate models by issue domain would reveal where coalitions overlap and where they diverge, identifying issue-specific opportunities for diplomatic engagement that aggregate scores obscure.

### Academic Foundations

This work builds on Gallop and Minhas, "A Network Approach to Measuring State Preferences" (*Network Science*); Choi, de Marchi, Gallop, and Minhas, "Decisive or Distracted: the Effects of US Constraint on Security Networks" (*British Journal of Political Science*, 2024); Minhas, Hoff, and Ward, "Taking Dyads Seriously" (2022); and Voeten, "Clashes in the Assembly" (*International Organization*, 2000). The statistical methodology employs a longitudinal additive and multiplicative effects model with dynamic latent positions, estimated via Bayesian MCMC. The approach to directed trade networks follows the framework in "Taking Dyads Seriously," which demonstrates the importance of estimating separate sender and receiver latent positions rather than assuming symmetric relationships. Raw voting data comes from Erik Voeten's UN General Assembly voting dataset hosted at Harvard Dataverse.

---

**Contact**: Shahryar Minhas (minhassh@msu.edu) · David Peng (DPeng@csis.org)
