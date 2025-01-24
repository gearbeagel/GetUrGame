import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const SteamCallback = ({ setIsAuthenticated }) => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(location.search);

      try {
        const response = await fetch(`http://localhost:8000/api/steam/callback/?${urlParams.toString()}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          console.log("Login successful:", data);
          setIsAuthenticated(true); // Update authentication state
          navigate('/');  // Redirect to the homepage
        } else {
          console.error("Login failed:", response.statusText);
          navigate('/');  // Redirect to the homepage on error
        }
      } catch (error) {
        console.error("Error during Steam callback:", error);
        navigate('/');  // Redirect to the homepage on error
      }
    };

    handleCallback();
  }, [location, navigate, setIsAuthenticated]);

  return <div>Processing Steam login...</div>;
};

export default SteamCallback;