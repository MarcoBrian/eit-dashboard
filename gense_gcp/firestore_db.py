import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


firebase_admin.initialize_app()
db = firestore.client()

def get_lung_docs(patient_id,session_id):
    return db.collection('patients'). \
        document(patient_id). \
        collection('sessions').document(session_id). \
        collection('lungs'). \
        where("session_id", "==", session_id).stream()

def get_mesh_data(patient_id,session_id):
    return db.collection('mesh').where("patient_id","==",patient_id).where("session_id","==",session_id).stream()

def write_new_mesh_data(patient_id,session_id,ds1,dsn1):
    new_record = {}
    new_record["patient_id"] = patient_id
    new_record["session_id"] = session_id
    new_record["ds1"] = ds1
    new_record["dsn1"] = dsn1
    db.collection('mesh').add(new_record)
    return
