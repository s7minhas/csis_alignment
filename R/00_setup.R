########################################################
# dynamic alignment observatory — master setup
########################################################

# paths
proj_dir = '/home/s7m/Research/csis'
data_raw = file.path(proj_dir, 'data', 'raw')
data_proc = file.path(proj_dir, 'data', 'processed')
data_reg = file.path(proj_dir, 'data', 'registry')
data_nets = file.path(proj_dir, 'data', 'networks')
res_dir = file.path(proj_dir, 'results')
res_scores = file.path(res_dir, 'scores')
res_models = file.path(res_dir, 'models')
res_diag = file.path(res_dir, 'diagnostics')
res_valid = file.path(res_dir, 'validation')
res_figs = file.path(res_dir, 'figures')

# carbon / plutonium paths for parity checks
carbon_dir = '/home/s7m/Research/Carbon'
pluto_dir = '/home/s7m/Research/plutonium'
carbon_results = '/home/s7m/Dropbox/Research/Carbon/Results'

# packages
library(tidyverse)
library(countrycode)
library(netify)
library(lame)
library(dbn)

# cores
n_cores = parallel::detectCores(logical = TRUE)
set_dbn_threads(n_cores)

# helper source
source(file.path(proj_dir, 'R', 'funcs', 'actor_helpers.R'))
source(file.path(proj_dir, 'R', 'funcs', 'score_helpers.R'))
source(file.path(proj_dir, 'R', 'funcs', 'viz_helpers.R'))

# constants
ANCHOR_US = 'USA'
ANCHOR_CN = 'CHN'
MIN_YEAR = 1965
MAX_YEAR = 2024

# country group definitions
G7 = c('USA', 'GBR', 'FRA', 'DEU', 'ITA', 'JPN', 'CAN')
G7_PLUS = c(G7, 'AUS', 'KOR')
BRICS_ORIG = c('BRA', 'RUS', 'IND', 'CHN', 'ZAF')
BRICS_PLUS = c(BRICS_ORIG, 'EGY', 'ETH', 'IRN', 'ARE', 'SAU')
