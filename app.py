import dash
from  flask import Flask, session
import numpy as np
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import uuid

import time
from dash.dependencies import Input, Output, State
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


from pyeit.mesh.meshpy.build import create
from pyeit.eit.utils import eit_scan_lines
import pyeit.eit.jac as jac
from pyeit.eit.interp2d import sim2pts

from Components.tabs_component import *
from Helpers.helpers import  *

# Global variables
dataSeries = None
dataRef = None
convergence_list = []
solved = []

server = Flask(__name__)
server.secret_key = "hello"
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])


def plotAbsoluteImage(args_dict):
    # Grabbing parameters
    num_eit = args_dict["number-electrodes"]
    curve = getShape(args_dict["select-geometry"])
    average_frames = args_dict["absolute-num-frames"]
    starting_frame = args_dict["absolute-slider"]
    lambda_parameter = args_dict["absolute-lambda"]
    max_iterations = args_dict["absolute-max-iters"]


    mesh_obj, el_pos = create(num_eit, curve=curve)
    pts = mesh_obj['node']
    tri = mesh_obj['element']
    tri_coord = np.mean(pts[tri], axis=1)
    # EIT setup: adjacent mode
    el_dist, step = 1, 1
    ex_mat = eit_scan_lines(num_eit, el_dist)
    # mesh
    x = pts[:, 0]
    y = pts[:, 1]
    # setup JAC solver
    eit = jac.JAC(mesh_obj, el_pos, ex_mat, step, perm=1.0, parser='fmmu')
    eit.setup(p=0.25, lamb=lambda_parameter, method='lm')
    start = time.time()

    # Ending frame is bounded by the length of the data series
    ending_frame = min(starting_frame+average_frames, len(dataSeries))

    selected_data = dataSeries[starting_frame:ending_frame]
    mean_data = np.mean(selected_data,axis=0)

    global convergence_list
    ds1,convergence_list = eit.gn(mean_data, lamb_decay=0.1, lamb_min=1e-5, maxiter=max_iterations, verbose=True,converge_info=True)

    end = time.time()

    print("Time taken:", (end - start))

    dsn1 = sim2pts(pts, tri, np.real(ds1))

    '''Plot the images '''
    # Draw the images
    fig = plt.figure()
    plt.jet()
    ax2 = fig.add_subplot(1, 1, 1)
    im2 = ax2.tripcolor(x, y, tri, np.real(dsn1), shading='flat')
    for i, k in enumerate(el_pos):
        vAlign = 'top' if y[k] < 0 else ('center' if y[k] == 0 else 'bottom')
        hAlign = 'right' if x[k] < 0 else ('center' if x[k] == 0 else 'left')
        ax2.annotate("%d" % i, xy=(x[k], y[k]), color='r', va=vAlign, ha=hAlign, ma='center')
    cb2 = plt.colorbar(im2, ax=ax2)
    ax2.set_aspect('equal')
    ax2.axis('off')
    return fig


def ValidateAbsoluteInputs(args_dict):
    if dataRef is None:
        return "Upload data reference from settings"

    if dataSeries is None:
        return "Upload data series from settings"

    if args_dict["select-geometry"] is None:
        return "Select a geometry in the settings"

    if args_dict["number-electrodes"] is None or not isinstance(args_dict["number-electrodes"],int) :
        return "Input valid number of electrodes in settings"

    if args_dict["absolute-num-frames" ] is None or not isinstance(args_dict["absolute-num-frames"],int):
        return "Input valid number of frames in settings"

    if args_dict["absolute-max-iters"] is None or not isinstance(args_dict["absolute-max-iters"], int):
        return "Input valid number of iterations in settings"

    if args_dict["absolute-lambda"] is None:
        return "Input valid lambda in settings"

    return None

def ValidateRelativeInputs(args_dict):

    if args_dict["select-geometry"] is None:
        return "Select a geometry in the settings"

    if args_dict["relative-num-frames"] is None or args_dict["relative-num-frames"]  < 1:
        return "Input valid number of frames to average in settings"

    if args_dict["number-electrodes"] is None or not isinstance(args_dict["number-electrodes"],int) :
        return "Input valid number of electrodes in settings"

    if args_dict["vminmax"] is None or args_dict["vminmax"] < 0 :
        return "Input valid number for Vmin Vmax"

    if args_dict["relative-lambda"] is None:
        return "Input valid lambda"

    return None

absolute_inputs = [
        Input(component_id='absolute-update',component_property='n_clicks')
    ]
absolute_states = [
        State(component_id='select-geometry',component_property='value'),
        State(component_id='number-electrodes',component_property='value'),
        State(component_id='absolute-num-frames',component_property='value'),
        State(component_id='absolute-max-iters',component_property='value'),
        State(component_id='absolute-lambda',component_property='value'),
        State(component_id='update-button-absolute-container',component_property='children'),
        State(component_id='absolute-slider', component_property='value')
    ]
@app.callback(
    [Output(component_id='visual-modal', component_property='is_open'),
     Output(component_id='visual-modal', component_property='children'),
     Output(component_id='absoluteimage', component_property='src'),
     Output(component_id='update-button-absolute-container',component_property='children')],
    absolute_inputs,
    absolute_states
)
def absolute_image_callback(*args):

    # gather input and states into one dictionary and named by component_id
    input_names = [item.component_id for item in absolute_inputs + absolute_states]
    args_dict = dict(zip(input_names,args))


    UpdateButton = dbc.Button("Update", id='absolute-update', className="mt-1", color="success")
    ConvergenceButton = dbc.Button("Show convergence", id="absolute-convergence",
                                       className="mt-1 ml-3",color="warning",disabled=False)
    button_container = []
    button_container.append(UpdateButton)
    button_container.append(ConvergenceButton)


    # first render do nothing (n_clicks is None)
    if args_dict["absolute-update"] is None:
        return False, dbc.ModalBody(""), "", args_dict["update-button-absolute-container"]

    error_string = ValidateAbsoluteInputs(args_dict)
    if error_string is None:
        AbsoluteImageFigure = plotAbsoluteImage(args_dict)
        out_url = fig_to_uri(AbsoluteImageFigure)
        return False,dbc.ModalBody(""), out_url, button_container
    else:
        return True, dbc.ModalBody(error_string,style={"color": "#E74C3C"}), "", button_container


@app.callback(
    Output('absolute-update', 'disabled'),
    [Input('absolute-update', 'n_clicks')]
)
def hide_absolute_update_button(n_clicks):
    if n_clicks is None:
        return False
    else:
        print('Disabling the button')
        return True




def createRelativeImage(args_dict):
    '''Setup for inverse problem'''
    num_eit = args_dict["number-electrodes"]
    window = args_dict["relative-num-frames"]
    curve = getShape(args_dict["select-geometry"])
    vminmax = args_dict["vminmax"]
    lambda_parameter = args_dict["relative-lambda"]
    start_frame, end_frame = args_dict["relative-range-slider"]
    print(start_frame)
    print(end_frame)

    mesh_obj, el_pos = create(num_eit, curve=curve)
    pts = mesh_obj['node']
    tri = mesh_obj['element']
    # EIT setup: adjacent mode
    el_dist, step = 1, 1
    ex_mat = eit_scan_lines(num_eit, el_dist)
    # mesh
    x = pts[:, 0]
    y = pts[:, 1]
    # setup JAC solver

    eit = jac.JAC(mesh_obj, el_pos, ex_mat, step, perm=1.0, parser='fmmu')
    '''Reconstruct a relative image'''

    eit.setup(p=0.35, lamb=lambda_parameter, method='kotre')
    global solved
    solved = []
    start = time.time()
    selected_dataSeries = dataSeries[start_frame:end_frame + 1,:]
    averaged_dataSeries = []

    frames = end_frame - start_frame + 1
    movingAverageLoop = frames - window + 1
    for i in range(movingAverageLoop):
        average = np.mean(selected_dataSeries[i:i+window,:],axis=0)
        averaged_dataSeries.append(average)

    print(type(averaged_dataSeries))

    for i in range(len(averaged_dataSeries)):
        condTG = eit.solve(averaged_dataSeries[i], dataRef, normalize=False)
        condNTG = sim2pts(pts, tri, np.real(condTG))
        solved.append(condNTG)
    solved = np.array(solved)

    print(solved.shape)
    end = time.time()
    print("computation:", end-start)

    fig = plt.figure()
    plt.jet()

    ax3 = fig.add_subplot(1, 1, 1)

    if vminmax is None:
        im3 = ax3.tripcolor(x, y, tri, np.real(solved[0]), shading='gouraud')
    else:
        im3 = ax3.tripcolor(x, y, tri, np.real(solved[0]), vmin=vminmax*-1, vmax=vminmax ,shading='gouraud')


    cb3 = plt.colorbar(im3, ax=ax3)
    ax3.set_aspect('equal')
    ax3.set_title('Reconstructed image')

    def init():
        im3.set_array([])
        return im3,


    def update_trip(i):
        solver = solved[i]
        solver = solver.ravel()
        im3.set_array(solver)
        return im3,


    anim = FuncAnimation(fig, update_trip, init_func=init, frames=range(len(averaged_dataSeries)), interval=100, repeat=False, blit=True)

    start = time.time()
    video_embed_str = anim.to_html5_video()
    end = time.time()

    video_embed_str = (video_embed_str.replace("\n", ""))
    starting_str = video_embed_str.find("src=\"")
    ending_str = video_embed_str.find("\"", starting_str + 5)
    video_embed_str = video_embed_str[starting_str:ending_str + 1]
    video_embed_str = video_embed_str[5:len(video_embed_str)-1]
    print("time render:", end-start)
    print("return")

    return video_embed_str

relative_inputs = [Input(component_id='relative-update',component_property='n_clicks')]
relative_states = [ State(component_id='select-geometry',component_property='value'),
                    State(component_id='number-electrodes',component_property='value'),
                    State(component_id='relative-num-frames', component_property='value'),
                    State(component_id='relative-range-slider',component_property='value'),
                    State(component_id='vminmax', component_property='value'),
                    State(component_id='relative-lambda',component_property='value')]
@app.callback(
    Output("relative-video","src"),
    relative_inputs,
    relative_states)
def relative_image_callback(*args):
    # gather input and states into one dictionary and named by component_id
    input_names = [item.component_id for item in relative_inputs + relative_states]
    args_dict = dict(zip(input_names, args))

    if args_dict["relative-update"] is not None:
        errorstring = ValidateRelativeInputs(args_dict)
        if errorstring is None:
            video_embed_str = createRelativeImage(args_dict)
            print(video_embed_str)
            return video_embed_str
        else:
            return ""




def visualizeRawData():
    fig = plt.figure()
    plt.jet()
    ax3 = fig.add_subplot(1, 1, 1)
    initial = np.reshape(dataSeries[0], (16, 13))
    im3 = ax3.imshow(initial, cmap='jet', interpolation='nearest')
    cb3 = plt.colorbar(im3, ax=ax3)

    def init():
        im3.set_data(initial)
        return im3,

    def update_trip(i):
        print(i)
        current = np.reshape(dataSeries[i], (16, 13))
        im3.set_data(current)
        return im3,

    anim = FuncAnimation(fig, update_trip, frames=300, init_func=init, interval=100, repeat=False, blit=True)
    video_embed_str = anim.to_html5_video()
    video_embed_str = (video_embed_str.replace("\n", ""))
    starting_str = video_embed_str.find("src=\"")
    ending_str = video_embed_str.find("\"", starting_str + 5)
    video_embed_str = video_embed_str[starting_str:ending_str+1]
    video_embed_str = video_embed_str[5:len(video_embed_str)-1]
    return video_embed_str


raw_data_inputs = [Input(component_id='raw-show',component_property='n_clicks')]
raw_data_states = []
@app.callback(
    Output(component_id="raw-video",component_property='src'),
    raw_data_inputs
)
def raw_image_callback(n_clicks):
    if n_clicks is not None:
        video_src = visualizeRawData()
        return video_src





@app.callback(
    [Output('upload-data-series','children'),
     Output('upload-data-series','style'),
     Output('absolute-starting-frame-slider','children'),
     Output('relative-range-slider-div','children')],
    [Input('upload-data-series', 'contents')],
    [State('upload-data-series', 'filename')]
)
def upload_data_series_callback(contents,filename):
    def CreateCurrentSlider(dataSeries):
        if dataSeries is not None:
            data_shape = dataSeries.shape
            maximum = data_shape[0]
            return dcc.Slider(
                min=0,
                max=maximum,
                step=1,
                value=0,
                id="absolute-slider",
                tooltip={"placement": "top"})
        else:
            return dcc.Slider(disabled=True)

    def CreateRangeSlider(dataSeries):
        if dataSeries is not None:
            data_shape = dataSeries.shape
            maximum = data_shape[0]
            return dcc.RangeSlider(
                min=0,
                max=maximum,
                step=1,
                id="relative-range-slider",
                value=[0,maximum],
                tooltip={"placement": "top"}
            )
        else:
            return dcc.RangeSlider(disabled=True)

    global dataSeries
    if filename is not None:
        dataSeries = parse_npy_file(contents,filename)
        try:
            dataSeries = np.reshape(dataSeries,(-1,208))
            text, style = UploadStyleUpdate(dataSeries)
            slider = CreateCurrentSlider(dataSeries)
            rangeSlider = CreateRangeSlider(dataSeries)
            return text, style, slider, rangeSlider

        except Exception as e:
            dataSeries = None
            text, style = UploadStyleUpdate(dataSeries)
            slider = CreateCurrentSlider(dataSeries)
            rangeSlider = CreateRangeSlider(dataSeries)
            return text,style,slider,rangeSlider


    if dataSeries is not None:
        text,style = UploadStyleUpdate(dataSeries)
        slider = CreateCurrentSlider(dataSeries)
        rangeSlider= CreateRangeSlider(dataSeries)
        return text,style,slider,rangeSlider



@app.callback(
    [Output('upload-reference-data','children'),
     Output('upload-reference-data','style')],
    [Input('upload-reference-data', 'contents')],
    [State('upload-reference-data', 'filename')]
)
def upload_data_reference_callback(contents,filename):
    global dataRef
    if filename is not None:
        dataRef = parse_npy_file(contents,filename)
        # Not valid reference file
        if (dataRef is None or len(dataRef) > 208):
            dataRef = None
            return UploadStyleUpdate(dataRef)
        else:
            return UploadStyleUpdate(dataRef)

    if dataRef is not None:
        return UploadStyleUpdate(dataRef)


@app.callback(
    [Output('prior-info-relative','children'),
     Output('prior-info-relative','style')],
    [Input('prior-info-relative', 'contents')],
    [State('prior-info-relative', 'filename')]
)
def upload_prior_info_relative_callback(contents,filename):
    if filename is not None:
        priorInfoRelative = parse_npy_file(contents,filename)
        return UploadStyleUpdate(priorInfoRelative)


@app.callback(
    [Output('prior-info-absolute','children'),
     Output('prior-info-absolute','style')],
    [Input('prior-info-absolute', 'contents')],
    [State('prior-info-absolute', 'filename')]
)
def upload_prior_info_absolute_callback(contents,filename):
    if filename is not None:
        priorInfoAbsolute = parse_npy_file(contents,filename)
        return UploadStyleUpdate(priorInfoAbsolute)



# This callback is called to show ROI and triggered by the Show ROI button
@app.callback(
    [Output(component_id='show-roi-modal', component_property='is_open'),
     Output(component_id='show-roi-modal', component_property='children')],
    [Input(component_id='show-roi', component_property='n_clicks')],
    [State(component_id='number-electrodes',component_property='value'),
     State(component_id='select-geometry',component_property='value'),
     State(component_id='relative-num-frames',component_property='value')]
)
def ShowROI(n_clicks, electrodes, geometry, window):
    def SetROIs(mesh, type='quadrants', constraint=True):
        pts = mesh['node']
        x = pts[:, 0]
        y = pts[:, 1]

        if type == 'quadrants':
            ROILU_TF = (x < 0) & (y > 0) & constraint
            ROIRU_TF = (x > 0) & (y > 0) & constraint

            ROILD_TF = (x < 0) & (y < 0) & constraint
            ROIRD_TF = (x > 0) & (y < 0) & constraint

            ROI_TF = [ROILU_TF, ROIRU_TF, ROILD_TF , ROIRD_TF]
        else:
            print('function does not support this type')

        ROI_idx = []
        for idx in range(len(ROI_TF)):
            appends = np.where(ROI_TF[idx])
            appended = appends[0]
            ROI_idx.append(appended)

        return ROI_TF

    def CreateROIGraph():
        num_eit = electrodes
        curve = getShape(geometry)
        mesh_obj, el_pos = create(num_eit,curve=curve)
        ROI = SetROIs(mesh_obj, type='quadrants')

        global solved
        quadrants = []
        for index_array in ROI:
            temp = solved[:, index_array]
            temp2 = temp.mean(axis=1)
            quadrants.append(temp2)

        moving = []
        for quads in quadrants:
            moving.append(movingAve(quads, window))

        fig = make_subplots(rows=2, cols=2)
        fig.append_trace(go.Scatter(
            x=np.arange(len(moving[0])),
            y=moving[0],
            name="Upper Left"
        ), row=1, col=1)
        fig.update_yaxes(nticks=10)
        fig.update_yaxes(automargin=True)


        fig.append_trace(go.Scatter(
            x=np.arange(len(moving[1])),
            y=moving[1],
            name="Upper Right"
        ), row=1, col=2)
        fig.update_yaxes(nticks=10)
        fig.update_yaxes(automargin=True)


        fig.append_trace(go.Scatter(
            x=np.arange(len(moving[2])),
            y=moving[2],
            name="Down Left"
        ), row=2, col=1)
        fig.update_yaxes(nticks=10)
        fig.update_yaxes(automargin=True)

        fig.append_trace(go.Scatter(
            x=np.arange(len(moving[3])),
            y=moving[3],
            name="Down Right"
        ), row=2, col=2)
        fig.update_yaxes(nticks=10)
        fig.update_yaxes(automargin=True)



        fig.update_layout(height=500, width=1000, title_text="Quadrants ROI")
        graph_object = dcc.Graph(figure=fig)
        return dbc.ModalBody(children=[graph_object])

    if n_clicks is not None:
        return True, CreateROIGraph()


# Display convergence graph callback, triggered by Show convergence button
@app.callback(
    [Output(component_id='convergence-modal', component_property='is_open'),
    Output(component_id='convergence-modal', component_property='children')],
    [Input('absolute-convergence',component_property='n_clicks')],
)
def ShowConvergence(n_clicks):
    def CreateConvergenceGraph():
        global convergence_list
        x = np.arange(len(convergence_list))
        fig = go.Figure(data=[go.Scatter(x=x, y=convergence_list)])
        fig.update_layout(
            title="Convergence graph",
            xaxis_title="Iterations",
            yaxis_title="Difference")
        graph_object = dcc.Graph(figure=fig)
        return dbc.ModalBody(children=[graph_object])
    if n_clicks is not None:
        return True, CreateConvergenceGraph()



# Callback used to control what to be displayed in the visualization tabs
@app.callback(
    Output(component_id='visual-content', component_property='children'),
    [Input(component_id='visual-checklist',component_property='value')]
)
def VisualControlsCallback(visual_array):
    def generateVisuals(visual_array):
        children = []
        # add  children
        for display_item in visual_array:
            if display_item == 'absolute':
                new_child = dbc.Col(visual_absolute,width="auto",id="absolute")
            if display_item == 'relative':
                new_child = dbc.Col(visual_relative, width="auto",id="relative")
            if display_item == 'raw':
                new_child = dbc.Col(visual_raw_data, width="auto", id="raw")


            children.append(new_child)

        return children
    children = generateVisuals(visual_array)
    return children



def serve_layout():
    session_id = str(uuid.uuid4())
    print(session_id)
    return html.Div([
    navbar , tabs, html.Div(session_id,id='session-id',style={'display':'none'})], id="main-div")

app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(threaded=True)