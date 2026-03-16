########################################################
# ingest trade data
# source: imf dot via plutonium (1975-2020) + cow trade (1960-2014)
# output: data/processed/trade.rda
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)

# load imf dot trade data (from plutonium)
load('/home/s7m/Dropbox/Research/plutonium/data/imfData.rda')

# map countries to iso3
trade_clean = imfData %>%
	mutate(
		iso3_1 = countrycode::countrycode(cname1, 'country.name', 'iso3c', warn = FALSE),
		iso3_2 = countrycode::countrycode(cname2, 'country.name', 'iso3c', warn = FALSE)
	)

# use exportsFOB as main trade variable (directed: i exports to j)
trade_clean = trade_clean %>%
	filter(!is.na(iso3_1), !is.na(iso3_2),
		iso3_1 %in% registry$iso3, iso3_2 %in% registry$iso3,
		iso3_1 != iso3_2,
		year >= MIN_YEAR) %>%
	mutate(trade_value = coalesce(exportsFOB, exportsCIF, 0)) %>%
	filter(!is.na(trade_value), trade_value > 0) %>%
	# compute trade dependency: exports i->j / total exports of i
	group_by(iso3_1, year) %>%
	mutate(total_exports = sum(trade_value, na.rm = TRUE)) %>%
	ungroup() %>%
	mutate(
		trade_dep = trade_value / pmax(total_exports, 1),
		log_trade = log(trade_value + 1)
	) %>%
	select(iso3_1, iso3_2, year, trade_value, trade_dep, log_trade) %>%
	group_by(iso3_1, iso3_2, year) %>%
	summarize(across(everything(), ~mean(.x, na.rm = TRUE)), .groups = 'drop')

validate_actor_coverage(unique(c(trade_clean$iso3_1, trade_clean$iso3_2)), 'Trade')

save(trade_clean, file = file.path(data_proc, 'trade.rda'))
