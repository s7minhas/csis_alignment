########################################################
# build network objects and dbn arrays
# input: processed unga, alliance, trade data
# output: data/networks/ -- netify objects and 4d arrays
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)
groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load processed data
load(file.path(data_proc, 'unga_agreement.rda'))   # unga_clean
load(file.path(data_proc, 'alliances.rda'))         # alliance_clean
load(file.path(data_proc, 'trade.rda'))             # trade_clean

# define common time range and actor set
YEARS = MIN_YEAR:MAX_YEAR

# for the multiplex model, we need a common actor set
# use all actors that appear in any layer (union, not intersection)
all_actors = sort(unique(c(
	unga_clean$iso3_1, unga_clean$iso3_2,
	alliance_clean$iso3_1, alliance_clean$iso3_2,
	trade_clean$iso3_1, trade_clean$iso3_2
)))

# filter to registry
all_actors = all_actors[all_actors %in% registry$iso3]
n_actors = length(all_actors)
validate_actor_coverage(all_actors, 'Network actors')

# build arrays for dbn
# dbn expects: Y[n_row, n_col, p, T]
# p = number of relation layers
# 3 layers:
#   1. unga agreement (symmetric)
#   2. alliance count (symmetric)
#   3. trade log (directed -- using log bilateral trade)

# use the overlapping time range where all 3 layers exist
# unga: 1965-2024, alliances: 1965-2024, trade: 1990-2020
# full model uses unga+alliances 1965-2024 (trade has NAs for missing years)

# initialize empty array with NAs
n_layers = 3
Y_array = array(NA_real_, dim = c(n_actors, n_actors, n_layers, length(YEARS)),
	dimnames = list(all_actors, all_actors,
		c('unga_agree', 'alliance', 'log_trade'),
		as.character(YEARS)))

# fill unga layer
for (i in seq_len(nrow(unga_clean))) {
	r = unga_clean[i, ]
	ri = match(r$iso3_1, all_actors)
	ci = match(r$iso3_2, all_actors)
	ti = match(as.character(r$year), as.character(YEARS))
	if (!is.na(ri) && !is.na(ci) && !is.na(ti)) {
		Y_array[ri, ci, 1, ti] = r$agree
		Y_array[ci, ri, 1, ti] = r$agree  # symmetric
	}
}

# fill alliance layer
for (i in seq_len(nrow(alliance_clean))) {
	r = alliance_clean[i, ]
	ri = match(r$iso3_1, all_actors)
	ci = match(r$iso3_2, all_actors)
	ti = match(as.character(r$year), as.character(YEARS))
	if (!is.na(ri) && !is.na(ci) && !is.na(ti)) {
		Y_array[ri, ci, 2, ti] = r$ally_total
		Y_array[ci, ri, 2, ti] = r$ally_total  # symmetric
	}
}

# fill trade layer (directed -- log trade)
for (i in seq_len(nrow(trade_clean))) {
	r = trade_clean[i, ]
	ri = match(r$iso3_1, all_actors)
	ci = match(r$iso3_2, all_actors)
	ti = match(as.character(r$year), as.character(YEARS))
	if (!is.na(ri) && !is.na(ci) && !is.na(ti)) {
		Y_array[ri, ci, 3, ti] = r$log_trade  # directed: i exports to j
	}
}

# set diagonal to NA
for (t in seq_along(YEARS)) {
	for (p in 1:n_layers) {
		diag(Y_array[, , p, t]) = NA
	}
}

# standardize within year
Y_std = Y_array
for (t in seq_along(YEARS)) {
	for (p in 1:n_layers) {
		vals = Y_array[, , p, t]
		vals_vec = vals[!is.na(vals)]
		if (length(vals_vec) > 10) {
			m = mean(vals_vec)
			s = sd(vals_vec)
			if (s > 0) Y_std[, , p, t] = (Y_array[, , p, t] - m) / s
		}
	}
}

# coverage diagnostics
for (p in 1:n_layers) {
	layer_name = dimnames(Y_array)[[3]][p]
	for (decade_start in seq(1970, 2020, 10)) {
		decade_years = which(YEARS %in% decade_start:(decade_start + 9))
		if (length(decade_years) > 0) {
			slice = Y_std[, , p, decade_years, drop = FALSE]
			pct_obs = round(100 * mean(!is.na(slice)), 1)
		}
	}
}

# build unga-only array for standalone model
Y_unga_only = Y_std[, , 1, , drop = FALSE]

# build unga+alliance array (symmetric layers only)
Y_structural = Y_std[, , 1:2, , drop = FALSE]

# save
save(Y_array, Y_std, all_actors, YEARS,
	file = file.path(data_nets, 'dbn_arrays.rda'))
save(Y_unga_only, file = file.path(data_nets, 'dbn_unga_only.rda'))
save(Y_structural, file = file.path(data_nets, 'dbn_structural.rda'))

# save actor list
write_csv(tibble(iso3 = all_actors, idx = seq_along(all_actors)),
	file.path(data_nets, 'actor_index.csv'))

# build lame-format lists (list of matrices per year)
# for unga layer
unga_lame = lapply(seq_along(YEARS), function(t) {
	Y_std[, , 1, t]
})
names(unga_lame) = as.character(YEARS)

# for trade layer (directed)
trade_lame = lapply(seq_along(YEARS), function(t) {
	Y_std[, , 3, t]
})
names(trade_lame) = as.character(YEARS)

save(unga_lame, file = file.path(data_nets, 'lame_unga.rda'))
save(trade_lame, file = file.path(data_nets, 'lame_trade.rda'))
