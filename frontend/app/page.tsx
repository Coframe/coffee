"use client";
import { useState, useEffect } from 'react';
import InputForm from './components/InputForm'
import Welcome from './components/welcome'

enum Plan {
  Free = 'free',
  Premium = 'premium',
  Enterprise = 'enterprise',
}

export default function Page() {
  const [name, setName] = useState('')
  console.log({name})
  return (
    <>
      <InputForm name={name} setName={setName} />
      <Welcome name={name} />
    </>
  )
}
