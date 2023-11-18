var div = document.createElement('div');
div.id = 'myExtensionDiv';
div.style.position = 'fixed';
div.style.top = '10px';
div.style.right = '10px';
div.style.zIndex = '1000';
div.style.backgroundColor = 'rgba(10, 10, 10, 0.8)';
div.style.padding = '10px';
div.style.borderRadius = '10px';
div.style.width = '450px';
div.style.backdropFilter = 'blur(10px)';
div.style.boxShadow = '10px 10px 10px rgba(0, 0, 0, 0.2)';
div.style.border = '1px solid rgba(255, 255, 255, 0.1)';
div.style.cursor = 'move';

// Add your interface to the div
div.innerHTML = `
  <input id="myExtensionInput" type="text" style="width: 100%; padding: 5px; box-sizing: border-box; color: black;">
  <button id="myExtensionButton" style="float:right; padding: 5px; margin-top: 5px; border: none; border-radius: 5px; cursor: pointer; background-color: #0076FF; color: #fff; text-align: right;">Update ✨</button>
  <div id="loading" style="display: none; color: white; animation: pulse 1s infinite;">
  ✨ Making magic<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
</div>

<style>
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

.dot {
  animation: dot 1s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot {
  0%, 20%, 100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}
</style>
`;

// Add the div to the body
document.body.appendChild(div);

// Add an event listener to the button
document.getElementById('myExtensionButton').addEventListener('click', function() {
  var inputText = document.getElementById('myExtensionInput').value;

  // Show the loading animation
  document.getElementById('loading').style.display = 'block';

  // Send the input text to your server
  fetch('http://localhost:8000/prompt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: inputText }),
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    // Hide the loading animation
    document.getElementById('loading').style.display = 'none';
  })
  .catch((error) => {
    console.error('Error:', error);
    // Hide the loading animation
    document.getElementById('loading').style.display = 'none';
  });

  // Clear the input field immediately after sending the request
  document.getElementById('myExtensionInput').value = '';
});

// Add a keypress event listener to the input field
document.getElementById('myExtensionInput').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    document.getElementById('myExtensionButton').click();
  }
});

// Add drag and drop functionality
var isMouseDown = false;
var mouseX, mouseY;

div.addEventListener('mousedown', function(e) {
  isMouseDown = true;
  mouseX = e.clientX - div.offsetLeft;
  mouseY = e.clientY - div.offsetTop;
});

document.addEventListener('mousemove', function(e) {
  if (isMouseDown) {
    div.style.left = (e.clientX - mouseX) + 'px';
    div.style.top = (e.clientY - mouseY) + 'px';
  }
});

document.addEventListener('mouseup', function() {
  isMouseDown = false;
});