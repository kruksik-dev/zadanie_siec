from dash import html, dcc, dash_table
from analyzer import DataAnalizer
import dash_bootstrap_components as dbc




class AppLayout():
    def __init__(self,app) -> None:
       self.app = app
       self.picked_data = None
       self.analyzer = DataAnalizer("task_data.hdf5")
       self.create_layout()
      
    

    def create_layout(self):
        
        self.group_data_labels = self.analyzer.return_group_data_labels()

        self.app.layout = html.Div(children=[
            html.Div(children=[
            html.H1(children='Analysis of the power grid operation between individual hours',className='title'),
            html.Div(children='Test task created by Maciej Krakowiak',className='Description'),
            ],className='top'),
            
            html.Div(children=[
            html.P(children='Please select an hour from list:', className='label_dd center'),
                html.Div(dcc.Dropdown(options=self.group_data_labels, id='demo-dropdown',
                         className='dd-menu center', placeholder="Select a Hour")),
                html.Div(id='dd-output-container',
                         className='datasetlabel center')
            ],className='settings-grid'),
            
           
            html.Div(children=[
                     dbc.Card([
                         dbc.CardHeader("Nodes info"),
                         dbc.CardBody([
                         dash_table.DataTable(id='table', columns=[{"name": i, "id": str(e)} for e, i in enumerate(
                         ['Generator ID', 'Generation power [MW]', 'Cost of power unit [zł]'])], data=[], style_cell={"textAlign": "center"}, style_table={'height': 'auto'}),
                         html.Div(dcc.Graph(id='Graph-histo'), className='graph_histo')
                                        ], className='card-body')
                     ]),
                     
                     
                     dbc.Card([
                         dbc.CardHeader("Power grid plot"),
                         dbc.CardBody([
                             html.Div(dcc.Graph(id='Graph-network'),
                                      className='graph')
                         ], className='card-body')
                     ]),
                
     
                        ],className='DataPanel'),
            
            html.Div(children=[
                dbc.Card([
                    dbc.CardHeader("Summary of nodes flow"),
                    dbc.CardBody([
                        dcc.Graph(id="Graph-bars")
                    ])
                ])
            ],className='bottomplot')
            
        ])



     
    
   

       
                        



