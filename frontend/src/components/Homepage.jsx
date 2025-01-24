import React from "react";
import NeonButton from "./NeonButton";
import { FaSteam } from "react-icons/fa";

const Homepage = ({ isAuthenticated, setIsAuthenticated, username }) => {
  const handleSteamLogin = async () => {
    try {
      const response = await fetch('/api/steam/login/?source=frontend', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
      }
    } catch (error) {
      console.error('Error during Steam login:', error);
    }
  };

  const handleSteamLogout = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/steam/logout/', {
        method: 'POST',
        credentials: 'include', 
      });
      if (response.ok) {
        setIsAuthenticated(false); 
      }
    } catch (error) {
      console.error('Error during Steam logout:', error);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <header className="text-center mb-12">
        <h1 className="text-6xl font-bold mb-4 animate-pulse">
          <span className="text-blue-500">get</span>{' '}
          <span className="text-pink-500">ur</span>{' '}
          <span className="text-green-500">game<i>!!!</i></span>
        </h1>
        <p className="text-xl text-purple-400">
          discover your next favorite game on Steam.
        </p>
        {username && <p className="text-xl text-blue-400">Welcome, {username}!</p>}
      </header>

      <main className="flex flex-col items-center space-y-6 mb-12">
        {!isAuthenticated ? (
          <NeonButton color="blue" onClick={handleSteamLogin}>
            <FaSteam className="w-6 h-6 mr-2" />
            Login with Steam
          </NeonButton>
        ) : (
          <>
            <NeonButton color="green">Look Through Your Games</NeonButton>
            <NeonButton color="pink">Get Recommendations</NeonButton>
            <NeonButton color="purple" onClick={handleSteamLogout}>
              Logout
            </NeonButton>
          </>
        )}
      </main>

      <footer className="text-center text-gray-500">
        <p>© 2025 get ur game!!! All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Homepage;