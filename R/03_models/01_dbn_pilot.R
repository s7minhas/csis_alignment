########################################################
# run dbn dynamic model (pilot, ~40 actors)
# unga voting layer, all 32 cores
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

# load arrays
load(file.path(data_nets, 'dbn_arrays.rda'))  # Y_std, all_actors, YEARS

# define pilot actor set (policy-relevant countries)
pilot_actors = sort(intersect(c(
	# g7
	'USA', 'GBR', 'FRA', 'DEU', 'ITA', 'JPN', 'CAN',
	# brics+
	'BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'EGY', 'IRN', 'SAU', 'ARE',
	# key csis interest
	'KOR', 'AUS', 'TUR', 'IDN', 'MEX', 'NGA', 'PAK', 'ISR', 'UKR', 'POL',
	'THA', 'VNM', 'PHL', 'ARG', 'COL', 'CUB', 'PRK', 'SGP', 'MYS',
	'KEN', 'ETH', 'KAZ', 'QAT', 'DZA', 'IRQ', 'SYR', 'JOR', 'MMR'
), all_actors))

n_pilot = length(pilot_actors)
pilot_idx = match(pilot_actors, all_actors)

# use unga layer only for the pilot (best coverage, most relevant)
Y_pilot = Y_std[pilot_idx, pilot_idx, 1, , drop = FALSE]
dimnames(Y_pilot)[[1]] = pilot_actors
dimnames(Y_pilot)[[2]] = pilot_actors

# memory check
estimate_memory(n_row = n_pilot, n_col = n_pilot, p = 1, Tt = length(YEARS),
	nscan = 10000, burn = 2000, odens = 10, family = 'gaussian')

# run
set_dbn_threads(n_cores)

t0 = Sys.time()

dbn_pilot = dbn(
	data = Y_pilot,
	model = 'dynamic',
	family = 'gaussian',
	symmetric = FALSE,   # use asymmetric specification for flexibility
	nscan = 10000,
	burn = 2000,
	odens = 10,
	seed = 6886,
	verbose = 1000
)

t1 = Sys.time()

# save
save(dbn_pilot, pilot_actors, YEARS,
	file = file.path(res_models, 'dbn_pilot.rda'))
