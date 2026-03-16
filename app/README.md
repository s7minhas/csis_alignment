# Dynamic Alignment Observatory

**Mapping diplomatic alignment and trade dependence across the international system.**

Interactive dashboard tracking diplomatic alignment (UNGA voting) and trade dependence (bilateral trade flows) across 193 countries (1990–2024).

Developed by [Shahryar Minhas](https://s7minhas.com) (Michigan State University) in collaboration with the [Center for Strategic and International Studies (CSIS)](https://www.csis.org).

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Docker

```bash
docker build -t csis-alignment-observatory .
docker run -p 8501:8501 csis-alignment-observatory
```

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo, branch `master`, main file `app.py`
5. Deploy

## Data

All data files are in `data/`. To update with new UNGA voting data:

1. Download latest Voeten Agreement Scores from [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LEJUQZ)
2. Run the R pipeline in the parent `csis/R/` directory
3. Copy updated CSVs to `data/`
