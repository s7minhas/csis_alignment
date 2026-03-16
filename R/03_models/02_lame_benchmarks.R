########################################################
# lame benchmarks (per-layer, full 193 countries)
# run longitudinal ame on unga voting layer
########################################################

source('/home/s7m/Research/csis/R/00_setup.R')

# load lame-format data
load(file.path(data_nets, 'lame_unga.rda'))   # unga_lame (list of matrices)
load(file.path(data_nets, 'dbn_arrays.rda'))   # all_actors, YEARS

# subset to post-1990 for better coverage
# pre-1990 has many missing countries, which makes lame unstable
start_idx = which(names(unga_lame) == '1990')
unga_lame_sub = unga_lame[start_idx:length(unga_lame)]

# run lame with dynamic latent positions
t0 = Sys.time()

lame_unga = lame(
	Y = unga_lame_sub,
	R = 2,
	symmetric = TRUE,
	nvar = TRUE,
	dynamic_uv = TRUE,
	family = 'normal',
	nscan = 10000,
	burn = 2000,
	odens = 25,
	seed = 6886,
	print = TRUE,
	gof = TRUE
)

t1 = Sys.time()

# save
save(lame_unga, file = file.path(res_models, 'lame_unga.rda'))
