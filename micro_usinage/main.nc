;**********************
;PROGRAMME PRINCIPAL
;              **********************

T1 M6
G53 G01 Z+24 F1000
G55 G90
L sub_spirale_surface_milling.nc
L sub_spirale_measurements.nc
M05
T0 M6
M30
