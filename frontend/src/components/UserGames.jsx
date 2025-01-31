import GameBox from "../components/GameBox";
import { Link } from "react-router-dom";
import NeonButton from "../components/NeonButton";
import { useEffect, useState } from "react";
import axios from "axios";
import { handleSteamLogout } from "../misc/Api";
import { FaSpinner } from "react-icons/fa";

export default function GamesPage() {
  const [gameData, setGameData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const getGameData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/user/games/",
        {
          withCredentials: true,
        }
      );
      setGameData(response.data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setError("Failed to fetch recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getGameData();
  }, []);

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
          <NeonButton color="pink" href="/get-recs">
            Get Recommendations
          </NeonButton>
          <NeonButton color="purple" onClick={handleSteamLogout}>
            Logout
          </NeonButton>
        </nav>
      </header>
      <main className="p-8">
        <h2 className="text-4xl font-bold mb-10 text-center">Your Games</h2>
        {error && <p className="text-red-500">{error}</p>}
        {loading && (
          <div className="text-center">
            <FaSpinner
              className={`animate-spin text-${getRandomColor()}-500 text-4xl mx-auto`}
            />
          </div>
        )}
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
      </main>
    </div>
  );
}
