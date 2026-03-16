########################################################
# ingest un general assembly voting data
# source: voeten agreement scores (local from carbon)
# output: data/processed/unga_agreement.rda
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)

# load voeten agreement scores
agree_file = file.path(data_raw, 'AgreementScores_latest.Rdata')
if (!file.exists(agree_file)) {
	download.file('https://dataverse.harvard.edu/api/access/datafile/11837232',
		agree_file, mode = 'wb')
}
load(agree_file)

# clean and map to iso3
unga_clean = dfAgree %>%
	select(cow_code1 = ccode1, cow_code2 = ccode2, year, agree,
		ideal_pt_dist = IdealPointDistance) %>%
	filter(year >= MIN_YEAR, !is.na(agree)) %>%
	mutate(
		iso3_1 = cow_to_iso3(cow_code1),
		iso3_2 = cow_to_iso3(cow_code2)
	) %>%
	filter(!is.na(iso3_1), !is.na(iso3_2),
		iso3_1 %in% registry$iso3, iso3_2 %in% registry$iso3,
		iso3_1 != iso3_2) %>%
	# for countries with same iso3 (e.g. old/new germany), deduplicate
	group_by(iso3_1, iso3_2, year) %>%
	summarize(agree = mean(agree, na.rm = TRUE),
		ideal_pt_dist = mean(ideal_pt_dist, na.rm = TRUE),
		.groups = 'drop')

validate_actor_coverage(unique(c(unga_clean$iso3_1, unga_clean$iso3_2)), 'UNGA')

# country counts by decade
yr_counts = unga_clean %>%
	group_by(year) %>%
	summarize(n_ctry = length(unique(c(iso3_1, iso3_2))), .groups = 'drop')

save(unga_clean, file = file.path(data_proc, 'unga_agreement.rda'))
