export default function Home() {

  return (
    <main className="flex flex-col justify-center items-center h-screen bg-black">
      <button 
        className={`bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded animate-bounce`}
      >
        Let's go Coframe!!
      </button>
      <div className="text-4xl font-bold text-center text-white">
        Hello World
      </div>
    </main>
  )
}