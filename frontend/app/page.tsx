"use client";
import { useState, useEffect } from 'react';
import Coffee from './coffee/Coffee';

export default function Page() {
  const [operations, setOperations] = useState('1+1');
  console.log(operations);
  return (
    <>
      <Coffee brew="Calculator.tsx" operations={operations} setOperations={setOperations}>
        Generate Calculator UI using tailwind css.
        Don't use col-span, all buttons same size.
      </Coffee>
    </>
  )
}
