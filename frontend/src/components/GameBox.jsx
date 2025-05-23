import React from "react"; // noqa
import NeonButton from "./NeonButton";
import { FaRegHeart, FaHeart } from "react-icons/fa";

const colors = ["blue", "purple", "green", "pink"];

const colorClasses = {
  blue: {
    border: "border-blue-500",
    hoverBorder: "hover:border-blue-400",
    text: "text-blue-400",
  },
  purple: {
    border: "border-purple-500",
    hoverBorder: "hover:border-purple-400",
    text: "text-purple-400",
  },
  green: {
    border: "border-green-500",
    hoverBorder: "hover:border-green-400",
    text: "text-green-400",
  },
  pink: {
    border: "border-pink-500",
    hoverBorder: "hover:border-pink-400",
    text: "text-pink-400",
  },
};

const GameBox = ({
  game,
  index,
  appid,
  cover,
  isRecommendation,
  onFavorite,
  onUnfavorite,
  isFavorited = false
}) => {
  const color = colors[index % colors.length];
  const { border, hoverBorder, text } = colorClasses[color];

  const handleFavoriteClick = () => {
    if (isFavorited) {
      onUnfavorite(game);
    } else {
      onFavorite(game);
    }
  };

  return (
    <div
      className={`bg-gray-900 rounded-lg overflow-hidden shadow-lg border ${border} ${hoverBorder} transition-colors duration-300 max-w-sm mx-auto flex flex-col relative`}
    >
      <div className="relative h-48">
        <img
          src={cover || "/placeholder.svg"}
          alt={`Cover image for ${game.name}`}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-6 flex flex-col flex-grow">
        <h2 className={`text-2xl font-bold ${text} mb-3`}>{game.name}</h2>
        <p className="text-gray-400 mb-4">{game.short_description}</p>
        <div className="mt-auto flex justify-between items-center">
          <NeonButton
            color={color}
            onClick={() =>
              window.open(`https://store.steampowered.com/app/${appid}/`, "_blank")
            }
          >
            View on Steam
          </NeonButton>
          {(isRecommendation || isFavorited) && (
            <button
              onClick={handleFavoriteClick}
              className="text-red-500 hover:text-red-700 transition-colors duration-300"
              aria-label={`${isFavorited ? 'Remove' : 'Add'} ${game.name} to favorites`}
            >
              {isFavorited ? <FaHeart size={24} /> : <FaRegHeart size={24} />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameBox;
