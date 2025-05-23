import GameBox from "../components/GameBox";
import React from "react";
import { useEffect, useState } from "react";
import axios from "axios";
import { FaSpinner } from "react-icons/fa";
import AppHeader from "./AppHeader";
import Pagination from './Pagination';

export default function GamesPage() {
  const [gameData, setGameData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const apiUrl = import.meta.env.VITE_API_URL;

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const getGameData = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${apiUrl}/user/games/?page=${page}`,
        { withCredentials: true }
      );
      setGameData(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
      setCurrentPage(page);
    } catch (error) {
      console.error("Error fetching games:", error);
      setError("Failed to fetch games");
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    getGameData(newPage);
  };

  useEffect(() => {
    getGameData(1);
  }, []);

  return (
    <div className="min-h-screen bg-black text-white">
      <AppHeader />
      <main className="p-8">
        <h2 className="text-4xl font-bold mb-10 text-center">Your Games</h2>
        {error && <p className="text-red-500">{error}</p>}
        {loading ? (
          <div className="text-center">
            <FaSpinner className={`animate-spin text-${getRandomColor()}-500 text-4xl mx-auto`} />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {gameData.map((game, index) => (
                <GameBox
                  key={game.id}
                  game={game}
                  appid={game.appid}
                  cover={game.cover_url}
                  index={index}
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
