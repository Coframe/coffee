"use client";
import { useState, useEffect } from 'react';
import InputForm from './components/InputForm'

export default function Page() {
  const [name, setName] = useState('')

  return (
    <>
      <InputForm name={name} setName={setName} />
    </>
  )
}
