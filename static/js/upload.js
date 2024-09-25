// Drag & Drop functionality
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const dropZoneText = document.getElementById('drop-zone-text');

dropZone.addEventListener('click', () => {
  fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');

  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    updateDropZoneText(fileInput.files[0].name); // Update the drop zone text
  }
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) {
    updateDropZoneText(fileInput.files[0].name);  // Update the drop zone text
  }
});

function updateDropZoneText(filename) {
  dropZoneText.textContent = `File selected: ${filename}`;
}

// Handle form submission with AJAX
document.getElementById('upload-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('prompt', document.getElementById('prompt').value);

  // Show the progress indicator
  document.getElementById('progress').style.display = 'block';

  // Hide previous results
  document.getElementById('result-box').style.display = 'none';

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    if (response.ok) {
      const data = await response.json();  // Expecting JSON with the transformed image URL

      // Hide the progress indicator
      document.getElementById('progress').style.display = 'none';

      // Show the result box with the transformed image
      const transformedImage = document.getElementById('transformed-image');
      const downloadBtn = document.getElementById('download-btn');

      transformedImage.src = data.image_url;
      downloadBtn.href = data.image_url;  // Set the download link
      downloadBtn.download = `transformed-${fileInput.files[0].name}`;  // Set the download filename

      document.getElementById('result-box').style.display = 'block';
      // Scroll down to the result box
      document.getElementById('result-box').scrollIntoView({ behavior: 'smooth' });
    } else {
      alert('Error: Something went wrong with the upload.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error: Failed to process the request.');
  }
});
