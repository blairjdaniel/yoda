var file;

function loadFile(event) {
    file = event.target.files[0];

    var buttonContainer = document.getElementById('fileButtonContainer');
    buttonContainer.innerHTML = ''; // Clear the container
  
    var button = document.createElement('button');
    button.textContent = file.name;
    button.onclick = openFile;
  
    buttonContainer.appendChild(button);
}


function openFile() {
  if (file) {
    var reader = new FileReader();
    reader.onload = function(e) {
      window.open(e.target.result);
    };
    reader.readAsDataURL(file);
  }
}

function displayFiles(event) {
  var fileList = document.getElementById('fileList');
  fileList.innerHTML = ''; // Clear the list

  for (var i = 0; i < event.target.files.length; i++) {
    var file = event.target.files[i];

    var listItem = document.createElement('li');
    listItem.textContent = file.name;

    fileList.appendChild(listItem);
  }
}