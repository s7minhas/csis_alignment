########################################################
# actor registry helper functions
########################################################

#' look up iso3 from cow code
cow_to_iso3 = function(cow_codes) {
	countrycode::countrycode(cow_codes, 'cown', 'iso3c',
		custom_match = c(
			'710' = 'CHN',
			'713' = 'TWN',
			'260' = 'DEU',
			'255' = 'DEU',
			'265' = 'DEU',
			'345' = 'SRB',
			'347' = 'XKX',
			'511' = 'TZA',
			'678' = 'YEM',
			'679' = 'YEM',
			'817' = 'VNM',
			'816' = 'VNM'
		))
}

#' look up cow code from iso3
iso3_to_cow = function(iso3_codes) {
	countrycode::countrycode(iso3_codes, 'iso3c', 'cown',
		custom_match = c(
			'CHN' = 710,
			'TWN' = 713,
			'DEU' = 260,
			'SRB' = 345,
			'XKX' = 347,
			'TZA' = 511,
			'YEM' = 678,
			'VNM' = 816
		))
}

#' validate that critical countries are present in a dataset
validate_actor_coverage = function(iso3_vec, label = '') {
	critical = c('USA', 'CHN', 'RUS', 'GBR', 'FRA', 'DEU',
		'JPN', 'IND', 'BRA', 'ZAF', 'KOR', 'SAU',
		'IRN', 'ISR', 'TUR', 'AUS', 'CAN', 'ITA',
		'MEX', 'IDN', 'NGA', 'PAK', 'EGY', 'ARE')
	missing = setdiff(critical, iso3_vec)
	if (length(missing) > 0) {
		warning(sprintf('[%s] Missing critical countries: %s',
			label, paste(missing, collapse = ', ')))
	}
	invisible(missing)
}
