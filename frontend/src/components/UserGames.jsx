import GameBox from "../components/GameBox";
import { Link } from "react-router-dom";
import NeonButton from "../components/NeonButton";
import { useEffect, useState } from "react";
import axios from "axios";

export default function GamesPage() {
  const [gameData, setGameData] = useState([]);

  const getGameData = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/user/games/",
        {
          withCredentials: true,
        }
      );
      setGameData(response.data);
    } catch (error) {
      console.error("Error fetching game data:", error);
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
          <NeonButton color="pink">Get Recommendations</NeonButton>
          <NeonButton color="purple">Logout</NeonButton>
        </nav>
      </header>
      <main className="p-8">
        <h2 className="text-4xl font-bold mb-10 text-center">Your Games</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {gameData.map((game, index) => (
            <GameBox key={game.id} game={game} index={index} />
          ))}
        </div>
      </main>
    </div>
  );
}
