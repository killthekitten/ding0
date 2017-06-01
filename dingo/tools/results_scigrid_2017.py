from dingo.tools import config as cfg_dingo
from dingo.tools import results

cfg_dingo.load_config('config_db_tables.cfg')
cfg_dingo.load_config('config_calc.cfg')
cfg_dingo.load_config('config_files.cfg')
cfg_dingo.load_config('config_misc.cfg')

base_path = "/home/guido/mnt/srv01/04_Projekte/140_open_eGo/04-Projektinhalte/AP2/AP2.6_Generierung_synthetischer_Netze/dingo_results/"
dingo = results.ResultsDingo(base_path)

# concat nd-pickles for single range
first_mvgd = 3601
last_mvgd = 3608
#dingo.concat_nd_pickles(list(range(first_mvgd,last_mvgd + 1)))
#ranges = [tuple([first_mvgd, last_mvgd])]
#dingo.concat_csv_stats_files(ranges)

# concat nd-pickle in multiple steps
#ranges = []
#for step in list(range(1,3501,100)):
    #dingo.concat_nd_pickles(list(range(1+step,101+step)))

    # concat csv files of larger ranges
    #ranges = [tuple([5,15]), tuple([16,24])]
    #ranges.append(tuple([0+step,99+step]))
#ranges.append(tuple([first_mvgd, last_mvgd]))
#print(ranges)
#dingo.concat_csv_stats_files(ranges)

# create results figures and numbers based of concatenated csv file
concat_csv_file_range = [1, 3608]
dingo.read_csv_results(concat_csv_file_range)

## calculate stats
mvgd_stats = dingo.calculate_mvgd_stats()
global_stats = dingo.calculate_global_stats()
print(mvgd_stats)
dingo.plot_cable_length()
for key in list(global_stats.keys()):
    print(key, global_stats[key])
