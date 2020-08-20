import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np
import datetime

# define class for patient
class Patient(object):
    def __init__(self,name):
        self.name = name
        self.sessions = []

    def to_dict(self):
        dict_version = {}
        dict_version["patient_name"] = self.name
        dict_version["sessions"] = self.sessions
        return dict_version

# define class for a patient's session
class Session(object):
    def __init__(self,start_time,end_time):
        self.start = start_time
        self.end = end_time

    def to_dict(self):
        dict_version = {}
        dict_version["start"] = self.start
        dict_version["end"] = self.end
        return dict_version

# define class for data point
class EIT_Data(object):
    def __init__(self, data,session_id,order,ref=None):
        self.data = data
        self.session_id = session_id
        self.order = order
        self.ref = ref
    def to_dict(self):
        dict_version = {}
        dict_version["data"] = self.data
        dict_version["session_id"] = self.session_id
        dict_version["order"] = self.order
        if self.ref != None:
            dict_version["ref"] = self.ref
        return dict_version

# Class used to store database reference information and perform database related methods
class DB_reference(object):
    def __init__(self):
        # Use a service account
        cred = credentials.Certificate('gense-1ab7f-firebase-adminsdk-vt5oe-6544c1b7d3.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.patients_ref = self.db.collection(u'patients')
        self.batch = None

    # this is used for making batch writes
    def InitializeNewBatch(self):
        self.batch = self.db.batch()

    def CreateNewPatient(self, name):
        new_patient = Patient(name)
        self.patients_ref.add(new_patient.to_dict())

    def CreateNewSessionForPatient(self,patient_id, session_object,batch_flag=False):
        patient_document = self.patients_ref.document(patient_id)
        document_reference = patient_document.collection('sessions').document()
        session_id = document_reference.id
        session_dict = session_object.to_dict()

        if (batch_flag == False):
            document_reference.set(session_dict)
            # update sessions array inside patient document
            patient_document.update({u'sessions' : firestore.ArrayUnion([{"session_id" : session_id , "start" : session_dict["start"]}])})
        else:
            self.batch.set(document_reference,session_dict)
            self.batch.update(patient_document,{u'sessions': firestore.ArrayUnion([{"session_id" : session_id , "start" : session_dict["start"]}])})
        return session_id

    # Get patient document id from name
    def GetPatientIdFromName(self,name):
        result = self.patients_ref.where("patient_name","==",name).stream()
        for doc in result:
            return doc.id

    # Insert EIT data to the collection
    def Insert_EITData(self, patient_doc_id , session_id, EIT_data_instance, batch_flag=False):
        new_entry = EIT_data_instance.to_dict()
        reference = self.patients_ref.document(patient_doc_id).collection(u'sessions').document(session_id).collection('lungs').document()
        if batch_flag == False:
            reference.set(new_entry)
        else:
            if self.batch != None:
                self.batch.set(reference, new_entry)

            else:
                print("batch object is undefined")

    # used to upload the array of data for patient in a particular session  (default batch write)
    def UploadObjectArray(self, object_array, ref, patient_id, session_id, order):
        if order == 0: # first grouping include reference array
            EIT = EIT_Data(object_array,session_id, order,ref)
        else:
            EIT = EIT_Data(object_array,session_id, order)

        self.Insert_EITData(patient_id, session_id, EIT, batch_flag=True)

    # methods for querying
    def get_patient_by_name(self,name):
        result = self.patients_ref.where("patient_name","==",name).stream()
        return result

    # create session with data
    def CreateNewSessionWithData(self,patient_id,new_session,object_array_collection,ref):
        self.InitializeNewBatch()
        session_id = self.CreateNewSessionForPatient(patient_id,new_session)
        for k in range(len(object_array_collection)):
            self.UploadObjectArray(object_array_collection[k], ref, patient_id, session_id, k)
        self.batch.commit()




# Helper functions
"""
load_data will return
[[{raw:"",time:""}, ..] ,[{raw:"",time:""}] ]
a 2D array where each row is a collection of objects of data. 
Each 1D array will contain data points to around 500 frames 
"""
def load_data(ts_path, data_path):
    ts = np.load(ts_path)
    data = np.load(data_path)
    length = len(ts)
    data = data.tolist()
    ts = ts.tolist()
    object_array = []
    object_array_collection = []
    image_count = 200
    count = 0
    for i in range(length):
        object = {"raw" : data[i], "time": ts[i]}
        object_array.append(object)
        count += 1
        if count == image_count:
            count = 0
            object_array_collection.append(object_array)
            object_array = []
    object_array_collection.append(object_array)
    return object_array_collection


# driver code
if __name__ == "__main__":
    # loading data
    object_array_collection = load_data('William_strectch2020_06_08_13_11_46_ts.npy',
                                  'William_strectch2020_06_08_13_11_46.npy')
    ref = np.load('William_strectch2020_06_08_13_11_46_ref.npy')
    ref = ref.tolist()

    # create database instance
    db_instance = DB_reference()

    # create new patient
    db_instance.CreateNewPatient("mario")

    # # create session for new patient
    patient_id = db_instance.GetPatientIdFromName("mario")
    new_session = Session(datetime.datetime(2020, 6, 25), datetime.datetime(2020, 6, 28))

    # Uploading data but not a batch write
    # session_id = db_instance.CreateNewSessionForPatient(patient_id, new_session)
    # # initialize a new batch write to upload the data
    # db_instance.batch = db_instance.db.batch()
    # for k in range(len(object_array_collection)):
    #     db_instance.UploadObjectArray(object_array_collection[k],ref, patient_id,session_id,k)
    # # commit the batch write
    # db_instance.batch.commit()

    # Create session as a batch write
    db_instance.CreateNewSessionWithData(patient_id,new_session,object_array_collection,ref)




