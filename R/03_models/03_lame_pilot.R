########################################################
# lame pilot model (60 key countries, 1990-2024)
# produces: results/models/lame_pilot.rda
# this is the primary production model for the dashboard.
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

load(file.path(data_nets, 'dbn_arrays.rda'))  # Y_std, all_actors, YEARS

# define pilot actor set
pilot = sort(intersect(c(
	'USA', 'GBR', 'FRA', 'DEU', 'ITA', 'JPN', 'CAN',
	'BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'EGY', 'IRN', 'SAU', 'ARE',
	'KOR', 'AUS', 'TUR', 'IDN', 'MEX', 'NGA', 'PAK', 'ISR', 'UKR', 'POL',
	'THA', 'VNM', 'PHL', 'ARG', 'COL', 'CUB', 'PRK', 'SGP', 'MYS',
	'KEN', 'ETH', 'KAZ', 'QAT', 'DZA', 'IRQ', 'SYR', 'JOR', 'MMR',
	'ESP', 'NLD', 'SWE', 'NOR', 'CHE', 'BEL', 'GRC', 'PRT',
	'VEN', 'LBY', 'SDN', 'AFG', 'MAR', 'NZL', 'IRL', 'PER'
), all_actors))

idx = match(pilot, all_actors)
n = length(pilot)

# build list-of-matrices for 1990-2024
years = 1990:2024
t_start = which(as.character(years[1]) == as.character(YEARS))

Y_list = lapply(seq_along(years), function(t) {
	mat = Y_std[idx, idx, 1, t_start + t - 1]  # unga layer only
	rownames(mat) = pilot
	colnames(mat) = pilot
	mat
})
names(Y_list) = as.character(years)

# run lame
t0 = Sys.time()
fit = lame(Y = Y_list, R = 2, symmetric = TRUE, nvar = TRUE,
	dynamic_uv = TRUE, family = 'normal',
	nscan = 8000, burn = 2000, odens = 20,
	seed = 6886, print = TRUE, gof = TRUE)

# save
lame_pilot = fit
lame_pilot_actors = pilot
lame_pilot_years = years

save(lame_pilot, lame_pilot_actors, lame_pilot_years,
	file = file.path(res_models, 'lame_pilot.rda'))
