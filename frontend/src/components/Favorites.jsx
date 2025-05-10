import React, { useState, useEffect } from "react";
import { getCsrfToken } from "../misc/Api";
import GameBox from "./GameBox";
import axios from "axios";
import { handleSteamLogout } from "../misc/Api";
import { FaSpinner } from "react-icons/fa";
import AppHeader from "./AppHeader";
import Pagination from './Pagination';

const apiUrl = import.meta.env.VITE_API_URL;

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const getFavorites = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${apiUrl}/user/favorites/?page=${page}`,
        { withCredentials: true }
      );
      setFavorites(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
      setCurrentPage(page);
    } catch (error) {
      console.error("Error fetching favorites:", error);
      setError("Failed to fetch favorites");
    } finally {
      setLoading(false);
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
      const newFavorites = await axios.get(
        `${apiUrl}/user/favorites/?page=${currentPage}`,
        { withCredentials: true }
      );
      setFavorites(newFavorites.data.results);
    } catch (error) {
      console.error("Error removing favorite:", error);
      alert("Failed to remove from favorites");
    }
  };

  const handlePageChange = (newPage) => {
    getFavorites(newPage);
  };

  useEffect(() => {
    getFavorites(1);
  }, []);

  return (
    <div className="min-h-screen bg-black text-white">
      <AppHeader />
      <main className="p-8">
        <h2 className="text-4xl font-bold mb-10 text-center">Your Favorites</h2>
        {error && <p className="text-red-500">{error}</p>}
        {loading ? (
          <div className="text-center">
            <FaSpinner className={`animate-spin text-${getRandomColor()}-500 text-4xl mx-auto`} />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {favorites.map((game, index) => (
                <GameBox
                  key={game.appid}
                  game={game}
                  appid={game.appid}
                  cover={game.header_image}
                  index={index}
                  isFavorited={true}
                  onUnfavorite={() => handleUnfavorite(game)}
                />
              ))}
            </div>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </main>
    </div>
  );
}
