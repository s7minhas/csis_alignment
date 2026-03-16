"""Interpretive text, caveats, and methodology content."""

CAVEAT_BOX = """
> **What this measures, and what it does not.**
>
> The diplomatic alignment scores on this dashboard reflect **position-taking
> at the UN General Assembly** — how similarly two countries vote on
> international resolutions covering sovereignty, human rights, security, and
> related issues. The trade dependence figures reflect **bilateral trade
> shares** — what fraction of a country's imports and exports flow to or from
> a given partner.
>
> Neither measure captures the full bilateral relationship. Countries can
> vote similarly at the UNGA while maintaining serious bilateral tensions
> (India and China both vote with the Global South bloc despite active border
> disputes). Countries can be major trade partners while voting on opposite
> sides of most resolutions (Australia trades heavily with China but votes
> with the US).
>
> The United States frequently votes in small minorities at the UNGA,
> typically alongside Israel and a handful of other states. As a result, most
> countries appear diplomatically closer to China than to the US in General
> Assembly voting. This is an accurate description of UNGA position-taking
> but should not be read as a measure of broader US influence or the strength
> of bilateral relationships.
"""

METHODOLOGY_FULL = """
## How This Works

### Data

**Diplomatic alignment** is derived from roll-call votes on every UN General
Assembly resolution from 1965 to 2024, covering 193 countries. The raw data
come from Erik Voeten's widely used
[UN voting dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LEJUQZ)
hosted at Harvard Dataverse. The model covers 193 countries from 1990 to 2024.

**Trade dependence** is derived from bilateral trade flows reported by the
IMF Direction of Trade Statistics (1990–2020) and the World Bank WITS database
(2021–2023). For each country in each year, we compute the share of total
trade (exports plus imports) conducted with each partner.

### Model

A statistical model called a **latent factor model** — specifically, a
longitudinal additive and multiplicative effects model (LAME) — estimates the
positions that best account for observed voting patterns. The model places
each country in a two-dimensional space where countries that consistently
participate in the same voting coalitions occupy nearby positions, and
countries that vote with opposing coalitions are placed far apart. These
positions update each year to capture how diplomatic alignments evolve.

This approach is more informative than simply counting how often two
countries vote the same way, because it captures indirect structure: if
France and Germany both vote with the same coalition of 50 countries, they
are estimated as aligned even on resolutions where one of them abstains.

Trade dependence does not pass through a statistical model. The trade shares
reported on the dashboard are computed directly from observed bilateral flows.

### Glossary of Terms

**Diplomatic alignment score** (0 to 1): How similarly two countries are
positioned in the UNGA voting network. A score of 1 means the two countries
vote identically across resolutions; a score of 0 means their voting patterns
are as different as any pair in the dataset that year. Computed from the
Euclidean distance between latent positions, normalized within each year.

**Trade dependence** (reported as a percentage): The share of a country's
total bilateral trade (exports plus imports) that flows to or from a
particular partner. For example, "Trade with China: 36%" means 36 percent
of that country's worldwide trade is with China.

**US-China tilt** (ranges from roughly -1 to +1): The difference between a
country's diplomatic alignment with the US and its diplomatic alignment with
China. Positive values mean the country votes more similarly to the US;
negative values mean it votes more similarly to China; values near zero mean
it is roughly equidistant.

**Bloc cohesion** (0 to 1): The average diplomatic alignment score across
all pairs of countries within a given group (e.g., G7, BRICS). Higher values
mean the group's members vote more similarly to one another. A cohesion of
0.93, for example, means the average pair within the group is very closely
aligned in UNGA voting.

**Trade US-China balance** (reported as a percentage difference): The
difference between a country's trade share with the US and its trade share
with China. Positive means the country trades more with the US; negative
means it trades more with China.

**Diplomacy-trade divergence**: Cases where a country's diplomatic
alignment and its trade dependence point in different directions relative to
the US and China. For example, a country that votes more like the US but
trades more with China exhibits a diplomacy-trade divergence.

### How Scores Are Computed

For each pair of countries in each year, the model produces a diplomatic
alignment score based on the Euclidean distance between their estimated
positions in the latent space. Distances are normalized within each year
so that the closest pair receives a score near 1 and the most distant pair
receives a score near 0.

For each country in each year, the dashboard reports diplomatic alignment
with the US (0 to 1), diplomatic alignment with China (0 to 1), and the
US-China tilt (the difference between the two). Bloc-level summaries
average these scores across group members. Trade dependence figures are
computed directly from bilateral trade data without modeling.

### Limitations

UNGA voting captures one dimension of interstate relations. Military
cooperation, intelligence sharing, summit diplomacy, and crisis behavior
operate through separate channels and are not reflected in the diplomatic
alignment scores. Trade dependence captures a second dimension but does
not account for the composition of trade, investment flows, or financial
linkages.

The United States frequently votes against supermajorities on issues such as
Palestinian statehood, nuclear disarmament, and economic sovereignty. As a
consequence, nearly every country appears more diplomatically aligned with
China than with the US. This pattern accurately describes UNGA
position-taking but does not characterize the broader bilateral relationship
between these countries and the US.

Coalition voting should not be conflated with bilateral friendship. India and
China vote similarly because both champion positions associated with the
Global South on sovereignty and development, not because they are strategic
partners. Russia and China have converged in UNGA voting over three decades,
which does reflect genuine strategic diplomatic alignment.

Scores are normalized within each year, meaning that a given score reflects
a country's position relative to the distribution of all scores in that year.
A value of 0.70 in 2000 and 0.70 in 2024 both indicate the 70th percentile
of diplomatic alignment in their respective years. This normalization is
necessary because the structure of the voting network changes over time as
new states join the UN and the issue agenda shifts. Large trends over time
are substantively meaningful, but small year-to-year fluctuations may
reflect changes in the reference distribution rather than real diplomatic
shifts.

Because the US occupies an outlier position in UNGA voting, the tilt score
differentiates effectively among Western-aligned countries but compresses
many Global South states into a narrow band. Small differences at the
China-aligned end of the distribution should not be over-interpreted.
Countries with few UNGA votes or irregular attendance produce less reliable
scores; small island states should be interpreted with particular care.

### Academic Foundations

This approach builds on Gallop and Minhas, "A Network Approach to Measuring
State Preferences" (*Network Science*); Choi, de Marchi, Gallop, and Minhas,
"Decisive or Distracted: the Effects of US Constraint on Security Networks"
(*British Journal of Political Science*, 2024); and Voeten, "Clashes in the
Assembly" (*International Organization*, 2000). The statistical methodology
employs a longitudinal additive and multiplicative effects model with dynamic
latent positions, estimated via Bayesian MCMC.
"""

ABOUT_TEXT = """
### About the Dynamic Alignment Observatory

This tool was developed as a collaboration between
[Shahryar Minhas](https://s7minhas.com) (Michigan State University) and the
[Center for Strategic and International Studies (CSIS)](https://www.csis.org).
It combines UN General Assembly voting data with bilateral trade flows to
measure both diplomatic alignment and trade dependence across all UN member
states.

**Contact**: David Peng (CSIS), Shahryar Minhas (MSU)

**Data updated through**: See landing page for latest year

**Code and methods**: Available upon request
"""


def format_alignment_description(score):
    """Return a plain-English description of a diplomatic alignment score."""
    if score >= 0.9:
        return "Very closely aligned diplomatically"
    elif score >= 0.7:
        return "Closely aligned diplomatically"
    elif score >= 0.5:
        return "Moderately aligned diplomatically"
    elif score >= 0.3:
        return "Weakly aligned diplomatically"
    elif score >= 0.15:
        return "Distantly positioned diplomatically"
    else:
        return "Very distantly positioned diplomatically"


def format_tilt_description(tilt):
    """Return a plain-English description of a US-China tilt score."""
    if tilt > 0.5:
        return "Votes substantially more like the US than China"
    elif tilt > 0.2:
        return "Votes somewhat more like the US than China"
    elif tilt > -0.2:
        return "Roughly equidistant between US and Chinese positions"
    elif tilt > -0.5:
        return "Votes somewhat more like China than the US"
    else:
        return "Votes substantially more like China than the US"
