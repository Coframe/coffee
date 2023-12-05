import React from 'react';

interface CalculatorProps {
  operationsScreen: string;
  setOperationsScreen: (value: string) => void;
  performOperations: () => void;
}

const Calculator: React.FC<CalculatorProps> = ({ operationsScreen, setOperationsScreen, performOperations }) => {
  const buttons = [
    '7', '8', '9', '+',
    '4', '5', '6', '-',
    '1', '2', '3', '*',
    'C', '0', '=', '/',
  ];

  const onButtonClick = (buttonValue: string) => {
    if (buttonValue === 'C') {
      setOperationsScreen('');
    } else if (buttonValue === '=') {
      performOperations();
    } else {
      setOperationsScreen(operationsScreen + buttonValue);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-200">
      <div className="bg-white shadow rounded p-4 max-w-md w-full">
        <div className="flex justify-end mb-4 p-2 bg-gray-100 rounded">
          <div className="text-right font-mono text-lg tracking-wide">{operationsScreen}</div>
        </div>
        <div className="grid grid-cols-4 gap-2">
          {buttons.map((button) => (
            <button
              key={button}
              onClick={() => onButtonClick(button)}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              {button}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Calculator;
