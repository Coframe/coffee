(function() {
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

  // Listens for console logs, to fix bugs and warnings
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
    const canvas = document.createElement('div');
    canvas.id = 'CoffeeCanvas';

    canvas.innerHTML = `
      <div id="CoffeeUI">
        <textarea id="CoffeeInput" rows="1"></textarea>
        <div id="CoffeeOutput"></div>
      </div>

      <style>
        #CoffeeCanvas {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          z-index: 100000;
        }

        #CoffeeUI {
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

    return canvas;
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


  function handleCanvasClick(e) {
    elements = document.elementsFromPoint(e.clientX, e.clientY)

    if(elements[0].id === Canvas().id) elements.shift();

    if(Canvas().contains(elements[0])) return

    if(appState.currentElement === elements[0]) {
      appState.setCurrentElement(null);
    } else {
      appState.setCurrentElement(elements[0], {point: {x: e.clientX, y: e.clientY}});
    }
  }

  function drawElementOverlay(rect) {
    const canvas = Canvas()

    const previousOverlay = canvas.querySelector('#coffeeElementOverlay');
    if (previousOverlay) previousOverlay.remove();

    if (!rect) return;


    const overlay = document.createElement('div');
    overlay.id = 'coffeeElementOverlay';
    Object.assign(overlay.style, {
      position: 'absolute',
      border: '2px solid rgb(172, 207, 253)',
      left: `${rect.left}px`,
      top: `${rect.top}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`,
      pointerEvents: 'none'
    });


    canvas.appendChild(overlay);
  }

  showCommentOverlay = (point) => {
    const coffeeUI = CoffeeUI();
    const coffeeInput = CoffeeInput();

    if (point) {
      coffeeUI.style.display = 'block';
      coffeeUI.style.top = `${point.y - 10}px`;

      const coffeeUIWidth = coffeeUI.offsetWidth;
      const viewportWidth = window.innerWidth;

      // Check if the CoffeeUI would go out of the viewport on the right side
      if (point.x + coffeeUIWidth + 20 > viewportWidth) {
        coffeeUI.style.left = `${point.x - coffeeUIWidth - 20}px`;
      } else {
        coffeeUI.style.left = `${point.x + 20}px`;
      }

      coffeeInput.focus();
      coffeeInput.select();
    } else {
      coffeeUI.style.display = 'none';
    }
  };


  Canvas = () => document.getElementById('CoffeeCanvas');
  CoffeeUI = () => document.getElementById('CoffeeUI');
  CoffeeInput = () => document.getElementById('CoffeeInput');
  CoffeeOutput = () => document.getElementById('CoffeeOutput');



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


  function initialize() {
      document.body.appendChild(createCoffeeUI());
      const logger = createConsoleLogger();
      (document.head || document.documentElement).appendChild(logger);
      bindEventListeners();
      appState.setConsoleErrors([]);
      appState.setLoading(false);
  }

  initialize();
  console.log('☕ Coffee is ready to brew!');
})();
