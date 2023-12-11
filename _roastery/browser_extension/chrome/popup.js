document.getElementById('sendButton').addEventListener('click', function() {
    var inputText = document.getElementById('inputText').value;
    fetch('http://localhost:8000/prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: inputText }),
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch((error) => {
      console.error('Error:', error);
    });
  });