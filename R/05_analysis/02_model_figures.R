########################################################
# model-based figures for csis report
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)
anchor_df = read_csv(file.path(res_scores, 'country_year_anchor.csv'), show_col_types = FALSE)
latent_pos = read_csv(file.path(res_scores, 'latent_positions.csv'), show_col_types = FALSE)
bloc_df = read_csv(file.path(res_scores, 'bloc_year_summaries_model.csv'), show_col_types = FALSE)
dyad_df = read_csv(file.path(res_scores, 'dyad_year_scores.csv'), show_col_types = FALSE)

# latent space snapshots (2000, 2012, 2024)
snapshot_years = c(2000, 2012, 2024)

latent_snap = latent_pos %>%
	filter(year %in% snapshot_years) %>%
	mutate(
		group_label = case_when(
			g7 ~ 'G7',
			brics_original ~ 'BRICS',
			global_south ~ 'Global South',
			TRUE ~ 'Other'
		),
		label = ifelse(iso3 %in% c('USA', 'CHN', 'RUS', 'IND', 'BRA', 'GBR',
		                            'JPN', 'KOR', 'SAU', 'IRN', 'TUR', 'ISR',
		                            'UKR', 'CUB', 'PRK', 'AUS', 'DEU', 'ZAF'),
		               iso3, NA)
	)

p6 = ggplot(latent_snap, aes(x = dim1, y = dim2, color = group_label)) +
	geom_point(size = 2.5, alpha = 0.8) +
	geom_text(aes(label = label), size = 2.5, vjust = -0.8, show.legend = FALSE) +
	facet_wrap(~year) +
	labs(title = 'Diplomatic Alignment Space',
	     subtitle = 'Latent positions from UNGA voting network model (lame, R=2)',
	     x = 'Dimension 1', y = 'Dimension 2', color = NULL) +
	theme_csis() +
	scale_color_manual(values = c('G7' = '#2166AC', 'BRICS' = '#B2182B',
	                               'Global South' = '#1B7837', 'Other' = '#969696'))

ggsave(file.path(res_figs, 'fig06_latent_space.pdf'), p6, width = 14, height = 5)
ggsave(file.path(res_figs, 'fig06_latent_space.png'), p6, width = 14, height = 5, dpi = 300)

# us-minus-china tilt over time for key countries
key_countries = c('KOR', 'IND', 'TUR', 'SAU', 'BRA', 'IDN', 'PAK', 'ZAF', 'NGA', 'EGY')

p7_data = anchor_df %>% filter(country %in% key_countries)

p7 = ggplot(p7_data, aes(x = year, y = US_minus_China, color = country)) +
	geom_line(linewidth = 0.6, alpha = 0.5) +
	geom_smooth(method = 'loess', span = 0.4, se = FALSE, linewidth = 1.2) +
	geom_hline(yintercept = 0, linetype = 'dashed', color = '#636363') +
	labs(title = 'US vs China Tilt: Key Swing States',
	     subtitle = 'Positive = closer to US, Negative = closer to China (LAME structural alignment)',
	     x = NULL, y = 'US minus China Alignment', color = NULL) +
	theme_csis() +
	annotate('text', x = 1991, y = 0.05, label = 'Closer to US', color = '#2166AC', size = 3) +
	annotate('text', x = 1991, y = -0.05, label = 'Closer to China', color = '#B2182B', size = 3)

ggsave(file.path(res_figs, 'fig07_tilt_swing_states.pdf'), p7, width = 12, height = 7)
ggsave(file.path(res_figs, 'fig07_tilt_swing_states.png'), p7, width = 12, height = 7, dpi = 300)

# bloc cohesion from model
p8 = ggplot(bloc_df %>% filter(bloc %in% c('G7', 'BRICS', 'NATO', 'ASEAN')),
            aes(x = year, y = within_cohesion, color = bloc)) +
	geom_line(linewidth = 0.6, alpha = 0.4) +
	geom_smooth(method = 'loess', span = 0.4, se = FALSE, linewidth = 1.2) +
	labs(title = 'Bloc Cohesion (Model-Based)',
	     subtitle = 'Mean pairwise structural alignment within each bloc (LAME latent space)',
	     x = NULL, y = 'Within-Bloc Alignment', color = NULL) +
	theme_csis() +
	scale_color_manual(values = c('G7' = '#2166AC', 'BRICS' = '#B2182B',
	                               'NATO' = '#4393C3', 'ASEAN' = '#1B7837'))

ggsave(file.path(res_figs, 'fig08_bloc_cohesion_model.pdf'), p8, width = 10, height = 6)
ggsave(file.path(res_figs, 'fig08_bloc_cohesion_model.png'), p8, width = 10, height = 6, dpi = 300)

# bloc tilt (us minus china)
p9 = ggplot(bloc_df, aes(x = year, y = US_minus_China, color = bloc)) +
	geom_line(linewidth = 0.6, alpha = 0.4) +
	geom_smooth(method = 'loess', span = 0.4, se = FALSE, linewidth = 1.2) +
	geom_hline(yintercept = 0, linetype = 'dashed', color = '#636363') +
	labs(title = 'Bloc-Level US vs China Tilt',
	     subtitle = 'Mean (alignment with US) - (alignment with China) within each bloc',
	     x = NULL, y = 'US minus China (Mean within Bloc)', color = NULL) +
	theme_csis() +
	scale_color_manual(values = c('G7' = '#2166AC', 'BRICS' = '#B2182B',
	                               'NATO' = '#4393C3', 'ASEAN' = '#1B7837',
	                               'Global South' = '#1B7837'))

ggsave(file.path(res_figs, 'fig09_bloc_tilt.pdf'), p9, width = 10, height = 6)
ggsave(file.path(res_figs, 'fig09_bloc_tilt.png'), p9, width = 10, height = 6, dpi = 300)

# us-south korea alignment trajectory
us_kor = dyad_df %>%
	filter((iso3_1 == 'USA' & iso3_2 == 'KOR') | (iso3_1 == 'KOR' & iso3_2 == 'USA'))

us_chn = dyad_df %>%
	filter((iso3_1 == 'USA' & iso3_2 == 'CHN') | (iso3_1 == 'CHN' & iso3_2 == 'USA'))

us_rus = dyad_df %>%
	filter((iso3_1 == 'USA' & iso3_2 == 'RUS') | (iso3_1 == 'RUS' & iso3_2 == 'USA'))

chn_rus = dyad_df %>%
	filter((iso3_1 == 'CHN' & iso3_2 == 'RUS') | (iso3_1 == 'RUS' & iso3_2 == 'CHN'))

focal_dyads = bind_rows(
	us_kor %>% mutate(dyad = 'US-South Korea'),
	us_chn %>% mutate(dyad = 'US-China'),
	us_rus %>% mutate(dyad = 'US-Russia'),
	chn_rus %>% mutate(dyad = 'China-Russia')
)

p10 = ggplot(focal_dyads, aes(x = year, y = structural_alignment, color = dyad)) +
	geom_line(linewidth = 1.2) +
	geom_point(size = 1.5) +
	labs(title = 'Key Dyad Structural Alignment (Model-Based)',
	     subtitle = 'From latent positions in UNGA voting network (LAME, R=2, dynamic)',
	     x = NULL, y = 'Structural Alignment', color = NULL) +
	theme_csis() +
	scale_color_manual(values = c('US-South Korea' = '#2166AC',
	                               'US-China' = '#B2182B',
	                               'US-Russia' = '#7B3294',
	                               'China-Russia' = '#E08214'))

ggsave(file.path(res_figs, 'fig10_key_dyad_alignment.pdf'), p10, width = 10, height = 6)
ggsave(file.path(res_figs, 'fig10_key_dyad_alignment.png'), p10, width = 10, height = 6, dpi = 300)
