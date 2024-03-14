# Data Engineer Miniproject
## 👋 Introduction
Welcome to the coding assignment page for the Data Engineering role at TfH for the Worldcoin project!

This coding assigment consists of a few tasks revolving around data loading, analysis and processing.

You will find information on how to submit your solutions below the task descriptions. Your submission should be able to stand on its own for our reviewing process. Please make sure that you submit all details you deem necessary to understand your approach, and all code (incl. instructions) to run your coding solution.

Review of your submission will also focus on the quality of code and documentation next to inspection of approach and outcomes. The time between sending you this project page and you submitting your results will not be part of the review process. We will however ask you about the time spent on the project as part of the post-review discussion panel.

You are free to make reasonable assumptions when working on the project to move forward and overcome any missing pieces of information.

## 🧑‍💻 Task description
This coding assignment presents you with some example data that is relevant for the task of face detection. You will not be provided with any actual image data, instead you will work only on the image metadata and bounding box information as it would be stored in a MongoDB instance collecting all information for this hypothetical face detection system.

## 🖼️ Primer on bounding boxes
### Specification
The core data structure in this assignment is a bounding box for user's faces in images. A bounding box is simply a rectangle that is drawn around a person's face in an image.

The specification of a bounding box in our case can come in two variants that fully and uniquely specify the rectangle:

1. Corners: Specifying the *top left* and *bottom right* corner of the rectangle.
2. Center & dimensions: Specifying the *centroid* alongside *width* and *height* of the rectangle.

You will find both these variants in the presented data.

### Coordinates
The coordinates used to specify the bounding boxes is present in *fractional coordinates* in the presented data.

Fractional coordinates are declaring a coordinate point in the range `[0, 1]` with respect to the image dimensions. E.g. a coordinate of `[0.5, 0.5]` would be the center of any image, irrespective of it's size or aspect ratio. The top left corner of an image is `[0.0, 0.0]`, the bottom right corner is `[1.0, 1.0]`.

The `x` coordinate in our system specifies the horizontal position, while y specifies the vertical position.

## 💽 Data
The data you will be working with is simulating a small amount of data as it might show up in a system for face detection. This specific system is designed to process incoming image data with machine-learning model for face detection, and pass results on to human audit & annotation teams. The end-goal is a dataset of face bounding boxes that can be used for training a face detection model.

Consider this high-level diagram to give you a mental model for the data flow and relationships between database collections that will be introduced:

[img]

- The bottom row in the diagram shows four MongoDB collections that will be introduced in more detail below. The basic flow of data is as follows:
- The metadata collection gets populated with image metadta documents at the moment where a new image is placed into the s3 bucket acting as raw image data storage.
- Over time all the available images will be ingested by the bbox_model kubernetes pod that runs the current bounding box model on the images. The model outputs get stored in the bbox.model collection.
- Over time all the stored bounding box model predictions will be audited by humans and the results of these audits will be stored in the bbox.audit colletion.
- All images that have an audit document indicating bbox_correct: false will over time be annotated by humans with a new set of bounding boxes, which are stored in the bbox.annotation collection.
- The totality of bounding box data available between the bbox.model and bbox.annotation collections will be used for the creation of a final dataset for training a bounding box model.

Here are additional details for each collection:

1. metadata
This collection holds only basic metadata for all images. It represents the entirety of all available images, i.e. any image that has been uploaded to the raw image storage location has a corresponding document in this collection. An example document for this collection is:

```js
{
    "image_id": "000ab0dfc1f4ba6f6531b908e4b7d71e",
    "capture_timestamp": 1704063601
}
```

- image_id is the unique identifier for each image.
- capture_timestamp is the unix timestamp for when the image was captured.

2. bbox.model
This collection contains outputs of an existing face detection model that is continuously running over the available image data and storing inference outputs. Not all images that are in the metadata collection will have corresponding model outputs, either due to processing delays or ingestion filters to the model processing step.

The model will return a bounding box for all faces it was able to detect in a given image. These bounding boxes are stored in an array inside the document.

You will find output documents for two different model versions in the data. Models of different versions will generally predict different sets of bounding boxes for the same image.

Example documents for this collection that shows two model versions predicting for the same image are:

```js
[
  {
    "image_id": "0b86e8fd3a5e91ec98078f95cd1da21b",
    "bboxes": [
      {"top": 0.051, "bottom": 0.382, "left": 0.388, "right": 0.564},
      {"top": 0.358, "bottom": 0.768, "left": 0.476, "right": 0.568}
    ],
    "model_version": "1.0.0"
  },
  {
    "image_id": "0b86e8fd3a5e91ec98078f95cd1da21b",
    "bboxes": [
      {"center_x": 0.234, "center_y": 0.487, "width": 0.165, "height": 0.318},
      {"center_x": 0.577, "center_y": 0.534, "width": 0.114, "height": 0.406}
    ],
    "model_version": "2.0.0"
  }
]
```

- image_id is corresponding to the image metadata data already encountered in the metadata.
- bboxes holds the model's inference output. The format of this output can change based on on the version of the model that was used to run the prediction. Each entry in the list is the bounding box of a predicted face.
- model_version specifies which version of the bounding box model generated the document. An image can have been processed by multiple versions of the model and multiple documents for one image might therefore exist.

3. bbox.human_audit
These documents represent human audits of model predictions.

For some of the model predictions a human was tasked to verify the correctness of the model output. The audit documents will contain the result of this verification. The verification result can only be bbox_correct: true, indicating that the model prediction was correct, or bbox_correct: false, indicating that the model prediction was incorrect in some way.

An example document for this collection is:

```js
{
  "image_id": "31786d091d728861dd8312287d0e7ae1",
  "model_version": "1.0.0",
  "bbox_correct": true,
  "auditor": "idkufm28qd@tfh.com",
  "task_version": "1.0.0",
  "timestamp": 1695380870.4499085,
}
```

- image_id is again the unique identifier for the image.
- model_version specifies which version of the model prediction was audited. The tuple of (image_id, model_version) will uniquely identify which document in bbox_model contains the audited model output.
- bbox_correct is the result of the audit.
- auditor specifies which person from the annotation team performed the audit.
- task_version specifies which version of the audit task generated this document. The same bounding boxes might have been audited in different versions of the task. E.g. a new version of the task might get introduced if the definition what a correct bounding box is has changed.
- timestamp is the unix timestamp for when the audit was received.

4. bbox.human_annotation
This last collection contains human-drawn bounding box information.

A human annotator is tasked to annotate bounding boxes in an image if the bbox_human_audit result for a model predition was found to be incorrect. In such a case a human annotator will provide a corrected annotation.

The human bounding box annotation task will only ever result in one bounding box per annotation document. That means that an image might have multiple annotation documents if there are multiple faces visible in it.

An example for annotations where a single image contained more than one face is:

```js
[
  {
    "image_id": "4dc364f6038194b897e23721740f395a",
    "bbox": {"center_x": 0.407, "center_y": 0.455, "width": 0.199, "height": 0.374},
    "annotator": "wyenwqnmi4@tfh.com",
    "task_version": "2.0.0",
    "timestamp": 1706192047.0,
  },
  {
    "image_id": "4dc364f6038194b897e23721740f395a",
    "bbox": {"center_x": 0.482, "center_y": 0.392, "width": 0.04, "height": 0.61},
    "annotator": "idkufm28qd@tfh.com",
    "task_version": "2.0.0",
    "timestamp": 1705962121.0,
  }
]
```

image_id is the unique identifier for the image.
bbox is the annotation result for a single bounding box in the image. Multiple bounding boxes in an image means that there will be multiple documents with the same image_id.
annotator specifies which person from the annotation team performed the annotation.
task_version specifies which version of the annotation task generated this document. A difference between task versions might represent a change in the bounding box format or a change in the definition for how a bounding box should be annotated. Documents of different versions are incompatible.
timestamp is the unix timestamp for when the annotation was received.

## ✏️ Tasks
For this assignment you will be asked to perform the following tasks:

1. Setup:
Set up a local MongoDB instance and populate the database instance with the provided documents. (See section Resources to download the data)

2. Data monitoring:
After loading the data into the database consider the following scenario: > Our ML Engineers are interested in monitoring the current state of the available bounding box data in our database at all times. > The data they are interested in is the following: > > - Fraction of all available images that have been processed by the bounding box model. > - Fraction of images where model predictions have been audited as correct by a human. > - Fraction of images where incorrect model predictions have been corrected by a human annotation.

Implement a function that returns the requested information human-readable (i.e. formatted, visualized, etc.) for the ML Engineers.

3. Model failure inspection:
After loading the data into the database consider the following scenario: > An ML engineer working on the bounding box model is interested to dig into cases where the bounding box model was failing to accurately predict a bounding box. > They ask you to provide them with functionality where they can query for a given image_id and get the bounding box model prediction(s) alongside the correct human annotations back. > There should be a direct mapping between the bounding box predicted by the model and the re-annotated version of the human, with the difference of bounding box coordinates being provided.

To make this more graspable consider the following diagram visualizing bounding boxes predicted by a model on the left, alongside the human annotations on the right:

[img]

For this example your function should return documents like this that put each predicted bounding box in context to its human-corrected version. Complete mispredictions of the model resulting in human annotations with a different number of bounding boxes as predicted should be handled as well:

```js
{
  "image_id": "123abc",
  "predicted": {"top": 0.18, "left": 0.2, "bottom": 0.49, "right": 0.53},
  "annotated": {"top": 0.17, "left": 0.24, "bottom": 0.41, "right": 0.55},
  "delta": {"top": -0.01, "left": 0.04, "bottom": -0.08, "right": 0.02}
},
{
  "image_id": "123abc",
  "predicted": {"top": 0.16, "left": 0.47, "bottom": 0.34, "right": 0.57},
  "annotated": {"top": 0.2, "left": 0.56, "bottom": 0.37, "right": 0.71},
  "delta": {"top": 0.04, "left": 0.09, "bottom": 0.03, "right": 0.14}
},
{
  "image_id": "123abc",
  "predicted": {"top": 0.62, "left": 0.69, "bottom": 0.66, "right": 0.84},
  "annotated": null
  "delta": null
}
```

➡️ After implementing the functionality report the result of your function for the following image_id values as part of your submission:

```
4a25a2ab002137dac4fe3e09ba91c349
24982f38d2d732ef367638a175d72eae
88d081d7b18e1c5c9170dd4787c765db
dbb4dfe40a50640e59f928dc386c0fb2
```

4. Dataset creation:
After loading the data into the database, implement functionality that creates another database collection bbox_dataset that represents the final dataset for training a bounding box model.

Each document in the collection must contain the following:

image_id: Which image the dataset entry is for.
bboxes: All bounding boxes for the image.
The rule for priority of which bounding box source to use is:

Prioritize human bounding box annotations over model predictions.
Prioritize most recent bounding boxes.

So in a case where an image has the following bounding box sources:

- Model v1 (October 2023)
- Model v2 (January 2024)
- Human v1 (December 2023)
, the Human v1 (December 2023) one should be the one that ends up in the dataset.

## Resources

- [database_documents](../coding_submission_documents)

## Submission
For all the tasks we recommend creating a (private) Github repository to easily share your results. Please push all the necessary content (files, images, slides, etc) and code to that repository and invite the following users:

- tbszlg
- for-aiur
