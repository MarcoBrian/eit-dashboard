import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html


main_setting = dbc.Card(
    dbc.CardBody([
        html.H2("Main Settings"),
        dbc.FormGroup(
            [
            dbc.Label("Geometry"),
            dbc.Select(
            id="select-geometry",
            options=[
                {"label": "Thorax", "value": "throx"},
                {"label": "Thorax Anomaly", "value": "throx_anomaly"},
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
        dbc.FormGroup(
            [
                dbc.Label("Number of Frames to average "),
                dbc.Input(
                    id="relative-num-frames",
                    placeholder="",
                    step="1",
                    value=10,
                    type="number",
                    min=1)]
        ),
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
                dbc.Label("VMin, VMax (Optional, abs value)"),
                dbc.Input(
                    id="vminmax",
                    placeholder="",
                    type="number",
                    step="any",
                    value=0.05,
                    min=0
                    )])
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

def UploadStyleUpdate(data):
    uploaded_style = {
        'width': '100%',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'solid',
        'backgroundColor': "#39DB80",
        "color": "#FFFFFF",
        'borderRadius': '5px',
        'textAlign': 'center',
    }
    error_style = {
                        'width': '100%',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'backgroundColor':"#E74C3C",
                        "color": "#FFFFFF",
                        'borderRadius': '5px',
                        'textAlign': 'center',
                    }
    uploaded_text = html.Div([html.A("Success! Click to re-upload file.")])
    error_text = html.Div([html.A("Error parsing file. Try again")])
    if data is None:
        return error_text,error_style
    else:
        return uploaded_text,uploaded_style
