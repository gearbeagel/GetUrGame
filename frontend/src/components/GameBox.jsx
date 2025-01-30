import React from "react";
import NeonButton from "./NeonButton";

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

const GameBox = ({ game, index, appid, cover }) => {
  const color = colors[index % colors.length];
  const { border, hoverBorder, text } = colorClasses[color];

  return (
    <div
      className={`bg-gray-900 rounded-lg overflow-hidden shadow-lg border ${border} ${hoverBorder} transition-colors duration-300 max-w-sm mx-auto flex flex-col`}
    >
      <div className="relative w-90 h-40">
        <img
          src={cover || "/placeholder.svg"}
          alt={game.name}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-6 flex flex-col flex-grow">
        <h2 className={`text-2xl font-bold ${text} mb-3`}>{game.name}</h2>
        <p className="text-gray-400 mb-4">{game.short_description}</p>
        <div className="mt-auto">
          <NeonButton
            color={color}
            onClick={() =>
              window.open(`https://store.steampowered.com/app/${appid}/`, "_blank")
            }
          >
            View on Steam
          </NeonButton>
        </div>
      </div>
    </div>
  );
};

export default GameBox;
