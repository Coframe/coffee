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
        <div className="text-4xl font-bold text-center text-black animate-pulse bg-gradient-to-r from-yellow-400 via-red-500 to-pink-500 bg-clip-text text-transparent">
          Contact Page
        </div>
        <p className="text-xl text-center text-black mt-10">
          This is a completely different section.
        </p>
        <div className="mt-10">
          <form className="w-full max-w-lg">
            <div className="flex flex-wrap -mx-3 mb-6">
              <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
                <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-first-name">
                  First Name
                </label>
                <input className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white" id="grid-first-name" type="text" placeholder="Jane"/>
              </div>
              <div className="w-full md:w-1/2 px-3">
                <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-last-name">
                  Last Name
                </label>
                <input className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white" id="grid-last-name" type="text" placeholder="Doe"/>
              </div>
            </div>
            <div className="flex flex-wrap -mx-3 mb-6">
              <div className="w-full px-3">
                <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-email">
                  Email
                </label>
                <input className="appearance-none block w-full bg-gray-200 text-gray-700 border rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white" id="grid-email" type="email" placeholder="jane.doe@example.com"/>
              </div>
            </div>
            <div className="flex flex-wrap -mx-3 mb-2">
              <div className="w-full px-3">
                <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-message">
                  Message
                </label>
                <textarea className=" no-resize appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500 h-48 resize-none" id="grid-message"></textarea>
              </div>
            </div>
          </form>
        </div>
      </section>
    </div>
  )
}