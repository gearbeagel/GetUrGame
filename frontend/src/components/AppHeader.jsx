import React from 'react';
import { Link } from 'react-router-dom';
import NeonButton from './NeonButton';
import { handleSteamLogout } from '../misc/Api';

const AppHeader = ({ showFavorites = true }) => {
  return (
    <header className="bg-black py-4 px-8 flex justify-between items-center">
      <Link to="/">
        <h1 className="text-3xl font-bold animate-pulse">
          <span className="text-blue-500">get</span>{" "}
          <span className="text-pink-500">ur</span>{" "}
          <span className="text-green-500">game!!!</span>
        </h1>
      </Link>
      <nav className="flex space-x-4">
        <Link to="/games">
          <NeonButton color="pink">Your Games</NeonButton>
        </Link>
        <Link to="/get-recs">
          <NeonButton color="green">Get Recommendations</NeonButton>
        </Link>
        {showFavorites && (
          <Link to="/favorites">
            <NeonButton color="purple">Favorites</NeonButton>
          </Link>
        )}
        <NeonButton color="blue" onClick={handleSteamLogout}>
          Logout
        </NeonButton>
      </nav>
    </header>
  );
};

export default AppHeader;
