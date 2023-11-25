(function() {
  // Define application state and operations
  const appState = {
      consoleErrors: [],
      loading: false,
      currentElement: null,
      status: null,

      setConsoleErrors(newErrors) {
          this.consoleErrors = newErrors;
      },

      setLoading(loading) {
          this.loading = loading;
          if(CoffeeInput()) {
            CoffeeInput().style.display = loading ? 'none' : 'block';
            CoffeeInput().select();
          }

          this.setStatus(null);
      },
      setCurrentElement(element, options={}) {
          this.currentElement = element;
          rect = element?.getBoundingClientRect();
          drawElementOverlay(rect);
          showCommentOverlay(options.point);
      },

      setStatus(status) {
          this.status = status;
          if(CoffeeOutput()){
            CoffeeOutput().innerText = status;
            CoffeeOutput().style.display = status ? 'block' : 'none';
          }
      }
  };

  // Create Logger
  createConsoleLogger = () => {
      const script = document.createElement('script');
      script.textContent = `
      (function() {
        const captureConsole = (method) => {
          const original = console[method];
          console[method] = function() {
            original.apply(console, arguments);
            const args = Array.from(arguments).filter(arg =>
              !(typeof arg === 'function' || typeof arg === 'symbol')
            );
            window.postMessage({ type: "CONSOLE_CAPTURE", method, args }, "*");
          };
        };

        // Capture console.log, console.error, and console.warn
        captureConsole('log');
        captureConsole('error');
        captureConsole('warn');

        // Setup window.coffee
        window.c = function(strings, ...values) {
          window.postMessage({ type: "COFFEE_COMMAND", strings, values }, "*");
          return "☕ Brewing...";
        }
        window.c.fix = function() {
          window.postMessage({ type: "COFFEE_COMMAND", strings: ['fix'], values: [] }, "*");
          return "☕ Brewing...";
        }
      })();
    `;
      return script;
  }

  // Create UI components
  function createCoffeeUI() {
    const div = document.createElement('div');
    div.id = 'coframeCoffeeUI';

    // Using textarea instead of input for multi-line support
    div.innerHTML = `
      <textarea id="CoffeeInput" rows="1"></textarea>
      <div id="CoffeeOutput"></div>
      <style>
        #coframeCoffeeUI {
          display: none;
          position: fixed;
          background: rgba(10, 10, 10, 0.8);
          border-radius: 10px;
          overflow: hidden;
          backdrop-filter: blur(10px);
          box-shadow: 10px 10px 10px rgba(0, 0, 0, 0.2);
          z-index:1;
          width: 200px;
        }

        #CoffeeInput {
          padding: 5px 10px;
          border: none;
          background: transparent;
          color: white;
          overflow-y: hidden; /* Prevent scrollbar */
          resize: none; /* Disable resizing of the textarea */
          outline: none;
        }

        #CoffeeOutput {
          display: none;
          padding: 5px 10px;
          color: white;
        }
      </style>
    `;
    document.body.appendChild(div); // Append the div to the body here

    return div;
  }


  // Fetching and sending data
  async function postData(url = '', data = {}) {
      appState.setConsoleErrors([]);
      appState.setLoading(true);
      appState.setStatus("☕ Brewing...");

      try {
          const response = await fetch(url, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'text/event-stream'
              },
              body: JSON.stringify(data),
          });
          // Handle streaming response
          const reader = response.body.getReader();
          while (true) {
              const { value, done } = await reader.read();
              if (done) break;
              const text = new TextDecoder().decode(value);
              const json_resp = JSON.parse(text);
              const status = json_resp.status;
              console.log('☕', status);
              appState.setStatus('☕ '+status);
          }

          appState.setLoading(false);
          return response;
      } catch (error) {
          console.log('Error generating:', error);
          appState.setLoading(false);
      }
  }

  async function sendPrompt(prompt, options={}) {
      console.log('Sending Prompt', prompt, appState.currentElement)
      let body = {
          text: prompt,
          html: appState.currentElement ? appState.currentElement.outerHTML : null,
          ...options
      };

      try {
          const data = await postData('http://localhost:8000/prompt', body);
          console.log('Generation success', data);
      } catch (error) {
          // ...
      }
  }


  // Error Sending Function
  async function sendConsoleErrors() {
      if (appState.consoleErrors.length === 0) {
          return;
      }

      try {
          const data = await postData('http://localhost:8000/errors', appState.consoleErrors.map(e => ({
              message: e.args.join('\n')
          })));
          console.log('Console Errors sent', data);
      } catch (error) {
          // Error handling
      }
  }

  function handleCanvasClick(e) {
    elements = document.elementsFromPoint(e.clientX, e.clientY)

    // check if element is canvas itself
    if(elements[0].id === Canvas().id) elements.shift();

    // check if element is withing canvas
    if(Canvas().contains(elements[0])) return

    if(appState.currentElement === elements[0]) {
      appState.setCurrentElement(null);
    } else {
      appState.setCurrentElement(elements[0], {point: {x: e.clientX, y: e.clientY}});
    }
  }

  function createCanvas() {
    // Create a container div to hold all overlays
    const overlayContainer = document.createElement('div');
    overlayContainer.id = 'coffeeCanvas';
    overlayContainer.style.position = 'fixed';
    overlayContainer.style.top = '0';
    overlayContainer.style.left = '0';
    overlayContainer.style.width = '100vw';
    overlayContainer.style.height = '100vh';
    overlayContainer.style.zIndex = '100000';

    return overlayContainer;
  }

  function drawElementOverlay(rect) {
    console.log('drawElementOverlay');
    const canvas = Canvas()

    // Clear previous #coffeeElementOverlay if any
    const previousOverlay = canvas.querySelector('#coffeeElementOverlay');
    if (previousOverlay) previousOverlay.remove();

    if (!rect) return;

    // Create a new overlay div to represent the rectangle
    const overlay = document.createElement('div');
    overlay.id = 'coffeeElementOverlay';
    overlay.style.position = 'absolute';
    overlay.style.border = '2px solid rgb(172, 207, 253)';
    overlay.style.left = `${rect.left}px`;
    overlay.style.top = `${rect.top}px`;
    overlay.style.width = `${rect.width}px`;
    overlay.style.height = `${rect.height}px`;
    overlay.style.pointerEvents = 'none'; // Make sure the overlay doesn't capture clicks

    // Append the overlay div to the container
    canvas.appendChild(overlay);
  }

  showCommentOverlay = (point) => {
    const coffeeUI = CoffeeUI(); // Assuming this is a function that returns your UI element
    const coffeeInput = CoffeeInput(); // And this returns your input element

    if (point) {
      coffeeUI.style.display = 'block';
      coffeeUI.style.top = `${point.y - 10}px`;

      const coffeeUIWidth = coffeeUI.offsetWidth; // Get the width of the CoffeeUI element
      const viewportWidth = window.innerWidth; // Width of the viewport

      // Check if the CoffeeUI would go out of the viewport on the right side
      if (point.x + coffeeUIWidth + 20 > viewportWidth) {
        coffeeUI.style.left = `${point.x - coffeeUIWidth - 20}px`;
      } else {
        coffeeUI.style.left = `${point.x + 20}px`;
      }

      // Focus and select the text in the input
      coffeeInput.focus();
      coffeeInput.select();
    } else {
      coffeeUI.style.display = 'none';
    }
  };


  function handlePromptSubmit(prompt){
    prompt = prompt || CoffeeInput().value;
    if(prompt.startsWith('/f')){
      sendConsoleErrors();
    } else if (prompt.startsWith('/a')) {
      prompt = prompt.substring(2);
      sendPrompt(prompt, {agent: 'auto_gpt'});
    } else {
      sendPrompt(prompt);
    }
  }


  Canvas = () => document.getElementById('coffeeCanvas');
  CoffeeUI = () => document.getElementById('coframeCoffeeUI');
  CoffeeInput = () => document.getElementById('CoffeeInput');
  CoffeeOutput = () => document.getElementById('CoffeeOutput');


  // Event Binding
  function bindEventListeners() {
      document.addEventListener('click', handleCanvasClick, true);

      // Send prompt on enter
      CoffeeInput().addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
            handlePromptSubmit()
            e.preventDefault();
          }
      });

      // Make sure the textarea grows with content
      CoffeeInput().addEventListener('input', function() {
        this.style.height = 'auto'; // Reset the height
        this.style.height = (this.scrollHeight) + 'px'; // Set the height to scroll height
      });

      window.addEventListener("message", (event) => {
          if (event.source === window && event.data.type === "CONSOLE_CAPTURE") {
            const {
              method,
              args
            } = event.data;
            if (method === 'error' || method === 'warn') {
              appState.setConsoleErrors([...appState.consoleErrors, {
                method,
                args
              }]);
            }
          }
          if(event.source === window && event.data.type === "COFFEE_COMMAND") {
            const { strings, values } = event.data;
            handlePromptSubmit(strings.join(''));
          }
      });
  }

  // Initialize
  function initialize() {
      canvas = createCanvas();
      ui = createCoffeeUI();
      canvas.appendChild(ui);
      document.body.appendChild(canvas);
      const logger = createConsoleLogger();
      (document.head || document.documentElement).appendChild(logger);
      bindEventListeners();
      appState.setConsoleErrors([]);
      appState.setLoading(false);
  }

  initialize();
  console.log('☕ Coffee is ready to brew!');
})();
