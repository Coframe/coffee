"use client";
import { useState, useEffect } from 'react';

const MovieCard = ({activeCard, cardIndex, title, subtitle, buttonText, trivia, heroImage}) => (
  activeCard === cardIndex ?
  <div className={`bg-black bg-opacity-75 rounded-lg shadow-lg mt-10 w-full max-w-lg transition-opacity duration-1000 ease-in-out`} style={{backdropFilter: 'blur(10px)'}}>
    <img src={heroImage} alt={title} className="w-full h-64 object-cover rounded-t-lg" style={{objectFit: 'cover'}} />
    <div className="p-5">
      <h1 className="text-6xl font-bold mb-5 text-shadow-lg text-white" style={{color: '#FFFFFF'}}>{title}</h1>
      <p className="text-2xl g text-shadow-md text-white" style={{color: '#FFFFFF'}}>{subtitle}</p>
      <p className="text-xl g text-shadow-md text-white mt-5" style={{color: '#FFFFFF'}}>{trivia}</p>
      <button className="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded mt-10 hover:bg-blue-700 focus:outline-none focus:ring focus:border-blue-300 shadow-lg transition-colors duration-200 ease-in-out">
        {buttonText}
      </button>
    </div>
  </div> : null
);

export default function Home() {
  const [activeCard, setActiveCard] = useState(0);

  const MenuBar = () => (
    <nav className="bg-opacity-75 p-4">
      <ul className="flex justify-between items-center">
        <li><a href="#" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Home</a></li>
        <li><a href="#about" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">About</a></li>
        <li><a href="#contact" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Contact</a></li>
        <div className="flex items-center space-x-2">
          <li><img src="https://via.placeholder.com/40" alt="Profile" className="inline-block h-10 w-10 rounded-full" /></li>
          <li><button className="text-white bg-blue-500 hover:bg-blue-700 font-bold py-2 px-4 rounded transition-colors duration-200 ease-in-out">Login</button></li>
        </div>
      </ul>
    </nav>
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard((prevActiveCard) => (prevActiveCard + 1) % 4);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <MenuBar />
      <main className="flex flex-col justify-center items-center min-h-screen text-white" style={{ backgroundImage: 'url(https://source.unsplash.com/random/800x600?background)', backgroundSize: 'cover', backgroundAttachment: 'fixed', paddingBottom: '100px' }}>
      <div className="flex flex-col justify-center items-center h-full">
        <MovieCard activeCard={activeCard} cardIndex={0} title="Welcome to MovieFrame!" subtitle="Discover the latest movies here." buttonText="Explore Now!" trivia="Did you know? The first movie ever made was 'Roundhay Garden Scene' in 1888." heroImage="https://source.unsplash.com/random/800x600?movie" />
        <MovieCard activeCard={activeCard} cardIndex={1} title="Hello Movie Lover!" subtitle="Ready to dive into the world of cinema?" buttonText="Dive in!" trivia="Trivia: 'The Shawshank Redemption' is the highest rated movie on IMDb." heroImage="https://source.unsplash.com/random/800x600?cinema" />
        <MovieCard activeCard={activeCard} cardIndex={2} title="Welcome back, Movie Buff!" subtitle="Let's continue where we left off." buttonText="Continue!" trivia="Fun Fact: The longest movie ever made is 'The Cure for Insomnia' with a runtime of 85 hours." heroImage="https://source.unsplash.com/random/800x600?film" />
        <MovieCard activeCard={activeCard} cardIndex={3} title="Ready for more Movies?" subtitle="Let's explore new releases." buttonText="Explore!" trivia="Movie Trivia: 'Gone with the Wind' holds the record for the most Oscars won by a single film." heroImage="https://source.unsplash.com/random/800x600?new-releases" />
      </div>
      </main>

    <footer className="bg-black text-white p-4 text-center">
      Basic Footer Content
      <div>© 2023 MovieFrame, Inc.</div>
      <div>Privacy Policy</div>
      <div>Terms of Service</div>
    </footer>

    </>
  )
}