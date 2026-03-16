########################################################
# build actor registry
# produces: actors_master.csv, group_membership.csv
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

# build master actor list from countrycode
# start with all countries that have a cow code
all_cow = countrycode::codelist %>%
	filter(!is.na(cown), !is.na(iso3c)) %>%
	select(iso3c, cown, country.name.en, un) %>%
	distinct(iso3c, .keep_all = TRUE) %>%
	rename(
		iso3 = iso3c,
		cow_code = cown,
		name_common = country.name.en,
		un_code = un
	) %>%
	mutate(is_un_member = !is.na(un_code))

# manual additions/fixes for critical countries
# ensure china is present with correct cow code
if (!'CHN' %in% all_cow$iso3) {
	all_cow = bind_rows(all_cow, tibble(
		iso3 = 'CHN', cow_code = 710,
		name_common = 'China', un_code = 156, is_un_member = TRUE
	))
}
# ensure taiwan
if (!'TWN' %in% all_cow$iso3) {
	all_cow = bind_rows(all_cow, tibble(
		iso3 = 'TWN', cow_code = 713,
		name_common = 'Taiwan', un_code = NA, is_un_member = FALSE
	))
}

# fix any duplicate cow codes (keep most recent / standard)
all_cow = all_cow %>%
	group_by(iso3) %>%
	slice_head(n = 1) %>%
	ungroup()

# add region info
all_cow$region_un = countrycode::countrycode(
	all_cow$iso3, 'iso3c', 'un.region.name', warn = FALSE)
all_cow$region_wb = countrycode::countrycode(
	all_cow$iso3, 'iso3c', 'region', warn = FALSE)
all_cow$continent = countrycode::countrycode(
	all_cow$iso3, 'iso3c', 'continent', warn = FALSE)

# anchor flags
all_cow$is_anchor = all_cow$iso3 %in% c('USA', 'CHN')

# sort and save
actors_master = all_cow %>%
	arrange(iso3)

write_csv(actors_master, file.path(data_reg, 'actors_master.csv'))

# validate critical countries
validate_actor_coverage(actors_master$iso3, 'actors_master')

# build group membership
group_membership = actors_master %>%
	select(iso3, cow_code, name_common) %>%
	mutate(
		continent = countrycode::countrycode(iso3, 'iso3c', 'continent', warn = FALSE),
	) %>%
	mutate(
		g7 = iso3 %in% c('USA', 'GBR', 'FRA', 'DEU', 'ITA', 'JPN', 'CAN'),
		g7_plus = g7 | iso3 %in% c('AUS', 'KOR'),
		brics_original = iso3 %in% c('BRA', 'RUS', 'IND', 'CHN', 'ZAF'),
		brics_plus = brics_original | iso3 %in% c('EGY', 'ETH', 'IRN', 'ARE', 'SAU'),
		nato = iso3 %in% c(
			'USA', 'GBR', 'FRA', 'DEU', 'ITA', 'CAN', 'BEL', 'NLD', 'LUX',
			'DNK', 'NOR', 'ISL', 'PRT', 'GRC', 'TUR', 'ESP', 'POL', 'CZE',
			'HUN', 'BGR', 'ROU', 'SVK', 'SVN', 'EST', 'LVA', 'LTU', 'HRV',
			'ALB', 'MNE', 'MKD', 'FIN', 'SWE'),
		eu = iso3 %in% c(
			'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN',
			'FRA', 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX',
			'MLT', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'),
		asean = iso3 %in% c(
			'BRN', 'KHM', 'IDN', 'LAO', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM'),
		sco = iso3 %in% c(
			'CHN', 'RUS', 'IND', 'PAK', 'IRN', 'KAZ', 'KGZ', 'TJK', 'UZB'),
		african_union = continent == 'Africa',
		arab_league = iso3 %in% c(
			'DZA', 'BHR', 'COM', 'DJI', 'EGY', 'IRQ', 'JOR', 'KWT', 'LBN',
			'LBY', 'MRT', 'MAR', 'OMN', 'PSE', 'QAT', 'SAU', 'SOM', 'SDN',
			'SYR', 'TUN', 'ARE', 'YEM'),
		oecd = iso3 %in% c(
			'AUS', 'AUT', 'BEL', 'CAN', 'CHL', 'COL', 'CRI', 'CZE', 'DNK',
			'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ISR',
			'ITA', 'JPN', 'KOR', 'LVA', 'LTU', 'LUX', 'MEX', 'NLD', 'NZL',
			'NOR', 'POL', 'PRT', 'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'TUR',
			'GBR', 'USA'),
		global_south = !oecd & !iso3 %in% c('RUS')  # simplified definition
	) %>%
	select(-continent)

write_csv(group_membership, file.path(data_reg, 'group_membership.csv'))
