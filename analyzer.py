import h5py
import glob
import re
import networkx as nx
import numpy as np 
import plotly.graph_objs as go


class DataAnalizer():
    def __init__(self,datafile) -> None:
        self.filepath = glob.glob(f'resources/{datafile}')[0]
        self.pos = None
        self.generated_graph = False

    def read_file(func):
        """Decorator opening file
        """
        def wrapper(self, *args, **kwargs):
            with h5py.File(self.filepath, "r") as f:
                return func(self, f, *args, **kwargs)
        return wrapper

    @staticmethod
    def num_sort(filename_with_int) -> list:
        """Method using re to get real name of dataset

        Args:
            filename_with_int (_str_): dataset name

        Returns:
            list: sorted names
        """
        return list(map(int, re.findall(r'\d+', filename_with_int)))[0]
    
    @staticmethod
    def get_color_for_edge(flow) -> str:
        """Method returns color of edge depends on flow value

        Args:
            flow ('_float_'): flow value

        Returns:
            str: hexcolor 
        """
        if flow < 0:
            flow = -1 * flow
 
        for _min, _max, color in [(0, 2, "#06f72c"), (2, 4, "#98bc00"), (4, 6, "#ab8f00"), (6, 8, "#a56600"), (8, 10, "#773729")]:
            if _min <= flow <= _max:
                return color
        
        return "#582a2a"
                
    
    @read_file
    def return_group_data_labels(self,data_file) -> list:
        """Method reading dataset labels

        Args:
            data_file (__h5py__): dataset

        Returns:
            list: list of sorted dicts with label and dataset
        """
        a_group_key = list(data_file.keys())[0]
        labels = [f'Hour {i+1}' for i in range(len(data_file[a_group_key]))]
        values = sorted(list(data_file[a_group_key]),key=self.num_sort)
        return [{'label': l, 'value': v} for l,v in zip(labels,values)]
    
            
    @read_file
    def get_current_data(self, data_file, hour) -> dict:
        """Method returns current dataset based on hour

        Args:
            data_file (__h5py__): dataset
            hour (_str_): hour

        Returns:
            dict: current hour dataset
        """
        a_group_key = list(data_file.keys())[0]
        data_labels = list(data_file[f'{a_group_key}/{hour}'])
        return {i: np.array(data_file[f'{a_group_key}/{hour}/{i}'])for i in data_labels}

            
    def get_data_for_plot(self, hour):
        """Method returns data using for plots

        Args:
            hour (_str_): hour

        Returns:
            list: data
            G.object: Graph object
        """
        data = self.get_current_data(hour)
        G = nx.Graph()
        G.add_nodes_from(
            [(int(node[0]), {'type': node[1], 'demand': node[2]}) for node in data['nodes']])
        G.add_edges_from(
            [(edge[0], edge[1], {'flow': edge[2]}) for edge in data['branches']])
        for i in data['gens']:
            G.nodes[i[0]]['generation'] = i[1]
            G.nodes[i[0]]['cost'] = i[2]


        if not self.generated_graph: # stick the same position for all graphs
            self.pos = nx.spring_layout(G, k=0.25, iterations=1000)
            self.generated_graph = True
            
        for i in G.nodes:
            G.nodes[i]['pos'] = self.pos[i]
            
        traceRecode = []
        
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                line=dict(width=2),
                colorbar=dict(
                    thickness=15,
                    title='Node power demand [MW]',
                    xanchor='left',
                    titleside='right'
                ),))

        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])

        for node, adjacencies in enumerate(G.adjacency(), 1): #fill nodes with values for labels
            flow_info_up = ''
            flow_info_down = ''
            node_trace['marker']['color'] += tuple([G.nodes[node]['demand']])

            for k, v in adjacencies[1].items():
                if v['flow'] < 0:
                    flow_info_up += f"<br>To node {k} flow equals {v['flow']} [MW]"
                else:
                    flow_info_down += f"<br>From node {k} flow equals {v['flow']} [MW]"

            node_info = f'Node_ID:{node} <br>Node_type:{G.nodes[node]["type"]}<br>Flow rate with nodes: {flow_info_up}{flow_info_down}'

            if 'generation' in G.nodes[node]:
                node_info += f"<br>Generation: {G.nodes[node]['generation']} [MW] <br>Generation cost per unit: {G.nodes[node]['cost']} [zł per MW]"
            node_trace['text'] += tuple([node_info])
        
        traceRecode.append(node_trace)
        
        colors = [self.get_color_for_edge(x[2]['flow']) for x in G.edges.data()] # colors for edges
   
        index = 0
        
        for edge in G.edges():
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            
            edge_trace = go.Scatter(
                x=tuple([x0,x1,None]),
                y=tuple([y0,y1,None]),
                mode='lines',
                marker=dict(color=colors[index]),
                line=dict(
                    width=1,
                ))
            traceRecode.append(edge_trace)
            index += 1
           
   
        return traceRecode, G
        
        


