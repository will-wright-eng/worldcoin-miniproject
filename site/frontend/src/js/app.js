document.addEventListener('DOMContentLoaded', function () {
  const canvas = new fabric.Canvas('bounding-box-canvas');
  canvas.setBackgroundColor('clear', canvas.renderAll.bind(canvas));

  // Function to process boxes data
  function processBoxes(boxes) {
    boxes.forEach(function (box) {
      // Draw predicted bounding box with dashed lines
      const predRect = new fabric.Rect({
        left: box.predicted.left * canvas.width,
        top: box.predicted.top * canvas.height,
        width: (box.predicted.right - box.predicted.left) * canvas.width,
        height: (box.predicted.bottom - box.predicted.top) * canvas.height,
        fill: 'transparent',
        stroke: 'blue',
        strokeWidth: 2,
        strokeDashArray: [5, 5] // This creates the dashed line effect
      });
      canvas.add(predRect);

      // Draw annotated bounding box or a centroid 'X' if annotated is null
      if (box.annotated) {
        const annotRect = new fabric.Rect({
          left: box.annotated.left * canvas.width,
          top: box.annotated.top * canvas.height,
          width: (box.annotated.right - box.annotated.left) * canvas.width,
          height: (box.annotated.bottom - box.annotated.top) * canvas.height,
          fill: 'transparent',
          stroke: 'red',
          strokeWidth: 2
        });
        canvas.add(annotRect);
      } else {
        // Calculate centroid of the predicted box
        const centroidX = (box.predicted.left + box.predicted.right) * canvas.width / 2;
        const centroidY = (box.predicted.top + box.predicted.bottom) * canvas.height / 2;

        // Place an 'X' at the centroid
        const text = new fabric.Text('X', {
          left: centroidX,
          top: centroidY,
          fontSize: 20,
          fill: 'red'
        });
        canvas.add(text);
      }
    });
  }

  // Function to load hardcoded data
  function loadHardcodedData() {
    const boxes = [
      {
        image_id: "123abc",
        predicted: {"top": 0.18, "left": 0.2, "bottom": 0.49, "right": 0.53},
        annotated: {"top": 0.17, "left": 0.24, "bottom": 0.41, "right": 0.55},
        delta: {"top": -0.01, "left": 0.04, "bottom": -0.08, "right": 0.02}
      },
      {
        image_id: "123abc",
        predicted: {"top": 0.16, "left": 0.47, "bottom": 0.34, "right": 0.57},
        annotated: {"top": 0.2, "left": 0.56, "bottom": 0.37, "right": 0.71},
        delta: {"top": 0.04, "left": 0.09, "bottom": 0.03, "right": 0.14}
      },
      {
        image_id: "123abc",
        predicted: {"top": 0.62, "left": 0.69, "bottom": 0.66, "right": 0.84},
        annotated: null,
        delta: null
      }
    ];
    processBoxes(boxes);
  }

  loadHardcodedData();

  function displayErrorMessage(message) {
    const errorContainer = document.getElementById('errorContainer');
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
  }

  // Modified fetch call to include 'processed' boolean
  function fetchImageIds() {
    const processed = document.getElementById('processedImagesCheckbox').checked;
    fetch(`/api/v1/model_failure_inspection/list_image_ids?processed=${processed}`)
      .then(response => response.json())
      .then(data => {
        const select = document.getElementById('imageIdSelect');
        select.innerHTML = '';
        // console.log(data);
        data.image_ids.forEach(imageId => {
          const option = new Option(imageId, imageId);
          select.add(option);
        });
      })
      .catch(error => console.error('Failed to fetch image IDs:', error));
  }

  fetchImageIds();

  document.getElementById('refreshImageIdSelect').addEventListener('click', function() {
    fetchImageIds();
  });

  document.getElementById('fetchDataButton').addEventListener('click', function() {
    const image_id = document.getElementById('imageIdSelect').value;
    if (!image_id) {
      alert('Please select an image ID.');
      return;
    }

    fetch('/api/v1/model_failure_inspection/get_image_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image_id }),
    })
    .then(response => response.json())
    .then(data => {
      if (data && data.length > 0) {
        // console.log(data);
        processBoxes(data);
      } else {
        throw new Error('No data returned from the backend');
      }
    })
    .catch(error => {
      console.error('Failed to fetch data from backend, using hardcoded data:', error);
      displayErrorMessage('Failed to fetch data from backend. Displaying hardcoded data.');
      loadHardcodedData();
    });
  });

  function resetCanvas() {
    canvas.clear();
    canvas.setBackgroundColor('clear', canvas.renderAll.bind(canvas));
  }

  document.getElementById('resetCanvasButton').addEventListener('click', function() {
    resetCanvas();
  });
});
