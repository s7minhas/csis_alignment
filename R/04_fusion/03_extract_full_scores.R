########################################################
# extract scores from full 193-country lame model
# replaces pilot scores with complete global coverage
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)
groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load full model
load(file.path(res_models, 'lame_unga.rda'))

U = lame_unga$U
n_actors = dim(U)[1]
n_dims = dim(U)[2]
n_times = dim(U)[3]
actor_names = rownames(U)
years = 1990:2024

validate_actor_coverage(actor_names, 'Full LAME')

# compute pairwise euclidean distances per year
dyad_scores = list()

for (t in 1:n_times) {
	yr = years[t]
	U_t = U[, , t]

	# euclidean distance
	dist_mat = as.matrix(dist(U_t))
	rownames(dist_mat) = actor_names
	colnames(dist_mat) = actor_names

	# min-max normalization within year: 0 = max distance, 1 = min distance
	all_dists = dist_mat[upper.tri(dist_mat)]
	d_min = min(all_dists)
	d_max = max(all_dists)
	d_range = d_max - d_min + 1e-10

	# extract upper triangle (i < j, no duplicates)
	for (i in 1:(n_actors - 1)) {
		for (j in (i + 1):n_actors) {
			dyad_scores[[length(dyad_scores) + 1]] = data.frame(
				iso3_1 = actor_names[i],
				iso3_2 = actor_names[j],
				year = yr,
				latent_distance = dist_mat[i, j],
				structural_alignment = 1 - (dist_mat[i, j] - d_min) / d_range,
				stringsAsFactors = FALSE
			)
		}
	}
}

dyad_df = do.call(rbind, dyad_scores)
dyad_df = as_tibble(dyad_df)

# add country names
dyad_df = dyad_df %>%
	left_join(registry %>% select(iso3, name_common), by = c('iso3_1' = 'iso3')) %>%
	rename(name_1 = name_common) %>%
	left_join(registry %>% select(iso3, name_common), by = c('iso3_2' = 'iso3')) %>%
	rename(name_2 = name_common)

# compute anchor-relative scores

# us alignment
us_scores = dyad_df %>%
	filter(iso3_1 == ANCHOR_US | iso3_2 == ANCHOR_US) %>%
	mutate(country = ifelse(iso3_1 == ANCHOR_US, iso3_2, iso3_1)) %>%
	select(country, year, alignment_with_US = structural_alignment)

# china alignment
cn_scores = dyad_df %>%
	filter(iso3_1 == ANCHOR_CN | iso3_2 == ANCHOR_CN) %>%
	mutate(country = ifelse(iso3_1 == ANCHOR_CN, iso3_2, iso3_1)) %>%
	select(country, year, alignment_with_China = structural_alignment)

# g7 alignment: for every country, mean alignment with g7 members
g7_iso3 = intersect(c('USA', 'GBR', 'FRA', 'DEU', 'ITA', 'JPN', 'CAN'), actor_names)
g7_scores = dyad_df %>%
	filter(iso3_1 %in% g7_iso3 | iso3_2 %in% g7_iso3) %>%
	{
		both_g7 = filter(., iso3_1 %in% g7_iso3 & iso3_2 %in% g7_iso3)
		one_g7 = filter(., xor(iso3_1 %in% g7_iso3, iso3_2 %in% g7_iso3))

		bind_rows(
			one_g7 %>% mutate(country = ifelse(iso3_1 %in% g7_iso3, iso3_2, iso3_1)),
			both_g7 %>% mutate(country = iso3_1),
			both_g7 %>% mutate(country = iso3_2)
		)
	} %>%
	group_by(country, year) %>%
	summarize(alignment_with_G7 = mean(structural_alignment, na.rm = TRUE), .groups = 'drop')

# brics alignment: same logic
brics_iso3 = intersect(c('BRA', 'RUS', 'IND', 'CHN', 'ZAF'), actor_names)
brics_scores = dyad_df %>%
	filter(iso3_1 %in% brics_iso3 | iso3_2 %in% brics_iso3) %>%
	{
		both_brics = filter(., iso3_1 %in% brics_iso3 & iso3_2 %in% brics_iso3)
		one_brics = filter(., xor(iso3_1 %in% brics_iso3, iso3_2 %in% brics_iso3))

		bind_rows(
			one_brics %>% mutate(country = ifelse(iso3_1 %in% brics_iso3, iso3_2, iso3_1)),
			both_brics %>% mutate(country = iso3_1),
			both_brics %>% mutate(country = iso3_2)
		)
	} %>%
	group_by(country, year) %>%
	summarize(alignment_with_BRICS = mean(structural_alignment, na.rm = TRUE), .groups = 'drop')

# merge
anchor_df = us_scores %>%
	full_join(cn_scores, by = c('country', 'year')) %>%
	left_join(g7_scores, by = c('country', 'year')) %>%
	left_join(brics_scores, by = c('country', 'year')) %>%
	mutate(
		US_minus_China = alignment_with_US - alignment_with_China,
		G7_minus_BRICS = alignment_with_G7 - alignment_with_BRICS
	) %>%
	filter(!country %in% c('USA', 'CHN')) %>%
	left_join(registry %>% select(iso3, name_common), by = c('country' = 'iso3')) %>%
	left_join(groups %>% select(iso3, g7, brics_original, brics_plus, nato, asean,
		global_south, oecd),
		by = c('country' = 'iso3'))

# bloc summaries

compute_bloc_stats = function(bloc_name, bloc_iso3s) {
	within = dyad_df %>%
		filter(iso3_1 %in% bloc_iso3s, iso3_2 %in% bloc_iso3s) %>%
		group_by(year) %>%
		summarize(
			within_cohesion = mean(structural_alignment, na.rm = TRUE),
			within_cohesion_sd = sd(structural_alignment, na.rm = TRUE),
			.groups = 'drop'
		) %>%
		mutate(bloc = bloc_name)

	group_anchor = anchor_df %>%
		filter(country %in% bloc_iso3s) %>%
		group_by(year) %>%
		summarize(alignment_with_US = mean(alignment_with_US, na.rm = TRUE),
			alignment_with_China = mean(alignment_with_China, na.rm = TRUE),
			US_minus_China = mean(US_minus_China, na.rm = TRUE),
			.groups = 'drop') %>%
		mutate(bloc = bloc_name)

	left_join(within, group_anchor, by = c('year', 'bloc'))
}

bloc_df = bind_rows(
	compute_bloc_stats('G7', intersect(G7, actor_names)),
	compute_bloc_stats('BRICS', intersect(BRICS_ORIG, actor_names)),
	compute_bloc_stats('NATO', intersect(groups$iso3[groups$nato], actor_names)),
	compute_bloc_stats('ASEAN', intersect(groups$iso3[groups$asean], actor_names)),
	compute_bloc_stats('Global South', intersect(groups$iso3[groups$global_south], actor_names))
)

# latent positions
latent_list = list()
for (t in 1:n_times) {
	for (i in 1:n_actors) {
		latent_list[[length(latent_list) + 1]] = data.frame(
			iso3 = actor_names[i],
			year = years[t],
			dim1 = U[i, 1, t],
			dim2 = U[i, 2, t],
			stringsAsFactors = FALSE
		)
	}
}
latent_positions = do.call(rbind, latent_list) %>%
	as_tibble() %>%
	left_join(registry %>% select(iso3, name_common), by = 'iso3') %>%
	left_join(groups %>% select(iso3, g7, brics_original, global_south), by = 'iso3')

# save all outputs
write_csv(dyad_df %>% select(iso3_1, iso3_2, name_1, name_2, year,
	structural_alignment, latent_distance),
	file.path(res_scores, 'dyad_year_scores.csv'))

write_csv(anchor_df, file.path(res_scores, 'country_year_anchor.csv'))
write_csv(bloc_df, file.path(res_scores, 'bloc_year_summaries_model.csv'))
write_csv(latent_positions, file.path(res_scores, 'latent_positions.csv'))
