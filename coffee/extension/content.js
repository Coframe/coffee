let currentElement = null;

var div = document.createElement('div');
div.id = 'coframeCoffeeDiv';
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
  <input id="coframeCoffeeInput" type="text" style="width: 100%; padding: 5px; box-sizing: border-box;">
  <div id='coframeCoffeeMeta' style="display: flex; gap: 8px">
    <div id="coframeCoffeePreview">Press an element to modify it specifically</div>
    <button id="coframeCoffeeButton" style="float:right; padding: 5px; height: 38px; min-width: 90px; margin-top: 10px; border: none; border-radius: 5px; cursor: pointer; background-color: #0076FF; color: #fff; text-align: right;">Update ✨</button>
  </div>
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

.coffee-highlighted-class {
  background-color: rgba(173, 216, 230, 0.5);
  outline: 1px solid #ADD8E6;
}

#coframeCoffeePreview {
  font-size: 12px;
  color: white;
  font-family: monospace;
  margin-top: 10px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: auto;
  max-height: 200px;
}
</style>
`;

// Add the div to the body
document.body.appendChild(div);

// Add an event listener to the button
document.getElementById('coframeCoffeeButton').addEventListener('click', function() {
  var inputText = document.getElementById('coframeCoffeeInput').value;
  
  // Show the loading animation
  document.getElementById('loading').style.display = 'block';

  // Send the input text to your server
  let body = {
    text: inputText,
  };

  if (currentElement) {
    body['html'] = currentElement.outerHTML;
  }
  
  fetch('http://localhost:8000/prompt', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
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
  document.getElementById('coframeCoffeeInput').value = '';
});

// Add a keypress event listener to the input field
document.getElementById('coframeCoffeeInput').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    document.getElementById('coframeCoffeeButton').click();
  }
});

// Add drag and drop functionality
var isMouseDown = false;
var mouseX, mouseY;

div.addEventListener('mousedown', function(e) {
  if (e.target.id === 'coframeCoffeeInput') {
    return;
  }
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

// Add a click event listener to all elements
document.body.addEventListener('click', function(e) {
  if (e.target.closest('#coframeCoffeeDiv')) {
    return;
  }

  if (currentElement) {
    currentElement.classList.remove('coffee-highlighted-class');
    document.getElementById('coframeCoffeePreview').innerText = 'Press an element to modify it specifically';
    if (e.target === currentElement) {
      currentElement = null;
      return;
    }
  }
  // Get the outer HTML of the hovered element
  var html = e.target.outerHTML;
  console.log(html);
  // highlight the element
  e.target.classList.add('coffee-highlighted-class');
  currentElement = e.target;
  document.getElementById('coframeCoffeePreview').innerText = html;
});