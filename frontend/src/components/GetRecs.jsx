import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import NeonButton from "../components/NeonButton";
import GameBox from "../components/GameBox";
import axios from "axios";
import { getCsrfToken, handleSteamLogout } from "../misc/Api";
import { FaSpinner } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const getRecommendations = async () => {
    setLoading(true);
    setError(null);
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    try {
      const csrfToken = await getCsrfToken();
      console.log("CSRF Token being sent:", csrfToken);

      const response = await axios.post(
        `${baseUrl}/api/get-recs/`,
        {},
        {
          withCredentials: true,
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        }
      );
      setRecommendations(response.data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setError("Failed to fetch recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="bg-black py-4 px-8 flex justify-between items-center">
        <Link to="/">
          <h1 className="text-3xl font-bold animate-pulse">
            <span className="text-blue-500">get</span>{" "}
            <span className="text-pink-500">ur</span>{" "}
            <span className="text-green-500">game!!!</span>
          </h1>
        </Link>
        <nav className="flex space-x-4">
          <Link to="/">
            <NeonButton color="blue">Home</NeonButton>
          </Link>
          <Link to="/games">
            <NeonButton color="pink">Your Games</NeonButton>
          </Link>
          <NeonButton color="purple" onClick={() => handleSteamLogout(navigate)}>
            Logout
          </NeonButton>
        </nav>
      </header>
      <main className="p-8">
        <h2 className="text-4xl font-bold mb-10 text-center">
          Recommended Games
        </h2>
        <div className="text-center mb-8 flex justify-center">
          <NeonButton color="green" onClick={getRecommendations}>
            Get Recommendations
          </NeonButton>
        </div>
        {loading && (
          <div className="text-center">
            <FaSpinner
              className={`animate-spin text-${getRandomColor()}-500 text-4xl mx-auto`}
            />
          </div>
        )}
        {error && <div className="text-red-500 text-center">{error}</div>}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {recommendations.map((game, index) => (
            <GameBox
              key={game.AppID}
              game={game}
              appid={game.AppID}
              cover={game.header_image}
              index={index}
            />
          ))}
        </div>
      </main>
    </div>
  );
}
