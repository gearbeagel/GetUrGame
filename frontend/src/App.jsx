import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import axios from "axios";
import Homepage from "./components/Homepage";
import SteamCallback from "./components/SteamCallback";
import GamesPage from "./components/UserGames";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState(null);

  useEffect(() => {
    const checkAuthFromBackend = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/misc/check-auth/", {
          withCredentials: true,
        });

        if (response.data.isAuthenticated) {
          setIsAuthenticated(response.data.isAuthenticated);
          setUsername(response.data.username);
        } else {
          setIsAuthenticated(false);
          setUsername(null);
        }
      } catch (error) {
        console.error("Error checking auth status:", error);
      }
    };

    checkAuthFromBackend();
  }, []);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <Homepage
              isAuthenticated={isAuthenticated}
              setIsAuthenticated={setIsAuthenticated}
              username={username}
            />
          }
        />
        <Route
          path="/steam/callback"
          element={<SteamCallback setIsAuthenticated={setIsAuthenticated} setUsername={setUsername} />}
        />
        <Route
          path="/games"
          element={<GamesPage />}
        />
      </Routes>
    </Router>
  );
}

export default App;
