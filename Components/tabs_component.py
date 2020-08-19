from .setting_components import *
from .visual_components import *

navbar = dbc.NavbarSimple(
    brand="EIT Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

tabs = dbc.Tabs(children=[
        dbc.Tab(settings_tab, label="Settings", tab_id='Settings'),
        dbc.Tab(visual_tab, label="Visualize", tab_id="Visualize"),
    ], className="m-3",id="select-tab"
)
