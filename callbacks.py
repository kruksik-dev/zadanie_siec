import plotly.express as px
from dash import Input, Output
from pandas import DataFrame
import plotly.graph_objs as go
import numpy as np

class BaseCalls:
    def __init__(self, app=None):
        self.app = app
        if self.app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.app)

class Callbacks(BaseCalls):
    def __init__(self, app=None, layout=None):
        super().__init__(app)
        self.layout = layout
        self.data_labels = [x['value'] for x in self.layout.group_data_labels]
        self.data = {x: self.layout.analyzer.get_data_for_plot(x) for x in self.data_labels}
       
  
    def callbacks(self, app):
        @app.callback(Output('dd-output-container', 'children'),Input('demo-dropdown', 'value'))
        def update_dataset(value):
            self.layout.picked_data = value
            return f'The following data is presented for the selected Dataset : {self.layout.picked_data}'
    
        @app.callback(Output('Graph-network', 'figure'), [Input('demo-dropdown', 'value')])
        def upgrade_graph_network(value):
            if not value:
                return go.Figure(layout=go.Layout(width=1250))
            traceRecode, _ = self.data[value]
            fig = go.Figure(data=traceRecode,
                            layout=go.Layout(
                title='Power grid for a given hour, edges color based on flow values (gradient green-red)',
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                plot_bgcolor='#fff',
                height = 757,
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False,
                        showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
            return fig
        
        @app.callback([Output('table', 'data'), Output('table', 'columns')], [Input('demo-dropdown', 'value')])
        def update_table_data(value):
            if not value:
                df = DataFrame(data=[], columns=[
                    'Generator ID', 'Generation power [MW]', 'Cost of power unit [zł]'])
                return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
            *_, G = self.data[value]
            values = []
            for i in G.nodes.data():
                if 'generation' in i[1]:
                    values.append(np.array([str(i[0]),i[1]['generation'],i[1]['cost']]))
            df = DataFrame(data=values, columns=[
                           'Generator ID', 'Generation power [MW]', 'Cost of power unit [zł]'])
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
        
        @app.callback(Output('Graph-histo', 'figure'), Input('demo-dropdown', 'value'))
        def upgrade_graph_histo(value):
            if not value:
                return go.Figure(layout=go.Layout())
            *_, G = self.data[value]
            degrees = [G.degree[i] for i in G.nodes]
            fig = px.histogram(degrees, nbins=len(degrees),  labels={"value": "Number of connected nodes"})
            fig.update_layout(showlegend=False)
            return fig
        
        @app.callback(Output('Graph-bars', 'figure'), [Input('demo-dropdown', 'value')])
        def update_graph_bars(value):
            if not value:
                return px.bar()
            *_, G = self.data[value]
            hist_val = []

            for n in G.nodes():
                flow = 0
                for nbr in G.neighbors(n):
                    flow += G.edges[(n, nbr)]['flow']
                hist_val.append([n, flow])

            df = DataFrame(hist_val, columns=['Node_ID', 'Flow summary [MW]'])
            fig = px.bar(df, x="Node_ID", y="Flow summary [MW]")
            return fig
               


            
