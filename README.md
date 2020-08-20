# EIT Dashboard

This web application is made by using the Dash web framework from Plotly.

The full documentation can be found in https://dash.plotly.com/ .

# Project Structure

* **/assets** - This is a directory to hold assets for the application. You can find CSS file here to change the design of the application. 


* **app.py** -  This is the script to create the Dash server (It is using Flask server underneath). The script also contains the registration of callback functions. The callback functions are triggered when a user interact with the UI. 


* **/Components** - This is a directory to contain the Dash UI components. You can find the components such as Card, Button, Input, Upload, Modal, etc, which corresponds to the UI. You can add/remove components here. 

* **requirements.txt** - A pip freeze of the environment i am running on.



## Components Folder 

There are currently separate files in the folder to hold components with different purposes (different tabs). There is one file to store the components inside the **settings** tab, another to store the components of the **visuals** tab. One file to store the tabs components and importing the other two files together. 

# Running the application

Install dependencies

`pip install -r requirements.txt`

Run application locally

`python app.py`

The application will be served in http://127.0.0.1:8050/

# Registering Callbacks

For more information on registering callbacks please visit: https://dash.plotly.com/basic-callbacks .

Here is a snippet of one of the callback function I wrote to call a function to compute an absolute image. In order to make a callback we used the @app.callback decorator on top of the function. In this case I am making the function called *absolute_image_callback* as the callback function. 

```python
@app.callback(
    [Output(component_id='visual-modal', component_property='is_open'),
     Output(component_id='visual-modal', component_property='children'),
     Output(component_id='absoluteimage', component_property='src'),
     Output(component_id='update-button-absolute-container',component_property='children')],
    absolute_inputs,
    absolute_states
)
def absolute_image_callback(*args):
    #some code

```

A callback decorator takes in 3 parameters. A list of Output, Input, and State (optional). These are classes imported from *dash.dependencies*. 

All the 3 classes requires **component_id** and **component_property** attributes to be defined. 

The **component_id** references to a UI component that has been defined in one of the components inside **/Components**. When creating a UI component there is usually the **id** field you can define yourself and **component_id**  is referring to this **id**.

The **component_property** is referencing to the UI component property (one referenced by **component_id**) that you would like to get / update. The **component_property** could be *style, children, value, src* or other common HTML properties. 


Instead of placing all inputs and state as parameters in the callback decorator. I placed them inside a list first and then passing them as argument later. This is to prevent from bloating the app.callback() decorator. 

```python

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


```

### Input 

We see here that the Input class is defined having the **component_id='absolute-update'** & **component_property='n_clicks'**. This actually corresponds to a button component defined inside /Components folder. So that now everytime the button in the UI is clicked, the callback function will be called. We then get the **component_property** of *n_clicks* as a parameter inside the callback function. 

### State

The state here is similar to Input , except that the callback function wont be triggered when any of these States are changed. The State is only used to keep hold of the value we want to track until the Input is triggered. When the Input is triggered then we will run the callback and we will be able to get the State of the components as argument too. 

### Output

Finally the Output is used to define the changes that this callback will have on the UI. The callback function must return a data type / structure corresponding to the Output component_property. The number of things to return in the callback function  is equal to the number of Outputs defined for this callback. 

In this example one of the Output is **Output(component_id='absoluteimage', component_property='src')** , which is an Img component and so the return for this Output is a string to correspond to the **src** property.

### Callback function's *args

We see from the example that the function *absolute_image_callback* takes in an *args argument. This is actually going to be values from component_property that we initially put from Inputs and States. Without the *args argument we could also get the Input and State like : 

```python
def absolute_image_callback(n_clicks,geometry,electrodes, num_frames, max_iters, lambda, #and so on.. ):
```

I used the args argument because as we use more States the function parameters become really long, which makes it harder to read. 
I then use the args argument and put all the argument into a dictionary where so that we can easily access the parameters by a  key. The key is the **component_id** of the Inputs and States, the value is their **component_property**.

### Storing parameters into dictionary

```python
# gather input and states into one dictionary and named by component_id

    input_names = [item.component_id for item in absolute_inputs + absolute_states]
    args_dict = dict(zip(input_names, args))

```


### Full Code Snippet 

```python

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
    # call function to plot absolute image passing in *args
```


# Next Steps / Improvements to be made

## Multi User Sessions

Because currently the application is running locally, the usage of global variables will not be a problem. But when you host this and multiple users are using the web application, then if a user access a global variable this will cause the change of state of the other users. 

**IMPORTANT** : *Current version is still using global variables so it is not well suited for multi users. Must take into consideration of the global variables or else application will break. *

For this not to happen we need to separately identify memory with session-ids. Only a person with the correct session-id can access his part of memory. 

This may give a start on how to implement : https://dash.plotly.com/sharing-data-between-callbacks . But I could not find anything that might be very relevant for our need.  There are some recommendation with using Redis but I am not familiar yet. 



## Integration with Google Cloud

This is a sketch draft of what might work. I have not truly implemented this because I did not have enough time. But try to see if this design might work or not. 




I got inspiration from : https://github.com/WileyIntelligentSolutions/wiley-dash-boilerplate2 . This example he used Celery to run long background processes locally.


# References

* Dash Bootstrap Components - https://dash-bootstrap-components.opensource.faculty.ai/docs/

* Dash Core Components - https://dash.plotly.com/dash-core-components

* Dash Callbacks - https://dash.plotly.com/basic-callbacks

* Sharing data between callbacks - https://dash.plotly.com/sharing-data-between-callbacks

* [Running Heavy Process in Background Discussion](https://community.plotly.com/t/running-calculation-heavy-process-in-background/17400/5)

