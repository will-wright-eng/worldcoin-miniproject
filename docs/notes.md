# notes

## setup

- download data

## planning

- objective: a few tasks revolving around data loading, analysis and processing
- motivation: tbd
- stakeholder: discussion panel
- boundary conditions:
  - submission should be able to stand on its own for our reviewing process
  - submit all details you deem necessary to understand your approach, and all code (incl. instructions) to run your coding solution
  - focus on the quality of code and documentation next to inspection of approach and outcomes

## data

*in order of appearance in process flow*

- metadata
- bbox.model
- bbox.audit (human_audit = audit)
- bbox.annotation (human_annotation = annotation)

## tasks

### setup

- mongodb
- populate db with provided data

### data monitoring (ie current state reporting)

- fraction of all available images that have been processed by bbox model (len(bbox.model) over len(metadata))
- fraction of images where model predictions have been audited as *correct* by human (len(bbox.model) over bbox.audit/bbox_correct == True)
- fraction of images where *incorrect* model predictions have been corrected by human annotation (len(bbox.model) over bbox.annotation/bbox_correct == True)

**implement a function that returns the requested information human-readable**

- build API and endpoints for each monitoring metric
  - requires db interface, crud ops, and analytics methods
- add UI refresh button xor auto-refresh rate (points to SSE capable js library)

### model failure inspection

- case: bbox model failing to predict bbox accurately
- query: given image_id, get bbox model predictions -- display alongside human annotations

**implement UI that gives overlay**

- how to draw squares on a screen with js? plotting library that draws squares from coordinates
- maybe generate an image using py library, then display img?

### dataset creation

- create dataset bbox.dataset
- schema
  - image_id
  - bboxes
- inclusion criteria
  - Prioritize human bounding box annotations over model predictions.
  - Prioritize most recent bounding boxes.

## mongodb analytics

- [Introduction to the MongoDB Aggregation Framework | MongoDB](https://www.mongodb.com/developer/products/mongodb/introduction-aggregation-framework/)
- [PyMongo — MongoDB Drivers](https://www.mongodb.com/docs/drivers/pymongo/)

## data samples

1. metadata

```js
{
    "image_id": "000ab0dfc1f4ba6f6531b908e4b7d71e",
    "capture_timestamp": 1704063601
}
```

2. bbox.model

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

3. bbox.human_audit

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

4. bbox.human_annotation

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
