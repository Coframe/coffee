export default function Home() {
  return (
    <div className="flex flex-col h-full overflow-auto">
      <main className="flex flex-col justify-center items-center h-screen bg-black">
        <div className="text-4xl font-bold text-center text-white bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent">
          Hello World
        </div>
        <p className="text-xl text-center text-white mt-10">
          Coframe is building the future of living interfaces
        </p>
        <div className="mt-10">
          <button 
            className={`bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded animate-bounce`}
          >
            Try Coframe
          </button>
        </div>
        <div className="absolute bottom-5 animate-bounce">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-10 h-10 text-white">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </main>
      <section className="flex flex-col justify-center items-center h-screen bg-white">
        <div className="text-4xl font-bold text-center text-black">
          Welcome to the new section
        </div>
        <p className="text-xl text-center text-black mt-10">
          This is a completely different section.
        </p>
      </section>
    </div>
  )
}