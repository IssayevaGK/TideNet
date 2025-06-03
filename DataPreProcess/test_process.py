from trip_count import *
from meshing import *
from trip2trips import *
from trips2new import *
from trips_drop import *
from trips_split import *
from trips_graph import *
from gather_time_loc_diff import *


data_name = 'AIS_new'

trip_count('csv', data_name)
meshing('csv', data_name)
trip2trips('csv', data_name)
trips2new('csv', data_name)
trips_drop('csv', data_name)
trips_split('csv', data_name)
trips_graph('csv', data_name)
gather_time_loc_diff('csv', data_name)