# GCP Sample Code

This was some code that i have written when setting up firestore and google app engine. But this code has not been integrated with the new Dash application. Also will have to set up in Gense GCP account. 

# app.yaml 

This is a server configuration file for deployment of the application in Google App Engine. 

# server.py

This is a Flask application that has two routes. Simply only /createtask and /computeimage. 

The function of the **/createtask** endpoint so that an **authenticated** user may be able to create a computation task. If a task is created succesfully it will be pushed to a Cloud Task Queue (This have to be set up in GCP console). 

*In the case for the Dash application, i think the **/create** task won't be necessary because we can directly create the tasks right from the Dash application.* 

The **/computeimage** endpoint only accepts requests from Cloud Task Queues. So once it receive a Cloud Task from the queue. It will compute the image. How it will get the data is described by the Task it receives. The Task will contain the session id and user id, so now we know which of the data to be fetched from Firestore. After the finished computation store the results in Firestore so that it may be fetched from the Client side / Dash application. 

# firestore_db.py

Contains function that perform database access. Write + Read functions. 

# EIT_entry.py

Sample code for inserting EIT data to firebase.

