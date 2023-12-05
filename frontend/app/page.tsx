"use client";
import { useState, useEffect } from 'react';
import Coffee from './coffee/Coffee';

export default function Page() {
  const [operationsScreen, setOperationsScreen] = useState('1+1');
  const performOperations = () => {
    const result = eval(operationsScreen);
    console.log(`performed operations in parent component: ${operationsScreen} = ${result}`);
    setOperationsScreen(result);
  }

  return (
    <>
      <Coffee brew="Calculator.tsx" operationsScreen={operationsScreen} setOperationsScreen={setOperationsScreen} performOperations={performOperations}>
        Generate Calculator UI using tailwind css.
        Don't use col-span, all buttons same size.
        All calculations are done in the parent component.
      </Coffee>
    </>
  )
}
