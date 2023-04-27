import dash
import requests
import psycopg2
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, dash_table, ctx
import base64

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

def execute_dag(dag_id = 'dag_train_evaluation_pipeline', params = {}):
    # dag_postgres_upload OR dag_train_evaluation_pipeline
    username = 'airflow'
    password = 'airflow'
    auth = base64.b64encode(f"{username}{password}".encode()).decode()

    auth = (username, password)

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }

    url = f'http://fuelproject-airflow-webserver-1:8080/api/v1/dags/{dag_id}/dagRuns'
    response = requests.post(url, headers=headers, json={"conf": params}, auth = auth)
    print(response)
    print(response.text)

def execute_query(query):

    dataframe = None

    connection = psycopg2.connect(
        host = "postgres",
        database = "postgres",
        user = "airflow",
        password = "airflow"
    )
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        headers = [desc[0] for desc in cursor.description]
        raw_data = cursor.fetchall()

        dataframe = pd.DataFrame(raw_data, columns = headers)

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
    
    return dataframe

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("FuelProject", className="display-4"),
        html.Hr(),
        html.P(
            "Menu", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Db Init & Queries", href="/", active="exact"),
                dbc.NavLink("Train a DNN", href="/query", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

page_1 = html.Div([
    dbc.Col([
        dbc.Button('Initialize a New Database!', id = 'init-db', n_clicks = 0, style = {"background-color": 'green'}),
        html.Div(id = 'init-db-msg'),
        html.Br(),
        dbc.Button('Get all models with a MAE smaller than 2.5 from the past week', id = 'btn-1', n_clicks = 0),
        dbc.Button('Get all model data', id = 'btn-2', n_clicks = 0, style = {"background-color": 'orange'}),
        html.P(),
        html.Div(id = 'sql_output')
    ]),
    
])
page_2 = html.Div([
    html.P("neurons"),
    dcc.Input(id = 'neurons', type = 'number', value = 64),
    html.P(),
    html.P("number of layers"),
    dcc.Input(id = 'number_of_layers', type = 'number', value = 5),
    html.P(),
    html.P("validation split"),
    dcc.Input(id = 'validation_split', type = 'number', value = 0.2),
    html.P(),
    html.P("loss fn"),
    #dcc.Input(id = 'loss', type = 'text', value = 'mean_aboslute_error'),
    dcc.Dropdown(
        id = 'loss',
        options = [
            {"label": "MSE", 'value': 'mean_squared_error'},
            {"label": "MAE", 'value': 'mean_absolute_error'}
        ],
        value = 'mean_absolute_error',
        style = {
            'width': '210px'
        }
    ),
    html.P(),
    html.P("kernel initializer"),
    dcc.Input(id = 'kernel_initializer', type = 'text', value = 'glorot_uniform'),
    html.P(),
    html.P("kernel regularizer"),
    dcc.Input(id = 'kernel_regularizer', type = 'number', value = None),
    html.P(),
    html.P("activation"),
    dcc.Input(id = 'activation', type = 'text', value = 'relu'),
    html.P(),
    html.P("learning rate"),
    dcc.Input(id = 'learning_rate', type = 'number', value = 0.1),
    html.P(),
    html.P("epochs"),
    dcc.Input(id = 'epochs', type = 'number', value = 50),
    html.P(),
    html.Button("Execute DAG", id = 'start-dag-button', n_clicks = 0),
    html.P(),
    html.Div(id = 'dag-status')
])

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/":
        return page_1
    elif pathname == "/query":
        return page_2
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

@app.callback(
    Output("sql_output", 'children'),
    Input("btn-1", "n_clicks"),
    Input('btn-2', 'n_clicks')
)
def show_table(button1, button2):
    if ctx.triggered_id == 'btn-1':
        query = """SELECT model_metadata.model_type, model_metadata.model_training_date, model_metadata.test_loss
                   FROM model_metadata
                   WHERE model_metadata.model_training_date > (NOW() - interval '7 days') AND model_metadata.test_loss <= 2.5 AND model_metadata.loss_metric = 'mean_absolute_error';"""
        df = execute_query(query)
        return dash_table.DataTable(
            df.to_dict('records'),
            [{"name": i, "id": i} for i in df.columns],
            style_cell = {
                "overflow": "hidden",
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },
            page_size = 10
        )
    if ctx.triggered_id:
        query = """SELECT model_metadata.model_type, model_metadata.model_training_date, model_metadata.loss_metric, model_metadata.train_loss, model_metadata.test_loss, model_metadata.comparison_to_base
                FROM model_metadata
                ORDER BY model_metadata.model_training_date DESC;"""
        df = execute_query(query)
        return dash_table.DataTable(
            df.to_dict('records'),
            [{"name": i, "id": i} for i in df.columns],
            style_cell = {
                "overflow": "hidden",
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },
            page_size = 10
        )

@app.callback(
    Output('dag-status', 'children'),
    Input("start-dag-button", 'n_clicks'),
    State('neurons', 'value'),
    State('number_of_layers', 'value'),
    State('validation_split', 'value'),
    State('loss', 'value'),
    State('kernel_initializer', 'value'),
    State('kernel_regularizer', 'value'),
    State('activation', 'value'),
    State('learning_rate', 'value'),
    State('epochs', 'value')
)
def trigger_dag(btn, neur, no_layers, val_splt, loss, kern_init, kern_reg, activ, lr, epochs):
    if btn > 0:
        params = {
            "neurons": neur,
            "number_of_layers": no_layers,
            "validation_split": val_splt,
            "loss": loss,
            "kernel_initializer": kern_init,
            "kernel_regularizer": kern_reg,
            "activation": activ,
            "learning_rate": lr,
            "epochs": epochs
        }
        with open("sent_conf.txt", "w") as f:
            f.write(str(params))
        
        execute_dag(dag_id = 'dag_train_evaluation_pipeline', params = params)
        return f"Your dag was ran {btn} times!"

@app.callback(
    Output('init-db-msg', 'children'),
    Input('init-db', 'n_clicks')
)
def initialise_database(clicks):
    if clicks > 0:
        execute_dag(dag_id = 'dag_postgres_upload',)
        return "DB initialised!"
        

if __name__ == "__main__":
    app.run_server(host = '0.0.0.0', port = 5000, debug = False)