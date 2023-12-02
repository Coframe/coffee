import React, { useState } from 'react';

const BlackFridaySale: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const discountRate = 20;

  const closeSaleBanner = () => {
    setIsVisible(false);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="bg-red-600 text-white rounded-lg shadow-lg p-5 m-5 relative">
      <button
        onClick={closeSaleBanner}
        className="absolute right-4 top-4 text-white text-2xl leading-none font-semibold outline-none focus:outline-none"
        aria-label="Close"
      >
        &times;
      </button>
      <div className="flex flex-col items-center justify-center">
        <h2 className="text-4xl font-bold mb-3">Black Friday Sale!</h2>
        <p className="text-2xl">
          Get an amazing <span className="font-bold">{discountRate}% OFF</span> on every movie!
        </p>
      </div>
    </div>
  );
};

export default BlackFridaySale;
