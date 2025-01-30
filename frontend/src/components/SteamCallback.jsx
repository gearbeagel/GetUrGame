import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { FaSpinner } from "react-icons/fa";

const SteamCallback = ({ setIsAuthenticated, setUsername }) => {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const getRandomColor = () => {
    const colors = ["blue", "purple", "green", "pink"];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  useEffect(() => {
    const handleSteamCallback = async () => {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const response = await axios.get(
          `${baseUrl}/api/steam/callback/?${urlParams.toString()}`,
          {
            withCredentials: true,
          }
        );
        console.log(response);

        if (
          response.status === 200 &&
          response.data.steam_id &&
          response.data.username
        ) {
          setIsAuthenticated(true);
          setUsername(response.data.username);
          navigate("/");
        } else {
          setLoading(false);
        }
      } catch (error) {
        console.error("Error during Steam callback:", error);
        setLoading(false);
      }
    };

    handleSteamCallback();
  }, [setIsAuthenticated, setUsername, navigate]);

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      {loading ? (
        <div className="text-center">
          <FaSpinner
            className={`animate-spin text-${getRandomColor()}-500 text-4xl mx-auto`}
          />
        </div>
      ) : (
        <p>
          Authentication failed or completed successfully. You will be
          redirected.
        </p>
      )}
    </div>
  );
};

export default SteamCallback;
