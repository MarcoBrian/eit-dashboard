# third-party lib imports
from flask import Flask, request
from firebase_admin import auth
import time
import os
import json
import numpy as np
from google.cloud import tasks_v2

# Imports the Cloud Logging client library
import google.cloud.logging
import logging


# custom imports
from pyeit.mesh.meshpy.build import create
from pyeit.eit.utils import eit_scan_lines
import pyeit.eit.jac as jac
from pyeit.eit.interp2d import *
import firestore_db


# init
app = Flask(__name__)

# Create a cloud task client.
cloud_tasks_client = tasks_v2.CloudTasksClient()

# Instantiates a client
log_client = google.cloud.logging.Client()
# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
log_client.get_default_handler()
log_client.setup_logging()


# restore data and timestamp from firestore
def restore_data(lung_docs):
    data = []
    ts = []
    ref =[]
    order = []
    map_for_orders = {}
    data_object_collections = []
    for doc in lung_docs:
        data_object_collections.append(doc.to_dict())

    for items in data_object_collections:
        order.append(items["order"])

    for i in range(len(order)):
        map_for_orders[order[i]] = i

    for index in range(len(order)):
        correct_index = map_for_orders[index]
        object = data_object_collections[correct_index]
        if index == 0:
            ref = object["ref"]
        data_object = object["data"]
        for raw_time in data_object:
            data.append(raw_time["raw"])
            ts.append(raw_time["time"])

    data = np.array(data)
    ts = np.array(ts)
    end = time.time()
    return data, ts, ref

# Calculate absolute image
def AbsoluteImagePhantom(data_series,ts,dataRef):
    logging.info("Entering computation")
    start = time.time()
    data_mean = np.mean(data_series, axis=0)
    SNR = 20 * np.log10(np.abs(np.mean(data_series, axis=0)) / np.std(data_series, axis=0))
    '''Setup for inverse problem'''
    num_eit = 16
    mesh_obj, el_pos = create(num_eit)
    pts = mesh_obj['node']
    tri = mesh_obj['element']
    # EIT setup: adjacent mode
    el_dist , step = 1 , 1
    ex_mat = eit_scan_lines(num_eit, el_dist)
    # mesh
    x = pts[:, 0]
    y = pts[:, 1]
    # setup JAC solver
    eit = jac.JAC(mesh_obj, el_pos, ex_mat, step, perm=1.0, parser='fmmu')

    '''Reconstruct a static image'''
    eit.setup(p=0.25, lamb=1.0, method='lm')
    # Absolute data 1
    ds1 = eit.gn(data_mean, lamb_decay=0.1, lamb_min=1e-5, maxiter=40, verbose=True)
    dsn1 = sim2pts(pts, tri, np.real(ds1))
    ds1 = ds1.tolist()
    dsn1 = dsn1.tolist()
    end = time.time()
    total_time = end - start
    logging.info("Finished computation")
    logging.info(f'total time taken for computation: {total_time}')
    return ds1, dsn1



# Task will send request to this endpoint
@app.route('/computeimage', methods=['POST'])
def computeImage():

    # verify that this is from Cloud Task. These headers are set internally so we can always be confident
    # that these headers are legit. External headers are replaced by Gcloud.

    try:
        queue_name = request.headers['X-AppEngine-QueueName']
    except Exception as e:
        response = "This URL is only accessible through Cloud Tasks"
        logging.error(response)
        return (response)

    req_body = request.get_data(as_text=True)
    req_body = json.loads(req_body)

    try:
        patient_id = req_body["patient_id"]
    except Exception as e:
        logging.error("Error while reading request body, invalid body")
        response = "Invalid syntax"
        status = 400
        return (response, status)
    try:
        session_id = req_body["session_id"]
    except Exception as e:
        logging.error("Error while reading request body, invalid body")
        response = "Invalid syntax"
        status = 400
        return (response, status)

    # verify if data has been computed or not (check if record exists)
    try:
        doc = firestore_db.get_mesh_data(patient_id, session_id)
    except Exception as e:
        logging.warning(str(e))
        response = "An error has occured when fetching data"
        status = 500
        return (response , status)

    query__res_length = len(list(doc))
    if query__res_length > 0 :
        logging.info("This patient's session has been calculated before.")
        # the following data has been computed so shouldn't be computed again
        response = "The following action is not performed by the server. This is not an error, nothing bad occured." \
                   "The action was decided for efficiency."
        return (response)
    else:
        try:
            lung_docs = firestore_db.get_lung_docs(patient_id,session_id)
        except Exception as e:
            logging.error("Error while fetching data from firestore")
            response = "An error has occurred"
            status = 500
            return (response , status)

        data_series, ts, data_ref = restore_data(lung_docs)

        try:
            ds1, dsn1 = AbsoluteImagePhantom(data_series, ts, data_ref)
        except Exception as e:
            logging.error("Error while computing absolute image")
            response = "An error has occurred"
            status = 500
            return (response , status)

        try:
            firestore_db.write_new_mesh_data(patient_id, session_id, ds1, dsn1)
        except Exception as e:
            logging.error("Error while writing data to firestore.")
            response = "An error has occurred"
            status = 500
            return (response , status)

        response = "Data has been successfully computed and stored in database"
        return (response)



# Create compute task here
@app.route('/createtask', methods=['POST'])
def createtask():

    # request body requires firebase id_token, patient_id , session_id.
    # id_token is created by firebase auth (if we use it)
    # {
    #   "id_token":
    #   "patient_id" :
    #   "session_id" :
    # }

    # verify authentication of client
    req_body = request.json
    id_token = req_body["id_token"]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
    except Exception as e:
        logging.error("User is unauthenticated. Could not verify token signature")
        response = "User is unauthenticated. Could not verify token signature."
        status = 401
        return (response, status)

    # verify message format
    try:
        patient_id = req_body["patient_id"]
    except Exception as e:
        logging.error("Error while reading request body, invalid body. Missing fields.")
        response = "Invalid syntax"
        status = 400
        return (response, status)
    try:
        session_id = req_body["session_id"]
    except Exception as e:
        logging.error("Error while reading request body, invalid body. Missing fields.")
        response = "Invalid syntax"
        status = 400
        return (response, status)

    # create task to Cloud task queue

    project = os.environ.get('PROJECT_ID')
    server_location = os.environ.get('SERVER_REGION')
    queue_name = os.environ.get('COMPUTE_IMAGE_QUEUE')

    logging.info("Creating image computation task")
    parent = cloud_tasks_client.queue_path(project, server_location, queue_name)
    task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/computeimage'
        }
    }
    payload_object = {}
    payload_object["patient_id"] = patient_id
    payload_object["session_id"] = session_id

    try:
        # The API expects a payload of type bytes.
        payload = json.dumps(payload_object).encode()
    except Exception as e:
        response = e.message
        status = 500
        return (response, status)

    if payload is not None:
        # Add the payload to the request.
        task['app_engine_http_request']['body'] = payload

    try:
        # Use the client to build and send the task.
        response = cloud_tasks_client.create_task(parent, task)
    except Exception as e:
        logging.error("Error while creating compute image task")
        response = str(e)
        status = 504
        return (response , status)

    logging.info("Task creation successful")
    return "Success in creating task"


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)