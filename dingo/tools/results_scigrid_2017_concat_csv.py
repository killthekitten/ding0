import pandas as pd
import os

file_base_name = 'mvgd_nodes_stats_{}.csv'
base_path = '/home/guido/mnt/srv01/04_Projekte/140_open_eGo/04-Projektinhalte/AP2/AP2.6_Generierung_synthetischer_Netze/dingo_results/results'

mvgd_ids = list(range(1,500))

list_ = []
filenames = []
[filenames.append(file_base_name.format(mvgd_id)) for mvgd_id in mvgd_ids]

for filename in filenames:
    df = pd.read_csv(os.path.join(base_path, filename), index_col=None, header=0)
    list_.append(df)

frame = pd.concat(list_)

print(frame)
