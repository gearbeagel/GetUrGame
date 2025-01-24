import React, { useState, useEffect } from "react";
import "./App.css";
import Homepage from "./components/Homepage";
import SteamCallback from "./components/SteamCallback";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState(null);

  const checkUserAuth = async () => {
    try {
      const response = await fetch("/api/misc/check-auth/", {
        method: "GET",
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setIsAuthenticated(data.isAuthenticated);
        setUsername(data.username);
        console.log(username)
        return data.isAuthenticated;
      }
    } catch (error) {
      console.error("Error checking auth status:", error);
    }
    return false;
  };

  useEffect(() => {
    checkUserAuth();
  }, []);

  return (
    <>
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
            element={
              <SteamCallback
                setIsAuthenticated={setIsAuthenticated}
                setUsername={setUsername}
              />
            }
          />
        </Routes>
      </Router>
    </>
  );
}

export default App;
