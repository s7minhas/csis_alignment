########################################################
# descriptive analysis and report figures
# produces csis-ready visualizations
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load scores
has_lame = file.exists(file.path(data_proc, 'anchor_scores_lame.rda'))
if (has_lame) {
	load(file.path(data_proc, 'anchor_scores_lame.rda'))
	load(file.path(data_proc, 'lame_unga_scores.rda'))
	anchor = anchor_lame %>%
		left_join(groups %>% select(iso3, name_common, g7, brics_original, brics_plus,
		                            nato, asean, global_south, oecd),
		          by = c('country' = 'iso3'))
}

# us-china bilateral alignment over time
load(file.path(data_proc, 'unga_agreement.rda'))

us_china_agree = unga_clean %>%
	filter((iso3_1 == 'USA' & iso3_2 == 'CHN') |
	       (iso3_1 == 'CHN' & iso3_2 == 'USA')) %>%
	group_by(year) %>%
	summarize(agreement = mean(agree, na.rm = TRUE), .groups = 'drop')

p1 = ggplot(us_china_agree, aes(x = year, y = agreement)) +
	geom_line(linewidth = 1.2) +
	geom_smooth(method = 'loess', span = 0.3, se = TRUE, alpha = 0.2) +
	labs(title = 'US-China Diplomatic Alignment',
	     subtitle = 'UNGA voting agreement score, 1965-2024',
	     x = NULL, y = 'Agreement Score') +
	theme_csis() +
	geom_vline(xintercept = c(1972, 1989, 2001, 2014, 2022),
	           linetype = 'dashed', alpha = 0.3)

ggsave(file.path(res_figs, 'fig01_us_china_alignment.pdf'), p1, width = 10, height = 6)
ggsave(file.path(res_figs, 'fig01_us_china_alignment.png'), p1, width = 10, height = 6, dpi = 300)

# key dyad time series
key_dyads = tibble(
	iso3_1 = c('USA', 'USA', 'CHN', 'USA', 'USA', 'CHN'),
	iso3_2 = c('RUS', 'KOR', 'RUS', 'IND', 'SAU', 'IRN'),
	label = c('US-Russia', 'US-S.Korea', 'China-Russia',
	          'US-India', 'US-Saudi', 'China-Iran')
)

dyad_trends = unga_clean %>%
	inner_join(key_dyads, by = c('iso3_1', 'iso3_2')) %>%
	bind_rows(
		unga_clean %>%
			inner_join(key_dyads %>% rename(iso3_1_old = iso3_1, iso3_2_old = iso3_2) %>%
			             rename(iso3_1 = iso3_2_old, iso3_2 = iso3_1_old),
			           by = c('iso3_1', 'iso3_2'))
	) %>%
	group_by(label, year) %>%
	summarize(agreement = mean(agree, na.rm = TRUE), .groups = 'drop')

p2 = ggplot(dyad_trends, aes(x = year, y = agreement, color = label)) +
	geom_line(linewidth = 0.8) +
	geom_smooth(method = 'loess', span = 0.3, se = FALSE, linewidth = 1.2) +
	labs(title = 'Key Bilateral Alignment Trends',
	     subtitle = 'UNGA voting agreement score',
	     x = NULL, y = 'Agreement Score', color = NULL) +
	theme_csis() +
	scale_color_brewer(palette = 'Set2')

ggsave(file.path(res_figs, 'fig02_key_dyads.pdf'), p2, width = 12, height = 7)
ggsave(file.path(res_figs, 'fig02_key_dyads.png'), p2, width = 12, height = 7, dpi = 300)

# group cohesion over time
# compute mean pairwise unga agreement within group
compute_group_cohesion = function(group_iso3s, data) {
	data %>%
		filter(iso3_1 %in% group_iso3s, iso3_2 %in% group_iso3s) %>%
		group_by(year) %>%
		summarize(cohesion = mean(agree, na.rm = TRUE),
		          n_pairs = n(), .groups = 'drop')
}

g7_iso3 = groups$iso3[groups$g7]
brics_iso3 = groups$iso3[groups$brics_original]
nato_iso3 = groups$iso3[groups$nato]
asean_iso3 = groups$iso3[groups$asean]

cohesion_data = bind_rows(
	compute_group_cohesion(g7_iso3, unga_clean) %>% mutate(group = 'G7'),
	compute_group_cohesion(brics_iso3, unga_clean) %>% mutate(group = 'BRICS'),
	compute_group_cohesion(nato_iso3, unga_clean) %>% mutate(group = 'NATO'),
	compute_group_cohesion(asean_iso3, unga_clean) %>% mutate(group = 'ASEAN')
)

p3 = ggplot(cohesion_data, aes(x = year, y = cohesion, color = group)) +
	geom_line(linewidth = 0.6, alpha = 0.4) +
	geom_smooth(method = 'loess', span = 0.3, se = FALSE, linewidth = 1.2) +
	labs(title = 'Within-Group Diplomatic Cohesion',
	     subtitle = 'Mean pairwise UNGA voting agreement within each bloc',
	     x = NULL, y = 'Mean Agreement', color = NULL) +
	theme_csis() +
	scale_color_manual(values = c('G7' = '#2166AC', 'BRICS' = '#B2182B',
	                               'NATO' = '#4393C3', 'ASEAN' = '#1B7837'))

ggsave(file.path(res_figs, 'fig03_group_cohesion.pdf'), p3, width = 10, height = 6)
ggsave(file.path(res_figs, 'fig03_group_cohesion.png'), p3, width = 10, height = 6, dpi = 300)

# group alignment with us vs china
compute_group_anchor = function(group_iso3s, anchor_iso3, data) {
	data %>%
		filter(
			(iso3_1 %in% group_iso3s & iso3_2 == anchor_iso3) |
			(iso3_2 %in% group_iso3s & iso3_1 == anchor_iso3)
		) %>%
		group_by(year) %>%
		summarize(alignment = mean(agree, na.rm = TRUE), .groups = 'drop')
}

group_anchor_data = bind_rows(
	# g7 alignment with us and china
	compute_group_anchor(g7_iso3, 'USA', unga_clean) %>%
		mutate(group = 'G7', anchor = 'with US'),
	compute_group_anchor(g7_iso3, 'CHN', unga_clean) %>%
		mutate(group = 'G7', anchor = 'with China'),
	# brics alignment
	compute_group_anchor(brics_iso3, 'USA', unga_clean) %>%
		mutate(group = 'BRICS', anchor = 'with US'),
	compute_group_anchor(brics_iso3, 'CHN', unga_clean) %>%
		mutate(group = 'BRICS', anchor = 'with China'),
	# global south
	compute_group_anchor(groups$iso3[groups$global_south], 'USA', unga_clean) %>%
		mutate(group = 'Global South', anchor = 'with US'),
	compute_group_anchor(groups$iso3[groups$global_south], 'CHN', unga_clean) %>%
		mutate(group = 'Global South', anchor = 'with China')
)

p4 = ggplot(group_anchor_data, aes(x = year, y = alignment, color = anchor)) +
	geom_smooth(method = 'loess', span = 0.3, se = TRUE, linewidth = 1.2, alpha = 0.2) +
	facet_wrap(~group) +
	labs(title = 'Bloc Alignment: US vs China',
	     subtitle = 'Mean UNGA voting agreement with each anchor state',
	     x = NULL, y = 'Mean Agreement', color = NULL) +
	theme_csis() +
	scale_color_manual(values = c('with US' = '#2166AC', 'with China' = '#B2182B'))

ggsave(file.path(res_figs, 'fig04_group_anchor.pdf'), p4, width = 12, height = 8)
ggsave(file.path(res_figs, 'fig04_group_anchor.png'), p4, width = 12, height = 8, dpi = 300)

# who is drifting toward china
# compare 2010-2014 average vs 2020-2024 average alignment with china
drift_data = unga_clean %>%
	filter((iso3_1 == 'CHN' | iso3_2 == 'CHN')) %>%
	mutate(
		country = ifelse(iso3_1 == 'CHN', iso3_2, iso3_1),
		period = case_when(
			year %in% 2010:2014 ~ 'early',
			year %in% 2020:2024 ~ 'late',
			TRUE ~ NA_character_
		)
	) %>%
	filter(!is.na(period), country != 'USA') %>%
	group_by(country, period) %>%
	summarize(agree_china = mean(agree, na.rm = TRUE), .groups = 'drop') %>%
	pivot_wider(names_from = period, values_from = agree_china) %>%
	filter(!is.na(early), !is.na(late)) %>%
	mutate(drift_to_china = late - early) %>%
	left_join(groups %>% select(iso3, name_common, g7, brics_original, global_south),
	          by = c('country' = 'iso3')) %>%
	mutate(
		group_label = case_when(
			g7 ~ 'G7',
			brics_original ~ 'BRICS',
			global_south ~ 'Global South',
			TRUE ~ 'Other'
		)
	)

p5 = ggplot(drift_data %>% filter(abs(drift_to_china) > 0.01),
            aes(x = reorder(name_common, drift_to_china), y = drift_to_china,
                fill = group_label)) +
	geom_col() +
	coord_flip() +
	labs(title = 'Who Is Drifting Toward China?',
	     subtitle = 'Change in UNGA voting agreement with China: 2020-2024 vs 2010-2014',
	     x = NULL, y = 'Change in Agreement with China', fill = NULL) +
	theme_csis() +
	scale_fill_manual(values = c('G7' = '#2166AC', 'BRICS' = '#B2182B',
	                              'Global South' = '#1B7837', 'Other' = '#636363'))

ggsave(file.path(res_figs, 'fig05_drift_to_china.pdf'), p5, width = 10, height = 14)
ggsave(file.path(res_figs, 'fig05_drift_to_china.png'), p5, width = 10, height = 14, dpi = 300)

# output summary csvs
registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)

# dyad-year raw unga scores with country names
dyad_year_unga = unga_clean %>%
	left_join(registry %>% select(iso3, name_common), by = c('iso3_1' = 'iso3')) %>%
	rename(name_1 = name_common) %>%
	left_join(registry %>% select(iso3, name_common), by = c('iso3_2' = 'iso3')) %>%
	rename(name_2 = name_common)

write_csv(dyad_year_unga, file.path(res_scores, 'dyad_year_unga_agreement.csv'))

# country-year anchor scores
if (has_lame) {
	anchor_out = anchor %>%
		select(country, year, name_common, alignment_with_US, alignment_with_China,
		       US_minus_China, g7, brics_original, global_south)
	write_csv(anchor_out, file.path(res_scores, 'country_year_anchor.csv'))
}

# bloc summaries
bloc_summary = cohesion_data %>%
	left_join(
		group_anchor_data %>%
			pivot_wider(names_from = anchor, values_from = alignment,
			            names_prefix = 'alignment_'),
		by = c('year', 'group')
	)
write_csv(bloc_summary, file.path(res_scores, 'bloc_year_summaries.csv'))
