import React, { useState } from "react";
import NeonButton from "./NeonButton";
import { FaSteam } from "react-icons/fa";
import axios from "axios";
import { getCsrfToken } from "../misc/Api";

const Homepage = ({ isAuthenticated, username }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const handleSteamLogout = async () => {
    try {

      const response = await axios.get(
        "http://127.0.0.1:8000/api/steam/logout/",
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status === 200) {
        console.log("Logout successful!")
        window.location.reload();
      } else {
        console.error("Logout failed:", response.statusText);
      }
    } catch (error) {
      console.error("Error during Steam logout:", error);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <header className="text-center mb-12">
        <h1 className="text-6xl font-bold mb-4 animate-pulse">
          <span className="text-blue-500">get</span>{" "}
          <span className="text-pink-500">ur</span>{" "}
          <span className="text-green-500">
            game<i>!!!</i>
          </span>
        </h1>
        <p className="text-xl text-purple-400">
          discover your next favorite game on Steam.
        </p>
        {username && (
          <p className="text-xl text-blue-400">welcome, {username}!</p>
        )}
      </header>

      <main className="flex flex-col items-center space-y-6 mb-12">
        {error && <p className="text-red-500">{error}</p>}
        {loading ? (
          <p className="text-white">Loading...</p>
        ) : !isAuthenticated ? (
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
