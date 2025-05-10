import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import NeonButton from "../components/NeonButton";
import GameBox from "../components/GameBox";
import axios from "axios";
import { getCsrfToken, handleSteamLogout } from "../misc/Api";
import { FaSpinner } from "react-icons/fa";
import AppHeader from "./AppHeader";

const apiUrl = import.meta.env.VITE_API_URL

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [favoritedGames, setFavoritedGames] = useState(new Set());

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const getRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const csrfToken = await getCsrfToken();
      console.log("CSRF Token being sent:", csrfToken);

      const response = await axios.post(
        `${apiUrl}/get-recs/`,
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

  const checkFavoriteStatus = async (appid) => {
    try {
      const response = await axios.get(
        `${apiUrl}/user/favorites/${appid}/`,
        { withCredentials: true }
      );
      return true;
    } catch (error) {
      if (error.response?.status === 404) {
        return false;
      }
      throw error;
    }
  };

  const handleFavorite = async (game) => {
    try {
      const csrfToken = await getCsrfToken();
      await axios.post(
        `${apiUrl}/user/favorites/`,
        {
          appid: game.appid,
          name: game.name,
          header_image: game.header_image,
          short_description: game.short_description
        },
        {
          withCredentials: true,
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        }
      );
      setFavoritedGames(prev => new Set([...prev, game.appid]));
    } catch (error) {
      console.error("Error adding favorite:", error);
      alert("Failed to add to favorites");
    }
  };

  const handleUnfavorite = async (game) => {
    try {
      const csrfToken = await getCsrfToken();
      await axios.delete(
        `${apiUrl}/user/favorites/${game.appid}/`,
        {
          withCredentials: true,
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
        }
      );
      setFavoritedGames(prev => {
        const newSet = new Set(prev);
        newSet.delete(game.appid);
        return newSet;
      });
    } catch (error) {
      console.error("Error removing favorite:", error);
      alert("Failed to remove from favorites");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <AppHeader />
      <main className="p-8">
        <h2 className="text-4xl font-bold mb-10 text-center">
          Recommended Games
        </h2>
        <div className="text-center mb-8 flex justify-center">
          <NeonButton color="green" onClick={getRecommendations}>
            Get Recommendations
          </NeonButton>
        </div>
        <div className="relative min-h-[200px]">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <FaSpinner
                className={`animate-spin text-${getRandomColor()}-500 text-4xl`}
              />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {recommendations.map((game, index) => (
                <GameBox
                  key={game.appid}
                  game={game}
                  appid={game.appid}
                  cover={game.header_image}
                  index={index}
                  isRecommendation={true}
                  onFavorite={() => handleFavorite(game)}
                  onUnfavorite={() => handleUnfavorite(game)}
                  isFavorited={favoritedGames.has(game.appid)}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
