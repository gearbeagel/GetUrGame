import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const SteamCallback = ({ setIsAuthenticated, setUsername }) => {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const handleSteamCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const response = await axios.get(
          `http://127.0.0.1:8000/api/steam/callback/?${urlParams.toString()}`,
          {
            withCredentials: true,
          }
        );
        console.log(response)

        if (response.status === 200 && response.data.steam_id && response.data.username) {
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
        <p>Loading...</p>
      ) : (
        <p>Authentication failed or completed successfully. You will be redirected.</p>
      )}
    </div>
  );
};

export default SteamCallback;
