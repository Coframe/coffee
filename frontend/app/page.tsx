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
      <button className="w-full bg-red-500 text-white font-bold py-2 px-4 rounded mt-10 hover:bg-red-700 hover:text-white shadow-lg transition-colors duration-200 ease-in-out">
        {buttonText}
      </button>
    </div>
  </div> : null
);

export default function Home() {
  const [activeCard, setActiveCard] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard((prevActiveCard) => (prevActiveCard + 1) % 4);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="flex flex-col justify-center items-center min-h-screen text-white" style={{backgroundImage: "url('https://source.unsplash.com/random/1920x1080')", backgroundSize: 'cover', backgroundPosition: 'center', backdropFilter: 'blur(100px)', backgroundColor: '#000000'}}>
      <div className="flex flex-col justify-center items-center h-full">
        <MovieCard activeCard={activeCard} cardIndex={0} title="Welcome to MovieFrame!" subtitle="Discover the latest movies here." buttonText="Explore Now!" trivia="Did you know? The first movie ever made was 'Roundhay Garden Scene' in 1888." heroImage="https://source.unsplash.com/random/800x600?movie" />
        <MovieCard activeCard={activeCard} cardIndex={1} title="Hello Movie Lover!" subtitle="Ready to dive into the world of cinema?" buttonText="Dive in!" trivia="Trivia: 'The Shawshank Redemption' is the highest rated movie on IMDb." heroImage="https://source.unsplash.com/random/800x600?cinema" />
        <MovieCard activeCard={activeCard} cardIndex={2} title="Welcome back, Movie Buff!" subtitle="Let's continue where we left off." buttonText="Continue!" trivia="Fun Fact: The longest movie ever made is 'The Cure for Insomnia' with a runtime of 85 hours." heroImage="https://source.unsplash.com/random/800x600?film" />
        <MovieCard activeCard={activeCard} cardIndex={3} title="Ready for more Movies?" subtitle="Let's explore new releases." buttonText="Explore!" trivia="Movie Trivia: 'Gone with the Wind' holds the record for the most Oscars won by a single film." heroImage="https://source.unsplash.com/random/800x600?new-releases" />
      </div>
    </main>
  )
}