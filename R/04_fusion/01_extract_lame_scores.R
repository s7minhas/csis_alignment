########################################################
# extract scores from lame pilot model
# produces: dyad-year alignment scores, anchor-relative scores
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)
groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load model
load(file.path(res_models, 'lame_pilot.rda'))

# extract latent positions
U = lame_pilot$U  # n x R x T (dynamic)
n_actors = dim(U)[1]
n_dims = dim(U)[2]
n_times = dim(U)[3]
actor_names = lame_pilot_actors

# compute pairwise euclidean distances per year
dyad_scores = list()

for (t in 1:n_times) {
	yr = lame_pilot_years[t]
	U_t = U[, , t]

	# euclidean distance in latent space
	dist_mat = as.matrix(dist(U_t))
	rownames(dist_mat) = actor_names
	colnames(dist_mat) = actor_names

	# correlation-based similarity (row profiles)
	cor_mat = cor(t(U_t))
	rownames(cor_mat) = actor_names
	colnames(cor_mat) = actor_names

	for (i in 1:(n_actors - 1)) {
		for (j in (i + 1):n_actors) {
			dyad_scores[[length(dyad_scores) + 1]] = tibble(
				iso3_1 = actor_names[i],
				iso3_2 = actor_names[j],
				year = yr,
				latent_distance = dist_mat[i, j],
				latent_correlation = cor_mat[i, j]
			)
		}
	}
}

dyad_df = bind_rows(dyad_scores)

# normalize: convert distance to alignment (higher = more aligned)
dyad_df = dyad_df %>%
	group_by(year) %>%
	mutate(
		# invert and normalize distance to [0,1]
		structural_alignment = 1 - (latent_distance - min(latent_distance)) /
			(max(latent_distance) - min(latent_distance) + 1e-10),
		# correlation is already [-1,1], rescale to [0,1]
		structural_alignment_cor = (latent_correlation + 1) / 2
	) %>%
	ungroup()

# add country names
dyad_df = dyad_df %>%
	left_join(registry %>% select(iso3, name_common), by = c('iso3_1' = 'iso3')) %>%
	rename(name_1 = name_common) %>%
	left_join(registry %>% select(iso3, name_common), by = c('iso3_2' = 'iso3')) %>%
	rename(name_2 = name_common)

# compute anchor-relative scores

# us alignment: distance from each country to usa
us_scores = dyad_df %>%
	filter(iso3_1 == 'USA' | iso3_2 == 'USA') %>%
	mutate(country = ifelse(iso3_1 == 'USA', iso3_2, iso3_1)) %>%
	select(country, year, alignment_with_US = structural_alignment)

# china alignment
cn_scores = dyad_df %>%
	filter(iso3_1 == 'CHN' | iso3_2 == 'CHN') %>%
	mutate(country = ifelse(iso3_1 == 'CHN', iso3_2, iso3_1)) %>%
	select(country, year, alignment_with_China = structural_alignment)

# g7 alignment: mean pairwise alignment with g7 members
g7_iso3 = intersect(c('USA', 'GBR', 'FRA', 'DEU', 'ITA', 'JPN', 'CAN'), actor_names)
g7_scores = dyad_df %>%
	filter((iso3_1 %in% g7_iso3 & !iso3_2 %in% g7_iso3) |
		(iso3_2 %in% g7_iso3 & !iso3_1 %in% g7_iso3)) %>%
	mutate(country = ifelse(iso3_1 %in% g7_iso3, iso3_2, iso3_1)) %>%
	group_by(country, year) %>%
	summarize(alignment_with_G7 = mean(structural_alignment, na.rm = TRUE), .groups = 'drop')

# brics alignment: mean pairwise alignment with brics members
brics_iso3 = intersect(c('BRA', 'RUS', 'IND', 'CHN', 'ZAF'), actor_names)
brics_scores = dyad_df %>%
	filter((iso3_1 %in% brics_iso3 & !iso3_2 %in% brics_iso3) |
		(iso3_2 %in% brics_iso3 & !iso3_1 %in% brics_iso3)) %>%
	mutate(country = ifelse(iso3_1 %in% brics_iso3, iso3_2, iso3_1)) %>%
	group_by(country, year) %>%
	summarize(alignment_with_BRICS = mean(structural_alignment, na.rm = TRUE), .groups = 'drop')

# merge anchor scores
anchor_df = us_scores %>%
	full_join(cn_scores, by = c('country', 'year')) %>%
	left_join(g7_scores, by = c('country', 'year')) %>%
	left_join(brics_scores, by = c('country', 'year')) %>%
	mutate(US_minus_China = alignment_with_US - alignment_with_China) %>%
	rename(distance_to_G7 = alignment_with_G7, distance_to_BRICS = alignment_with_BRICS) %>%
	filter(!country %in% c('USA', 'CHN')) %>%
	left_join(registry %>% select(iso3, name_common), by = c('country' = 'iso3')) %>%
	left_join(groups %>% select(iso3, g7, brics_original, brics_plus, nato, asean,
		global_south, oecd),
		by = c('country' = 'iso3'))

# compute bloc summaries

compute_bloc_stats = function(bloc_name, bloc_iso3s) {
	# within-group cohesion
	within = dyad_df %>%
		filter(iso3_1 %in% bloc_iso3s, iso3_2 %in% bloc_iso3s) %>%
		group_by(year) %>%
		summarize(
			within_cohesion = mean(structural_alignment, na.rm = TRUE),
			within_cohesion_sd = sd(structural_alignment, na.rm = TRUE),
			.groups = 'drop'
		) %>%
		mutate(bloc = bloc_name)

	# group anchor alignment
	group_us = anchor_df %>%
		filter(country %in% bloc_iso3s) %>%
		group_by(year) %>%
		summarize(alignment_with_US = mean(alignment_with_US, na.rm = TRUE),
			alignment_with_China = mean(alignment_with_China, na.rm = TRUE),
			US_minus_China = mean(US_minus_China, na.rm = TRUE),
			.groups = 'drop') %>%
		mutate(bloc = bloc_name)

	left_join(within, group_us, by = c('year', 'bloc'))
}

bloc_df = bind_rows(
	compute_bloc_stats('G7', intersect(G7, actor_names)),
	compute_bloc_stats('BRICS', intersect(BRICS_ORIG, actor_names)),
	compute_bloc_stats('NATO', intersect(groups$iso3[groups$nato], actor_names)),
	compute_bloc_stats('ASEAN', intersect(groups$iso3[groups$asean], actor_names)),
	compute_bloc_stats('Global South', intersect(groups$iso3[groups$global_south], actor_names))
)

# save outputs
write_csv(dyad_df %>% select(iso3_1, iso3_2, name_1, name_2, year,
	structural_alignment, latent_distance, latent_correlation),
	file.path(res_scores, 'dyad_year_scores.csv'))

write_csv(anchor_df, file.path(res_scores, 'country_year_anchor.csv'))
write_csv(bloc_df, file.path(res_scores, 'bloc_year_summaries_model.csv'))

# save latent positions for visualization
latent_pos = list()
for (t in 1:n_times) {
	for (i in 1:n_actors) {
		latent_pos[[length(latent_pos) + 1]] = tibble(
			iso3 = actor_names[i],
			year = lame_pilot_years[t],
			dim1 = U[i, 1, t],
			dim2 = U[i, 2, t]
		)
	}
}
latent_positions = bind_rows(latent_pos) %>%
	left_join(registry %>% select(iso3, name_common), by = 'iso3') %>%
	left_join(groups %>% select(iso3, g7, brics_original, global_south), by = 'iso3')

write_csv(latent_positions, file.path(res_scores, 'latent_positions.csv'))
