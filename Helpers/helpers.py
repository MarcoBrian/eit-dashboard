from pyeit.mesh.meshpy import shape
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import numpy as np



def parse_npy_file(content,filename):
    try:
        content_type, content_string = content.split(',')
        data_buffer = base64.b64decode(content_string)
        if 'npy' in filename:
            data = np.frombuffer(data_buffer, dtype=np.float64)
            data = data[16:]
            return data
        else:
            raise Exception("Not numpy file")

    except Exception as e:
        print(e)
        return None


def getShape(geometry):
    if geometry == "throx":
        return shape.throx
    if geometry == "throx_anomaly":
        return shape.throx_anomaly
    if geometry == "disc":
        return shape.disc
    if geometry == "disc_anomaly":
        return shape.disc_anomaly
    if geometry == "anomaly_perm":
        return shape.anomaly_perm

def fig_to_uri(in_fig, close_all=True, **save_args):
    # type: (plt.Figure) -> str
    """
    Save a figure as a URI
    :param in_fig:
    :return:
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        in_fig.clf()
        plt.close('all')
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)

def movingAve(values, window):
    weights = np.repeat(1.0, window) / window
    smas = np.convolve(values, weights, 'valid')
    return smas