import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html


navbar = dbc.NavbarSimple(
    brand="EIT Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

main_setting = dbc.Card(
    dbc.CardBody([
        html.H2("Main Settings"),
        dbc.FormGroup(
            [
            dbc.Label("Geometry"),
            dbc.Select(
            id="select-geometry",
            options=[
                {"label": "Throx", "value": "throx"},
                {"label": "Throx Anomaly", "value": "throx_anomaly"},
                {"label": "Disc", "value": "disc"},
                {"label": "Disc Anomaly", "value": "disc_anomaly"},
                {"label": "Anomaly Perm", "value": "anomaly_perm"}
            ],
            value="throx"
        )]),
        dbc.FormGroup(
            [
            dbc.Label("Number of Electrodes"),
            dbc.Input(
            id='number-electrodes',
            step="1",
            placeholder="",
            value=16,
            type="number",
            min=0)]
        ),
        dbc.FormGroup(
            [
            dbc.Label("Upload Reference Data (npy file)"),
            dcc.Upload(
                    id='upload-reference-data',
                    children=html.Div([
                        html.A('Select File')
                    ]),
                    style={
                        'width': '100%',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    }
                )
            ]
        ),
    dbc.FormGroup(
            [
            dbc.Label("Upload Data Series (npy file)"),
            dcc.Upload(
                    id='upload-data-series',
                    children=html.Div([
                        html.A('Select File')
                    ]),
                    style={
                        'width': '100%',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    }
                )
            ]
        ),
        dbc.Card(dbc.CardBody(
        dbc.FormGroup(
                [
                    html.H5("Choose Visuals", style={"font-weight":"bold"}),
                    dbc.Checklist(
                        options=[
                            {"label": "Absolute", "value": "absolute"},
                            {"label": "Relative", "value": "relative"},
                            {"label": "Raw", "value": "raw"}
                        ],
                        value=[],
                        id="visual-checklist",
                    ),
                    dbc.Row(
                        [dbc.Col(
                            dbc.Button('Update Visuals', id="update-visuals", color="success",className="mt-3")
                        )]
                    )
                ]
            )),color="success",outline=True)
    ]),
    className="m-3"
)

absolute_settings = dbc.Card(
    dbc.CardBody([
        html.H2("Absolute Image settings"),
        dbc.FormGroup(
            [
                dbc.Label("Number of Frames (Average)"),
                dbc.Input(
                    id='absolute-num-frames',
                    placeholder="",
                    type="number",
                    value=100,
                    min=1)]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Choose starting frame"),
                html.Div([dcc.Slider(
                    disabled=True,
                    id="absolute-slider")
                    ],
                className="mt-2",
                id='absolute-starting-frame-slider')
                ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Max Iterations"),
                dbc.Input(
                    id='absolute-max-iters',
                    placeholder="",
                    type="number",
                    value=40,
                    min=1)]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Regularization Parameter (Lambda)"),
                dbc.Input(
                    id='absolute-lambda',
                    placeholder="",
                    value=1,
                    type="number",
                    step="any",
                    className="no-arrow",
                    min=1),
                dbc.Checklist(
                    options=[
                        {"label": "Automatically Optimize", "value": True}
                    ],
                    value=[],
                    id="optimize-switch-absolute",
                    switch=True,
                    className="mt-1"
                )
            ]
        ),
        dbc.FormGroup(
            [
            dbc.Label("Upload Prior Information (npy file, optional)"),
            dcc.Upload(
                    id='prior-info-absolute',
                    children=html.Div([
                        html.A('Select File')
                    ]),
                    style={
                        'width': '100%',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    }
                )
            ]
        )
    ]),
    className="m-3")


relative_settings = dbc.Card(
    dbc.CardBody([
        html.H2("Relative Dynamic Image settings"),
        # dbc.FormGroup(
        #     [
        #         dbc.Label("Number of Frames "),
        #         dbc.Input(
        #             id="relative-num-frames",
        #             placeholder="",
        #             step="1",
        #             type="number",
        #             min=1)]
        # ),
        dbc.FormGroup(
            [
                dbc.Label("Choose frame range to visualize", html_for="relative-range-slider"),
                html.Div([dcc.RangeSlider(id="relative-range-slider", min=0, max=10, disabled=True)],
                         id="relative-range-slider-div", className="mt-2",)
            ]
        )
        ,
        dbc.FormGroup(
            [
                dbc.Label("Regularization Parameter (Lambda)"),
                dbc.Input(
                    id="relative-lambda",
                    placeholder="",
                    type="number",
                    step="any",
                    value=0.005,
                    min=0
                    ),
                dbc.Checklist(
                    options=[
                        {"label": "Automatically Optimize", "value": True}
                    ],
                    value=[],
                    id="optimize-switch-relative",
                    switch=True,
                    className="mt-1"
                ),
            ]
        ),
        dbc.FormGroup(
            [
            dbc.Label("Upload Prior Information (npy file, optional)"),
            dcc.Upload(
                    id='prior-info-relative',
                    children=html.Div([
                        html.A('Select File')
                    ]),
                    style={
                        'width': '100%',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    }
                )
            ]
        )
    ]),
    className="m-3")

settings_content = html.Div([dbc.Row(
            [
                dbc.Col(main_setting),
                dbc.Col(absolute_settings),
                dbc.Col(relative_settings),
            ]
        )])

settings_tab = dbc.Card(
    dbc.CardBody(
        [
           settings_content,
        ]
    ),
    className="m-3 overflow-auto",
    style={"height": "100vh","backgroundColor":"#F6F6F6"}
)

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

tabs = dbc.Tabs(children=[
        dbc.Tab(settings_tab, label="Settings", tab_id='Settings'),
        dbc.Tab(visual_tab, label="Visualize", tab_id="Visualize"),
    ], className="m-3",id="select-tab"
)
