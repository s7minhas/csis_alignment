########################################################
# download recent bilateral trade data from wits api
# extends trade coverage from 2020 to 2023
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

library(httr)
library(jsonlite)
library(xml2)

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)

# define reporters to query
# wits uses iso3 codes for reporters
reporters = sort(unique(c(
	'USA', 'CHN', 'GBR', 'DEU', 'FRA', 'JPN', 'CAN', 'ITA',
	'KOR', 'AUS', 'IND', 'BRA', 'RUS', 'ZAF', 'MEX', 'IDN',
	'TUR', 'SAU', 'ARE', 'EGY', 'NGA', 'PAK', 'IRN', 'ISR',
	'THA', 'VNM', 'PHL', 'MYS', 'SGP', 'ARG', 'COL', 'CHL',
	'POL', 'NLD', 'ESP', 'SWE', 'NOR', 'CHE', 'BEL', 'UKR',
	'KAZ', 'QAT', 'KEN', 'ETH', 'DZA', 'IRQ', 'MAR', 'NZL',
	'IRL', 'PER', 'CUB', 'VEN', 'GRC', 'PRT', 'MMR', 'JOR'
)))

years = 2021:2023

# parse wits sdmx xml response
parse_wits_xml = function(xml_text) {
	tryCatch({
		doc = read_xml(xml_text)

		# series elements contain PARTNER attribute; obs children contain OBS_VALUE
		series = xml_find_all(doc, './/*[local-name()="Series"]')
		if (length(series) == 0) return(NULL)

		results = lapply(series, function(s) {
			partner = xml_attr(s, 'PARTNER')
			obs = xml_find_all(s, './/*[local-name()="Obs"]')
			if (length(obs) == 0 || is.na(partner)) return(NULL)
			value = as.numeric(xml_attr(obs[[1]], 'OBS_VALUE'))
			if (is.na(value) || value <= 0) return(NULL)
			tibble(partner = partner, value = value)
		})

		bind_rows(results)
	}, error = function(e) NULL)
}

# download bilateral exports for each reporter-year
all_trade = list()
failed = character()

for (yr in years) {
	for (rep in reporters) {
		url = sprintf(
			'https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/%s/year/%d/partner/all/product/Total/indicator/XPRT-TRD-VL',
			rep, yr)

		resp = tryCatch(GET(url, timeout(20)), error = function(e) NULL)

		if (!is.null(resp) && status_code(resp) == 200) {
			txt = content(resp, as = 'text', encoding = 'UTF-8')
			parsed = parse_wits_xml(txt)

			if (!is.null(parsed) && nrow(parsed) > 0) {
				all_trade[[length(all_trade) + 1]] = parsed %>%
					mutate(reporter = rep, year = yr)
			}
		} else {
			failed = c(failed, paste(rep, yr))
		}

		Sys.sleep(0.5)  # rate limit
	}
}

if (length(all_trade) > 0) {
	trade_wits = bind_rows(all_trade)

	# map partner codes to iso3 (wits partner codes are already iso3)
	trade_wits = trade_wits %>%
		rename(iso3_1 = reporter, iso3_2 = partner, trade_value = value) %>%
		filter(iso3_1 != iso3_2,
			iso3_1 %in% registry$iso3,
			iso3_2 %in% registry$iso3) %>%
		mutate(
			log_trade = log(trade_value + 1)
		) %>%
		# compute trade dependency
		group_by(iso3_1, year) %>%
		mutate(total_exports = sum(trade_value, na.rm = TRUE)) %>%
		ungroup() %>%
		mutate(trade_dep = trade_value / pmax(total_exports, 1))

	# merge with existing trade data
	load(file.path(data_proc, 'trade.rda'))

	trade_extended = bind_rows(
		trade_clean %>% select(iso3_1, iso3_2, year, trade_value, trade_dep, log_trade),
		trade_wits %>% select(iso3_1, iso3_2, year, trade_value, trade_dep, log_trade)
	) %>%
		group_by(iso3_1, iso3_2, year) %>%
		summarize(across(everything(), ~mean(.x, na.rm = TRUE)), .groups = 'drop')

	# save
	trade_clean = trade_extended
	save(trade_clean, file = file.path(data_proc, 'trade.rda'))
	save(trade_wits, file = file.path(data_proc, 'trade_wits_recent.rda'))
}
