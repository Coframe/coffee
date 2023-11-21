(function() {
  // Define application state and operations
  const appState = {
      consoleErrors: [],
      loading: false,
      selectionMode: true,
      currentElement: null,
      status: null,

      setConsoleErrors(newErrors) {
          this.consoleErrors = newErrors;
          if(SendErrorsButton())
            SendErrorsButton().style.display = newErrors.length > 0 ? 'block' : 'none';
      },

      setLoading(loading) {
          this.loading = loading;
          if(LoadingIndicator())
            LoadingIndicator().style.display = loading ? 'block' : 'none';
      },

      setSelectionMode(newSelectionMode) {
          this.selectionMode = newSelectionMode;
          if(ToogleSelectionModeButton())
            ToogleSelectionModeButton().style.backgroundColor = newSelectionMode ? '#0076FF' : '#ffffff1a';

          if(SelectedDomPreview())
            SelectedDomPreview().style.opacity = newSelectionMode ? 1 : 0.0;

            this.currentElement && this.setCurrentElement(null);
          document.body.classList.toggle('selection-mode-active', newSelectionMode);
      },

      setCurrentElement(element) {
          if (this.currentElement) {
              this.currentElement.classList.remove('coffee-highlighted-class');
          }
          this.currentElement = element;
          const previewText = element ? element.outerHTML : 'Press an element to modify it specifically';
          if(SelectedDomPreview())
            SelectedDomPreview().innerText = previewText;
          element && element.classList.add('coffee-highlighted-class');
      },

      setStatus(status) {
          this.status = status;
          if(CoffeeStatus()){
            CoffeeStatus().innerText = status;
            CoffeeStatus().display = status ? 'block' : 'none';
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
      div.id = 'coframeCoffeeDiv';
      div.innerHTML = getCoffeeUIHtml();
      return div;
  }

  function getCoffeeUIHtml() {
      // Returns the inner HTML for the coffee UI
      const loadingDots = Array(3).fill('<span class="CoffeeLoadingDot">.</span>').join('');

      return `
      <input id="CoffeeInput" type="text">
      <div id='CoffeeMeta'>
          <button id='CoffeeToggleSelectionMode'>🎯</button>
          <div id="CoffeePreview" class="CoffeeCode">Press an element to modify it specifically</div>
          <button id="CoffeeSendErrorsButton">🐞</button>
          <button id="CoffeeUpdateButton">Update ✨</button>
      </div>
      <div id="CoffeeLoadingIndicator">
          <span class="CoffeePulse">☕</span> Brewing${loadingDots}
      </div>
      <div id="CoffeeStatus" class="CoffeeCode">
      </div>
      <style>
          #coframeCoffeeDiv {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 100000;
            background: rgba(10, 10, 10, 0.8);
            padding: 10px;
            border-radius: 10px;
            width: 450px;
            backdrop-filter: blur(10px);
            box-shadow: 10px 10px 10px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            cursor: move;
          }

          #CoffeeInput {
            padding: 5px;
            border-radius: 5px;
            box-sizing: border-box;
            width: 100%;
            border: none;
          }

          #CoffeeMeta {
              display: flex;
              gap: 8px;
          }

          #CoffeeMeta button {
              height: 38px;
              margin-top: 10px;
              border: none;
              cursor: pointer;
              background-color: #2d2929;
              color: #fff;
              padding: 5px;
              border-radius: 5px;
              box-sizing: border-box;
          }

          #CoffeeToggleSelectionMode {
              background-color: #0076FF;
          }

          .CoffeeCode {
            font-size: 12px;
            color: white;
            font-family: monospace;
            margin-top: 10px;
            padding: 0 10px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
          }

          #CoffeePreview {
            overflow: auto;
            max-height: fit-content;
            line-height: 38px;
            white-space: nowrap;
          }

          #CoffeeMeta button#CoffeeUpdateButton {
              float: right;
              min-width: 90px;
              background-color: #0076FF;
              color: #fff;
              text-align: right;
          }
          #CoffeeLoadingIndicator {
              margin-top: 10px;
              display: none;
              color: white;
          }

          .CoffeeLoadingDot {
            animation: dot 1s infinite;
          }

          .CoffeeLoadingDot:nth-child(2) {
            animation-delay: 0.2s;
          }

          .CoffeeLoadingDot:nth-child(3) {
            animation-delay: 0.4s;
          }

          @keyframes dot {
            0%, 100% {
              opacity: 0;
            }
            50% {
              opacity: 1;
            }
          }

          .CoffeePulse {
            animation: pulse 1s infinite;
          }

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
      </style>
  `;
  }


  // Fetching and sending data
  async function postData(url = '', data = {}) {
      appState.setConsoleErrors([]);
      appState.setLoading(true);
      appState.setStatus(null);

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
              appState.setStatus(status);
          }

          appState.setLoading(false);
          return response;
      } catch (error) {
          console.log('Error generating:', error);
          appState.setLoading(false);
      }
  }

  async function sendPrompt(prompt) {
      var inputText = prompt || PromptInput().value;

      let body = {
          text: inputText,
          html: appState.currentElement ? appState.currentElement.outerHTML : null,
      };

      try {
          const data = await postData('http://localhost:8000/prompt', body);
          console.log('Generation success', data);
      } catch (error) {
          // ...
      }

      PromptInput().value = '';
  }

  async function handleDomClick(e) {
      if (!appState.selectionMode || e.target.closest('#coframeCoffeeDiv')) {
          return;
      }

      if (e.target === appState.currentElement) {
          appState.setCurrentElement(null);
      } else {
          appState.setCurrentElement(e.target);
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


  ToogleSelectionModeButton = () => document.getElementById('CoffeeToggleSelectionMode');
  SelectedDomPreview = () => document.getElementById('CoffeePreview');
  SendErrorsButton = () => document.getElementById('CoffeeSendErrorsButton');
  SendPromptButton = () => document.getElementById('CoffeeUpdateButton');
  PromptInput = () => document.getElementById('CoffeeInput');
  LoadingIndicator = () => document.getElementById('CoffeeLoadingIndicator');
  CoffeeStatus = () => document.getElementById('CoffeeStatus');

  // Event Binding
  function bindEventListeners() {
      document.body.addEventListener('click', handleDomClick);
      SendErrorsButton().addEventListener('click', sendConsoleErrors);
      ToogleSelectionModeButton().addEventListener('click', () => appState.setSelectionMode(!appState.selectionMode));
      SendPromptButton().addEventListener('click', ()=>sendPrompt());
      PromptInput().addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
              sendPrompt();
          }
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
            if (strings[0] === 'fix') {
              sendConsoleErrors();
            } else {
              sendPrompt(strings.join(' '));
            }
          }
      });
  }

  // Initialize
  function initialize() {
      const ui = createCoffeeUI();
      document.body.appendChild(ui);
      const logger = createConsoleLogger();
      (document.head || document.documentElement).appendChild(logger);
      bindEventListeners();
      appState.setConsoleErrors([]);
      appState.setLoading(false);
      appState.setSelectionMode(true);
  }

  initialize();


  console.log('Coffee is ready to brew!');
})();
