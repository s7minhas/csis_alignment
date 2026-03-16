########################################################
# extract scores from dbn and lame models
# produces: dyad-year alignment scores with decomposition
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)
groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load models
dbn_exists = file.exists(file.path(res_models, 'dbn_pilot.rda'))
lame_exists = file.exists(file.path(res_models, 'lame_unga.rda'))

if (dbn_exists) {
	load(file.path(res_models, 'dbn_pilot.rda'))
}
if (lame_exists) {
	load(file.path(res_models, 'lame_unga.rda'))
}

load(file.path(data_nets, 'dbn_arrays.rda'))  # Y_std, all_actors, YEARS

# extract dbn scores
if (dbn_exists) {

	# get posterior mean theta
	theta_mean = theta_summary(dbn_pilot, fun = mean)

	# extract per-layer, per-year theta matrices
	n_pilot = length(pilot_actors)
	n_years = length(YEARS)
	n_layers = dbn_pilot$dims$p

	# build dyad-year dataframe from theta
	dbn_scores_list = list()

	for (t_idx in seq_along(YEARS)) {
		yr = YEARS[t_idx]

		for (i in 1:(n_pilot - 1)) {
			for (j in (i + 1):n_pilot) {
				# get theta values across layers for this dyad-year
				# theta_mean is organized differently per model
				# use theta_slice for specific dyad
				row = tibble(
					iso3_1 = pilot_actors[i],
					iso3_2 = pilot_actors[j],
					year = yr
				)
				dbn_scores_list[[length(dbn_scores_list) + 1]] = row
			}
		}
	}

	dbn_dyads = bind_rows(dbn_scores_list)

	# for structural alignment: compute row-profile similarity from theta
	# for each year, get posterior mean theta matrix and compute correlations

	structural_scores = list()
	for (t_idx in seq_along(YEARS)) {
		yr = YEARS[t_idx]

		# get posterior mean theta for unga layer at this time
		# theta_slice returns draws x 1 for a specific i,j,rel,time
		theta_mat = matrix(NA, n_pilot, n_pilot)
		for (i in 1:n_pilot) {
			for (j in 1:n_pilot) {
				if (i != j) {
					draws = tryCatch(
						theta_slice(dbn_pilot, i = i, j = j, rel = 1, time = t_idx),
						error = function(e) NA
					)
					if (!any(is.na(draws))) theta_mat[i, j] = mean(draws)
				}
			}
		}

		# compute row-profile correlations (structural alignment)
		row_cors = cor(t(theta_mat), use = 'pairwise.complete.obs')

		for (i in 1:(n_pilot - 1)) {
			for (j in (i + 1):n_pilot) {
				structural_scores[[length(structural_scores) + 1]] = tibble(
					iso3_1 = pilot_actors[i],
					iso3_2 = pilot_actors[j],
					year = yr,
					structural_alignment = row_cors[i, j]
				)
			}
		}
	}

	dbn_structural = bind_rows(structural_scores)

	save(dbn_structural, file = file.path(data_proc, 'dbn_structural_scores.rda'))
}

# extract lame scores
if (lame_exists) {

	# u contains latent positions: n x R x T (or n x R if static)
	U = lame_unga$U

	# get year labels
	lame_years = as.integer(names(lame_unga$Y %||% names(lame_unga$YPM)))
	if (is.null(lame_years) || length(lame_years) == 0) {
		# try to infer from model
		lame_years = 1990:2024
	}

	# compute pairwise euclidean distances in latent space per year
	lame_scores_list = list()
	n_lame = dim(U)[1]
	actor_names = rownames(U) %||% all_actors[1:n_lame]

	if (length(dim(U)) == 3) {
		# dynamic: n x R x T
		n_times = dim(U)[3]
		for (t in 1:min(n_times, length(lame_years))) {
			U_t = U[, , t]
			dists = as.matrix(dist(U_t))
			yr = lame_years[t]

			for (i in 1:(n_lame - 1)) {
				for (j in (i + 1):n_lame) {
					lame_scores_list[[length(lame_scores_list) + 1]] = tibble(
						iso3_1 = actor_names[i],
						iso3_2 = actor_names[j],
						year = yr,
						lame_distance = dists[i, j]
					)
				}
			}
		}
	} else {
		# static: n x R
		dists = as.matrix(dist(U))
		for (i in 1:(n_lame - 1)) {
			for (j in (i + 1):n_lame) {
				lame_scores_list[[length(lame_scores_list) + 1]] = tibble(
					iso3_1 = actor_names[i],
					iso3_2 = actor_names[j],
					lame_distance = dists[i, j]
				)
			}
		}
	}

	lame_distances = bind_rows(lame_scores_list)
	# invert distance: higher = more aligned
	lame_distances = lame_distances %>%
		group_by(year) %>%
		mutate(
			lame_alignment = 1 - (lame_distance - min(lame_distance, na.rm = TRUE)) /
				(max(lame_distance, na.rm = TRUE) - min(lame_distance, na.rm = TRUE) + 1e-10)
		) %>%
		ungroup()

	save(lame_distances, file = file.path(data_proc, 'lame_unga_scores.rda'))
}

# compute anchor-relative scores
compute_anchor_scores = function(scores_df, score_col, actors_col1 = 'iso3_1',
	actors_col2 = 'iso3_2') {
	# for each country-year, compute alignment with us and china
	us_scores = scores_df %>%
		filter(!!sym(actors_col1) == ANCHOR_US | !!sym(actors_col2) == ANCHOR_US) %>%
		mutate(
			country = ifelse(!!sym(actors_col1) == ANCHOR_US,
				!!sym(actors_col2), !!sym(actors_col1))
		) %>%
		select(country, year, alignment_with_US = !!sym(score_col))

	cn_scores = scores_df %>%
		filter(!!sym(actors_col1) == ANCHOR_CN | !!sym(actors_col2) == ANCHOR_CN) %>%
		mutate(
			country = ifelse(!!sym(actors_col1) == ANCHOR_CN,
				!!sym(actors_col2), !!sym(actors_col1))
		) %>%
		select(country, year, alignment_with_China = !!sym(score_col))

	anchor_df = full_join(us_scores, cn_scores, by = c('country', 'year')) %>%
		mutate(US_minus_China = alignment_with_US - alignment_with_China) %>%
		filter(country != ANCHOR_US, country != ANCHOR_CN)

	return(anchor_df)
}

if (lame_exists) {
	anchor_lame = compute_anchor_scores(lame_distances, 'lame_alignment')
	save(anchor_lame, file = file.path(data_proc, 'anchor_scores_lame.rda'))
}
