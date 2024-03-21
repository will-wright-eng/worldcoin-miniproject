document.getElementById('saveAnnotation').addEventListener('click', function() {
    // Assuming you have a function to gather annotation data from the canvas
    const annotationData = getAnnotationData(); // Implement this function based on your app's logic

    // Example of calling a backend service to save annotation data
    fetch('/api/annotations/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(annotationData),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to save annotation');
    })
    .then(data => {
        console.log('Annotation saved:', data);
        // Update status message or UI accordingly
    })
    .catch(error => console.error('Error saving annotation:', error));
});

document.getElementById('loadImage').addEventListener('click', function() {
    // Example of calling a backend service to get an image URL or image data
    fetch('/api/images/random')
    .then(response => response.json())
    .then(data => {
        // Use fabric.js or another method to load the image onto the canvas
        console.log('Image data:', data);
    })
    .catch(error => console.error('Error loading image:', error));
});
