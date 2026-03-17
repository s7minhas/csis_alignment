########################################################
# extract trade-based alignment scores from lame trade model
# adds operational_coupling to the dashboard data
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)
groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load trade model
load(file.path(res_models, 'lame_trade.rda'))

# trade model is directed: U = sender positions, V = receiver positions
U = lame_trade$U
V = lame_trade$V
n_actors = dim(U)[1]
n_dims = dim(U)[2]
n_times = dim(U)[3]
actor_names = rownames(U)
years = 1990:2023

# compute pairwise distances
# for directed networks: use average of sender-receiver positions
trade_scores = list()

for (t in 1:n_times) {
	yr = years[t]
	U_t = U[, , t]
	V_t = if (!is.null(V)) V[, , t] else U_t

	# compute distances in both sender and receiver spaces
	dist_U = as.matrix(dist(U_t))
	dist_V = as.matrix(dist(V_t))
	dist_avg = (dist_U + dist_V) / 2

	rownames(dist_avg) = actor_names
	colnames(dist_avg) = actor_names

	# min-max normalize within year
	all_dists = dist_avg[upper.tri(dist_avg)]
	d_min = min(all_dists)
	d_max = max(all_dists)
	d_range = d_max - d_min + 1e-10

	for (i in 1:(n_actors - 1)) {
		for (j in (i + 1):n_actors) {
			trade_scores[[length(trade_scores) + 1]] = data.frame(
				iso3_1 = actor_names[i],
				iso3_2 = actor_names[j],
				year = yr,
				trade_coupling = 1 - (dist_avg[i, j] - d_min) / d_range,
				stringsAsFactors = FALSE
			)
		}
	}
}

trade_df = do.call(rbind, trade_scores) %>% as_tibble()

# compute trade anchor scores

trade_us = trade_df %>%
	filter(iso3_1 == 'USA' | iso3_2 == 'USA') %>%
	mutate(country = ifelse(iso3_1 == 'USA', iso3_2, iso3_1)) %>%
	select(country, year, trade_coupling_US = trade_coupling)

trade_cn = trade_df %>%
	filter(iso3_1 == 'CHN' | iso3_2 == 'CHN') %>%
	mutate(country = ifelse(iso3_1 == 'CHN', iso3_2, iso3_1)) %>%
	select(country, year, trade_coupling_China = trade_coupling)

trade_anchor = trade_us %>%
	full_join(trade_cn, by = c('country', 'year')) %>%
	mutate(trade_US_minus_China = trade_coupling_US - trade_coupling_China) %>%
	filter(!country %in% c('USA', 'CHN'))

# merge with existing diplomatic scores
anchor_diplo = read_csv(file.path(res_scores, 'country_year_anchor.csv'), show_col_types = FALSE)

# join trade scores (years 1990-2023 only)
anchor_combined = anchor_diplo %>%
	left_join(trade_anchor, by = c('country', 'year'))

# compute structural vs operational gap
anchor_combined = anchor_combined %>%
	mutate(
		structural_vs_trade_gap = alignment_with_US - trade_coupling_US
	)

# export trade latent positions for circplot
# sender (U) and receiver (V) exported separately
# following lame uv_plot convention: U = outer ring, V = inner ring
trade_latent_list = list()
for (t in 1:n_times) {
	yr = years[t]
	U_t = U[, , t]
	V_t = if (!is.null(V)) V[, , t] else U_t

	for (i in 1:n_actors) {
		trade_latent_list[[length(trade_latent_list) + 1]] = data.frame(
			iso3 = actor_names[i],
			year = yr,
			u_dim1 = U_t[i, 1], u_dim2 = U_t[i, 2],
			v_dim1 = V_t[i, 1], v_dim2 = V_t[i, 2],
			stringsAsFactors = FALSE
		)
	}
}

trade_latent_positions = do.call(rbind, trade_latent_list) %>%
	as_tibble() %>%
	left_join(registry %>% select(iso3, name_common), by = 'iso3') %>%
	left_join(groups %>% select(iso3, g7, brics_original, global_south), by = 'iso3')

# save
write_csv(anchor_combined, file.path(res_scores, 'country_year_anchor.csv'))
write_csv(trade_df, file.path(res_scores, 'dyad_year_trade_scores.csv'))
write_csv(trade_latent_positions, file.path(res_scores, 'trade_latent_positions.csv'))
