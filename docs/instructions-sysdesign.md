Data Engineer Miniproject
👋 Introduction
Welcome to the miniproject page for the Data Engineering role at TfH for the Worldcoin project!

This miniproject consists of a system design task that is closely related to the role we already presented you during the interview process.

You will find information on how to submit your solution below the task description. Your submission should be able to stand on its own for our reviewing process. Please make sure that you submit all details you deem necessary to understand your approach.

The time between sending you this project page and you submitting your results will not be part of the review process. We will however ask you about the time spent on the project as part of the post-review discussion panel.

You are free to make reasonable assumptions when working on the project to move forward and overcome any missing pieces of information.

🏗️ Task Description
The task is about creating a system design for a central data pipelining & dataset creation system for computer vision data in an existing infrastructure. The kind of data that this system deals with are face images of users for the purposes of face-recognition and fraud prevention.

ℹ️ Overview
The graphic below gives you a high-level overview of how this system should be integrated into a set of existing components.

0
Example data pipeline configuration from ML engineers
The drawn components that the data pipelining system will interact with are described below:

Data Sources The Orbs send raw image data into AWS s3 buckets, and any metadata regarding the images to a MongoDB. Given the sensitive nature our user-data there can never be any long-term copies of the image files anywhere outside of these s3 buckets. The MongoDB holds any non-image data and contains pointers to the raw image data for any document that pertains to an image. You can assume that the MongoDB has any database & collection setup that you see fit for this usecase. There is nothing specific that we dictate here.

Signal Producers By "signal" we are referring to any metadata, feature or human annotation data that can be added to the raw image data. This example infrastructure contains two sources of such additional signal:

i. ML Model Workers A set of ML models that continuously process any data they are configured to process. The signal they generate (model inference outputs) are stored in the MongoDB with pointer metadata as a reference to the original image. Assume that this system scales perfectly and the model output for any image is available immediately after the image has been ingested. ⚠️ From time to time the version of the models running as workers will update. This will also lead to changes in the signal and their formats that are generated. Example models ran as workers: Face detection model (face bounding-boxes and face keypoints), spoof detection model (binary classification), image quality assessment model (5 quality classes).

ii. Human Annotations A system to request human labels from an annotation team. The system allows any other component to request human labels using API calls and resulting labels are automatically stored back in the MongoDB with reference to the raw image. The annotation task system requires us to upload image data to a different storage location from which the annotation platform reads and displays them to the annotation user. ⚠️ Since we cannot have long-lived storage of raw image data anywhere outside our original s3 data buckets, these annotation images will be automatically deleted every 24 hours to ensure no data is stored there for long periods. This also means that any annotation request that was not resolved inside that timeframe will have to be re-generated in order to be presented to the annotation team. You can not assume that the size of our annotation team will scale proportional to the amount of requests. Example tasks for human annotation: Face bounding box annotation, Face keypoint annotation, Classification tasks (e.g. "Rate the perceived quality of this image on scale of 1-5").

Users The users in this scenario are ML engineers. They are the ones that want to define how the data ingestion, processing and eventual dataset creation is done. The idea is that they can use config files or simple python scripting/module implementations to specify how the data should be processed, they should not have to know about the inner workings of the processing system (with exception of some outside facing interfaces if necessary). Typical configurations will specify a mix of ML model-generated data and human audits or additional annotation work to flow into the resulting dataset(s). An example idea for what a configuration should allow developers to do is depicted by the flowchart below.

0
Example data pipeline configuration from ML engineers
Model training The training of ML models happens on a cluster of AWS EC2 GPU instances. Experiment tracking and model registry are taken care of by MLFlow. The training will use versioned datasets from the dataset registry to ensure experiment reproducibility and to assess impact of data filtering/processing changes on model performances. The datasets used during training are the specialized datasets of the dataset registry. The expected scenario here is that each model that gets trained will have one specialized and versioned dataset available for its training in the dataset registry. ⚠️ Some of the specialized datasets will share the same signals between them. For example, both the dataset for the face detection model and the dataset for the spoof detection model require face bounding boxes to be present in their dataset. Example model training: Face detection model, spoof detection model, image quality assessment model.

Dataset registry Based on the desired configuration a global dataset will be created by the dataset system. Initially this dataset should hold all the available information that is necessary to create all the required specialized datasets used in model training. Because it holds all information we call it the global dataset. All the specialized datasets are derived from this global dataset by applying filter and transformation operations on it, which are again defined by the ML practitioners that want to use these datasets for model training. The graphic below tries to schematically showcase what sort of specialized datasets might be required by the ML engineers.

0
Example data pipeline configuration from ML engineers
✏️️ Task
Your task is to come up with a system design proposal for the described data processing & dataset creation system.

The requirements on the system are:

Ingest data from the MongoDB in a configurable way by applying various filters defined by the ML engineers.
Allow for specification of data processing pipelines as defined by the ML engineers.
By sending annotation requests to our human annotation team.
By leveraging continuously generated ML model worker outputs.
Account for data provenance. If one of the sub-components of a processing pipeline changes, all downstream data might need to be re-generated if dependent.
Create "global" dataset from all available data that is required in subsequent specialized datasets.
Allow for specialized datasets to be created from global dataset by applying filters and transformations defined by the ML engineers.
Store datasets in versioned way in a dataset registry.
Aspects to consider for your design include:

Versioning and format changes of both model worker outputs and human annotations.
Challenges of including human annotations as intermediary steps in pipelines
Looping nature of pipeline designs (annotation -> audit -> annotation -> ...)
Challenges of having human annotation requests deleted periodically due to sensitive nature of data
Aspects you can safely ignore for your design include:

The system denoted as 'Worker System' in the diagram above. The details of ML model deployments and their continuous execution is not part of this task.
MlFlow or the ML training infrastructure. Continuous retraining or downstream utilization of the generated datasets is not part of this task.
The system denoted as 'Label Request System' in the diagram above. You can assume that there exists an API to fetch and submit annotations and their requests for this task.
One aspect to highlight is that the ML engineers will likely want to iterate often on the configurations of data ingestion, processing and dataset export given the iterative nature of the dataset <-> experiment workflow that this system enables. For example, if an engineer specifies a given dataset and runs a training afterwards they might come up with new ideas how the data needs to be filtered or processed to improve model performances. The minimization of iteration complexity and wait times should be optimized for.

The format of submission for this task is up to you. Long-form document, slides, video presentations are all fine for us. You should put the focus on clearly stating your design decisions and the reasoning behind them.

Submission
To submit your solution to the project you can send us links to documents, slides, videos, etc. per mail. If you want, you can also set up a private GitHub repo to store all relevant files and invite the following users:

tbszlg
for-aiur
