import React, { useState } from "react";
import NeonButton from "./NeonButton";
import { FaSteam } from "react-icons/fa";
import axios from "axios";
import { handleSteamLogout } from "../misc/Api";
import { FaSpinner } from "react-icons/fa";

const Homepage = ({ isAuthenticated, username }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const handleSteamLogin = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/steam/login/?source=frontend",
        {
          withCredentials: true,
        }
      );
      if (response.data.redirect_url) {
        window.location.href = response.data.redirect_url;
      }
    } catch (error) {
      console.error("Error during Steam login:", error);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <header className="text-center mb-8">
        <h1 className="text-6xl font-bold mb-4 animate-pulse">
          <span className="text-blue-500">get</span>{" "}
          <span className="text-pink-500">ur</span>{" "}
          <span className="text-green-500">
            game<i>!!!</i>
          </span>
        </h1>
        <p className="text-xl text-purple-400 mb-3">
          discover your next favorite game on Steam.
        </p>
        {username && (
          <p className="text-xl text-blue-400 mt-3">welcome, {username}!</p>
        )}
      </header>

      <main className="flex flex-col items-center space-y-6 mb-12">
        {error && <p className="text-red-500">{error}</p>}
        {loading ? (
          <div className="text-center">
          <FaSpinner
            className={`animate-spin text-${getRandomColor()}-500 text-4xl mx-auto`}
          />
        </div>
        ) : !isAuthenticated ? (
          <NeonButton color="blue" onClick={handleSteamLogin}>
            <FaSteam className="w-6 h-6 mr-2" />
            Login with Steam
          </NeonButton>
        ) : (
          <>
            <NeonButton color="pink" href="/games">
              Look Through Your Games
            </NeonButton>
            <NeonButton color="green" href="/get-recs">
              Get Recommendations
            </NeonButton>
            <NeonButton color="purple" href="/favorites">
              Your Favorites
            </NeonButton>
            <NeonButton color="blue" onClick={handleSteamLogout}>
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
