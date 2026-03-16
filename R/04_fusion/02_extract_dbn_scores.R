########################################################
# extract scores from dbn core model
# computes: theta-based structural alignment + A_t dynamics
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

registry = read_csv(file.path(data_reg, 'actors_master.csv'), show_col_types = FALSE)
groups = read_csv(file.path(data_reg, 'group_membership.csv'), show_col_types = FALSE)

# load dbn model
load(file.path(res_models, 'dbn_core.rda'))

n_actors = length(dbn_core_actors)
n_years = length(dbn_core_years)
n_draws = length(dbn_core$A)

# compute posterior mean theta per year
# theta dims: [n, n, p, T_stored, n_draws]
T_stored = dim(dbn_core$Theta)[4]

# average across draws
theta_mean = apply(dbn_core$Theta[, , 1, , ], c(1, 2, 3), mean)

# compute structural alignment from theta
dbn_dyad_scores = list()
for (t in 1:T_stored) {
	theta_t = theta_mean[, , t]
	rownames(theta_t) = dbn_core_actors
	colnames(theta_t) = dbn_core_actors

	# row-profile correlation: how similarly do i and j relate to all others?
	cor_mat = cor(t(theta_t), use = 'pairwise.complete.obs')

	# map time index back to year
	yr = dbn_core_years[min(t * 3 - 2, n_years)]

	for (i in 1:(n_actors - 1)) {
		for (j in (i + 1):n_actors) {
			dbn_dyad_scores[[length(dbn_dyad_scores) + 1]] = tibble(
				iso3_1 = dbn_core_actors[i],
				iso3_2 = dbn_core_actors[j],
				year = yr,
				dbn_structural = (cor_mat[i, j] + 1) / 2  # rescale [-1,1] to [0,1]
			)
		}
	}
}

dbn_scores = bind_rows(dbn_dyad_scores)

# compute posterior mean A_t (sender dynamics)

# A is a list of [n x n x T_stored] matrices, one per draw
A_mean = Reduce('+', lapply(dbn_core$A, function(a) a)) / n_draws

# extract coupling trajectories (row norms of A)
coupling = matrix(NA, n_actors, T_stored)
for (t in 1:T_stored) {
	for (i in 1:n_actors) {
		coupling[i, t] = sqrt(sum(A_mean[i, , t]^2))
	}
}
rownames(coupling) = dbn_core_actors

# save
write_csv(dbn_scores, file.path(res_scores, 'dbn_dyad_scores.csv'))

# save coupling trajectories
coupling_df = as_tibble(coupling, rownames = 'iso3') %>%
	pivot_longer(-iso3, names_to = 'time_idx', values_to = 'coupling') %>%
	mutate(time_idx = as.integer(gsub('V', '', time_idx)))
write_csv(coupling_df, file.path(res_scores, 'dbn_coupling.csv'))
