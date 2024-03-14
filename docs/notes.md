## setup

- download data

## planning

- objective: a few tasks revolving around data loading, analysis and processing
- motivation: tbd
- stakeholder: discussion panel
- boundry conditions:
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
- fraction of images where model predictions have been audited as *correct* by human (len(bbox.model) over bbox.audit/bbox_correct == True))
- fraction of images where *incorrect* model predictions have been corrected by human annotation (len(bbox.model) over bbox.annotation/bbox_correct == True))

**implement a function that returns the requested information human-readable**

- build API and endpoints for each monitoring metric
	- requires db interface, crud ops, and analytics methods
- add UI refresh button xor auto-refresh rate (points to SSE capable js library)

### model failure inspection
- case: bbox model failing to predict bbox accuratly
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
