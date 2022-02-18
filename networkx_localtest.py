import h5py
import glob
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class DataAnalizer():
    def __init__(self, datafile) -> None:
        self.filepath = glob.glob(f'resources/{datafile}')[0]

    def read_file(func):
        def wrapper(self,*args,**kwargs):
            with h5py.File(self.filepath, "r") as f:
                return func(self,f,*args, **kwargs)
        return wrapper

    @staticmethod
    def num_sort(filename_with_int):
        return list(map(int, re.findall(r'\d+', filename_with_int)))[0]

    @read_file
    def return_group_data_labels(self, data_file) -> list:
        a_group_key = list(data_file.keys())[0]
        labels = [f'Hour {i+1}' for i in range(len(data_file[a_group_key]))]
        values = sorted(list(data_file[a_group_key]), key=self.num_sort)
        return [{'label': l, 'value': v} for l, v in zip(labels, values)]

    @read_file
    def return_current_data(self, data_file):
        a_group_key = list(data_file.keys())[0]
        hour = list(data_file[a_group_key])[0]
        data_labels = list(data_file[f'{a_group_key}/{hour}'])
        for x in data_labels:
            print(np.array(data_file[f'{a_group_key}/{hour}/{x}']))
            print("\n##################################\n")
            
    @read_file 
    def get_current_data(self,data_file,hour):
        a_group_key = list(data_file.keys())[0]
        data_labels = list(data_file[f'{a_group_key}/{hour}'])
        return {i:np.array(data_file[f'{a_group_key}/{hour}/{i}'])for i in data_labels}
    


Analyzer = DataAnalizer('task_data.hdf5')

data = Analyzer.get_current_data('hour_1')

G = nx.Graph()


G.add_nodes_from([(int(node[0]), {'type': node[1], 'demand': node[2]}) for node in data['nodes']])
G.add_edges_from([(edge[0], edge[1],{'flow' : edge[2]}) for edge in data['branches']])

for i in data['gens']:
    G.nodes[i[0]]['generation'] = i[1]
    G.nodes[i[0]]['cost'] = i[2]



fig = plt.figure(1)
ax = fig.add_subplot(111)
pos = nx.spring_layout(G, k=0.25, iterations=1000)
color_map = ['red' if 'generation' in G.nodes[n] else 'blue' for n in G.nodes]


edges, weights = zip(*nx.get_edge_attributes(G, 'flow').items())
nodes, values = zip(*nx.get_node_attributes(G, 'demand').items())
node_size = [node_type[1] * 200 for node_type in data['nodes']]

cmap = plt.cm.winter
cmap2 = plt.cm.twilight_shifted

hist_val = {}
for n in G.nodes:
    flow = 0
    for nbr in G.neighbors(n):
        flow += G.edges[(n,nbr)]['flow']
    hist_val[n] = flow


nk = nx.draw_networkx(G, arrows=False, pos=pos, with_labels=True, node_size=node_size, font_color='white', font_size=9, font_weight='bold',
                      node_color=values, edgelist=edges, edge_color=weights, edge_cmap=cmap, nodelist=nodes, cmap=cmap2)

edge_lables = {(edge[0],edge[1]):round(edge[2]['flow'],2) for edge in G.edges(data=True)}



vmin = min(weights)
vmax = max(weights) +10

sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm2 = plt.cm.ScalarMappable(cmap=cmap2,  norm=plt.Normalize(
    vmin=min(values), vmax=max(values)))

cbar = plt.colorbar(sm)
cbar2 = plt.colorbar(sm2, ax=[ax], location='left')
cbar.set_label("Flow rate [MW]")
cbar2.set_label("demand [MW]")
plt.show()

fig = plt.figure(2)
plt.bar(hist_val.keys(),hist_val.values())
plt.legend()
plt.show()

