import React from "react"

const NeonButton = ({ children, color, onClick, href }) => {
  const baseClasses =
    "px-6 py-3 rounded-full font-bold text-lg transition-all duration-300 ease-in-out flex items-center justify-center hover:cursor-pointer"
  const colorClasses = {
    blue: "bg-blue-500 text-white hover:bg-blue-600 shadow-[0_0_15px_rgba(59,130,246,0.5)] hover:shadow-[0_0_25px_rgba(59,130,246,0.8)]",
    green:
      "bg-green-500 text-white hover:bg-green-600 shadow-[0_0_15px_rgba(34,197,94,0.5)] hover:shadow-[0_0_25px_rgba(34,197,94,0.8)]",
    pink: "bg-pink-500 text-white hover:bg-pink-600 shadow-[0_0_15px_rgba(236,72,153,0.5)] hover:shadow-[0_0_25px_rgba(236,72,153,0.8)]",
    purple:
      "bg-purple-500 text-white hover:bg-purple-600 shadow-[0_0_15px_rgba(168,85,247,0.5)] hover:shadow-[0_0_25px_rgba(168,85,247,0.8)]",
  }

  const buttonClasses = `${baseClasses} ${colorClasses[color]}`

  if (href) {
    return (
      <a href={href} className={buttonClasses}>
        {children}
      </a>
    )
  }

  return (
    <button className={buttonClasses} onClick={onClick}>
      {children}
    </button>
  )
}

export default NeonButton
