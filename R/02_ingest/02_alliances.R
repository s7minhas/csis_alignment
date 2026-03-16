########################################################
# ingest alliance data
# source: atop v2026 (local from carbon)
# output: data/processed/alliances.rda
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)

# load atop alliance data
load('/home/s7m/Dropbox/Research/Carbon/Data/Binaries/atop_v2026.rda')

# clean and map to iso3
alliance_clean = totAlly %>%
	rename(cow_code1 = ccode1, cow_code2 = ccode2, ally_total = allyTotal) %>%
	filter(year >= MIN_YEAR) %>%
	mutate(
		iso3_1 = cow_to_iso3(cow_code1),
		iso3_2 = cow_to_iso3(cow_code2)
	) %>%
	filter(!is.na(iso3_1), !is.na(iso3_2),
		iso3_1 %in% registry$iso3, iso3_2 %in% registry$iso3,
		iso3_1 != iso3_2) %>%
	group_by(iso3_1, iso3_2, year) %>%
	summarize(ally_total = max(ally_total, na.rm = TRUE), .groups = 'drop')

# extend alliances to 2024 (carry forward -- alliances are sticky)
max_ally_year = max(alliance_clean$year)
if (max_ally_year < MAX_YEAR) {
	last_year_data = alliance_clean %>% filter(year == max_ally_year)
	for (yr in (max_ally_year + 1):MAX_YEAR) {
		alliance_clean = bind_rows(alliance_clean,
			last_year_data %>% mutate(year = yr))
	}
}

validate_actor_coverage(unique(c(alliance_clean$iso3_1, alliance_clean$iso3_2)), 'Alliances')

save(alliance_clean, file = file.path(data_proc, 'alliances.rda'))
