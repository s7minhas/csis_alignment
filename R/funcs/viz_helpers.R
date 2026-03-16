########################################################
# visualization helpers — csis report style
########################################################

# csis color palette
csis_colors = c(
	us = '#2166AC',
	china = '#B2182B',
	russia = '#7B3294',
	neutral = '#636363',
	positive = '#2166AC',
	negative = '#B2182B',
	g7 = '#2166AC',
	brics = '#B2182B',
	global_south = '#1B7837'
)

# theme for csis report figures
theme_csis = function(base_size = 12) {
	theme_bw(base_size = base_size) +
		theme(
			plot.title = element_text(face = 'bold', size = base_size + 2),
			panel.border = element_blank(),
			panel.grid.minor = element_blank(),
			legend.position = 'bottom',
			strip.background = element_rect(fill = 'black', color = 'black'),
			strip.text.x = element_text(color = 'white', hjust = 0),
			strip.text.y = element_text(color = 'white', hjust = 0)
		)
}
