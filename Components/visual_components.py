import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

visual_relative = dbc.Card(
    dbc.CardBody(
        [
            dbc.Modal(id='show-roi-modal', is_open=False,size="xl",centered=True),
            html.H2("Relative Image Visual"),
            html.Br(),
            dbc.Row([
                dbc.Col(
                html.Div([
                    dcc.Loading(
                        type="default",
                        children=html.Video(id='relative-video', controls=True,src="")
                    )
                ]))
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Button("Update", id="relative-update", className="mt-1", color="success")),

            ]
            ),

            dbc.FormGroup([
                dbc.Select(
                    id="select-roi",
                    options=[
                        {"label": "Quadrant", "value": "quadrant"}
                    ],
                    value='quadrant'
                ),
                dbc.Button("Show ROI", id="show-roi", className="mt-1 ml-3", color="warning")
            ],className="mt-1")


        ]
    )
)

visual_absolute = dbc.Card(
    dbc.CardBody(
        [
            dbc.Modal(id='visual-modal', is_open=False),
            dbc.Modal(id='convergence-modal', is_open=False),
            html.H2("Absolute Image Visual"),
            html.Br(),
            dbc.Row([
                dbc.Col(
                html.Div([
                    dcc.Loading(
                        type="default",
                        children=html.Img(id="absoluteimage",src="",style={"width":"90%","height":"auto"})
                    )
                ]))
            ]),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(html.Div(id="update-button-absolute-container",children=[
                        dbc.Button("Update", id='absolute-update', className="mt-1", color="success")
                    ])),
                    # dbc.Col(dbc.Button("Show convergence", id="absolute-convergence",
                    #                    className="mt-1",color="warning",style={"display":"none"}))
                ]
            )
        ]
    )
)

visual_raw_data = dbc.Card(
    dbc.CardBody(
        [
            html.H2("Raw Data Visual"),
            html.Br(),
            dbc.Row([
                dbc.Col(
                html.Div([
                    dcc.Loading(
                        type="default",
                        children=html.Video(id='raw-video', controls=True, src="")
)
                ],id="raw-data-div"))
            ]),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(html.Div(children=[
                        dbc.Button("Show raw", id="raw-show", className="mt-1", color="success")
                    ]))
                ]
            )
        ]
    )
)


visual_content = html.Div([dbc.Row(
    [dbc.Col(visual_absolute,width=6),
     dbc.Col(visual_relative,width=6)]
,id="visual-content",justify='around'),
], className="d-flex align-content-around flex-wrap")

visual_tab = html.Div([
    dbc.Card(
    dbc.CardBody(
        [
            visual_content
        ]),
    className="m-3 overflow-auto",
    style={"height": "auto","backgroundColor":"#F6F6F6"})])