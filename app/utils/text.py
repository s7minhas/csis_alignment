"""Interpretive text, caveats, and methodology content."""

CAVEAT_BOX = """
> **What this measures, and what it does not.**
> These scores reflect **diplomatic position-taking** at the UN General Assembly,
> specifically how similarly countries vote on international resolutions covering
> sovereignty, human rights, and security. High alignment means two countries
> take similar positions across these issue areas.
>
> Alignment in UNGA voting is **not** the same as being allies, trading partners,
> or friends. Countries can vote similarly while maintaining serious bilateral
> tensions. India and China, for example, both vote with the Global South bloc
> on many issues despite active border disputes.
>
> The US frequently votes in small minorities at the UNGA (typically with Israel
> and a few others), which places most countries closer to Chinese positions than
> to American ones. This reflects genuine differences in diplomatic position-taking,
> not a lack of US influence in the broader international system.
"""

METHODOLOGY_FULL = """
## How This Works

### Data
The underlying data consist of roll-call votes on every UN General Assembly
resolution from 1965 to 2024, covering **193 countries** and producing over
one million country-pair-year observations. The raw data come from Erik Voeten's
widely used
[UN voting dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LEJUQZ)
hosted at Harvard Dataverse. The model covers **193 countries from 1990 to 2024**.

### Model
A statistical model called a **latent factor model** (specifically, a longitudinal
additive and multiplicative effects model) estimates the underlying positions that
best account for observed voting patterns. The model places each country in a
latent space where countries that consistently participate in the same voting
coalitions occupy nearby positions, while countries that vote with opposing
coalitions are placed far apart. These positions update each year to capture
how diplomatic alignments evolve.

This approach is more informative than simply counting how often two countries
vote the same way. It captures indirect alignment: if France and Germany both
vote with the same coalition of 50 countries, they are estimated as aligned
even on resolutions where one of them abstains.

### Outputs
For each pair of countries in each year, the model produces a **Diplomatic
Alignment Score** (0 to 1), where 1 indicates identical positions and 0
indicates maximally dissimilar positions.

For each country in each year, the dashboard reports alignment with the US
(0 to 1), alignment with China (0 to 1), and the US-China tilt (the difference
between the two, where positive values indicate closer proximity to US positions
and negative values indicate closer proximity to Chinese positions).

### Limitations

UNGA voting captures one dimension of interstate relations. Countries interact
through trade, military cooperation, intelligence sharing, diplomatic exchanges,
and other channels not reflected here. The measure captures the public diplomatic
dimension only.

The United States frequently votes against supermajorities on issues such as
Palestinian statehood, nuclear disarmament, and economic sovereignty. As a
consequence, nearly every country appears more aligned with China than with
the US in General Assembly voting. This pattern is accurate for UNGA
position-taking but does not characterize the broader bilateral relationship.

Coalition voting should not be conflated with bilateral friendship. India and
China vote similarly because both champion Global South positions, not because
they are strategic partners. Russia and China have converged in UNGA voting
over three decades, which does reflect genuine strategic alignment.

Scores are normalized within each year. A value of 0.70 in 2000 and 0.70 in
2024 both indicate the 70th percentile of alignment in their respective years.
This normalization is necessary because the structure of the voting network
changes over time as new states join the UN and the issue agenda shifts.
Large trends over time are substantively meaningful, but small year-to-year
fluctuations may reflect changes in the reference distribution rather than
real diplomatic shifts.

Because the US occupies an outlier position, the tilt score differentiates
effectively among Western-aligned countries but compresses many Global South
states into a narrow band. Small differences at the China-aligned end of the
distribution should not be over-interpreted. Countries with few UNGA votes or
irregular attendance produce less reliable scores; the model accounts for this
through uncertainty estimation, but small states should be interpreted with care.

### Academic Foundations
This approach builds on Gallop and Minhas, "A Network Approach to Measuring
State Preferences" (*Network Science*); Choi, de Marchi, Gallop, and Minhas,
"Decisive or Distracted" (*British Journal of Political Science*, 2024); and
Voeten, "Clashes in the Assembly" (*International Organization*, 2000).
"""

ABOUT_TEXT = """
### About the Dynamic Alignment Observatory

This tool was developed as a collaboration between
[Shahryar Minhas](https://s7minhas.com) (Michigan State University) and the
[Center for Strategic and International Studies (CSIS)](https://www.csis.org).
It applies network-based statistical methods to UN General Assembly voting data
to produce a continuously updated measure of diplomatic alignment across all
UN member states.

**Contact**: David Peng (CSIS), Shahryar Minhas (MSU)

**Data updated through**: See landing page for latest year

**Code and methods**: Available upon request
"""


def format_alignment_description(score):
    """Return a plain-English description of an alignment score."""
    if score >= 0.9:
        return "Very closely aligned"
    elif score >= 0.7:
        return "Closely aligned"
    elif score >= 0.5:
        return "Moderately aligned"
    elif score >= 0.3:
        return "Weakly aligned"
    elif score >= 0.15:
        return "Distantly positioned"
    else:
        return "Very distantly positioned"


def format_tilt_description(tilt):
    """Return a plain-English description of a US-China tilt score."""
    if tilt > 0.5:
        return "Strongly tilted toward US positions"
    elif tilt > 0.2:
        return "Moderately tilted toward US positions"
    elif tilt > -0.2:
        return "Roughly equidistant between US and China"
    elif tilt > -0.5:
        return "Moderately tilted toward China's positions"
    else:
        return "Strongly tilted toward China's positions"
