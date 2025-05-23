import axios from "axios";
import { useNavigate } from "react-router-dom";


export const apiUrl = import.meta.env.VITE_API_URL;

export const getCsrfToken = async () => {
  try {
    const response = await axios.get(`${apiUrl}/csrf/`, {
      withCredentials: true,
    });
    const csrfToken = response.data.csrfToken;
    console.log("CSRF Token fetched:", csrfToken);
    return csrfToken;
  } catch (error) {
    console.error("Error fetching CSRF token:", error);
    return null;
  }
};

export const handleSteamLogout = async () => {
    try {

      const response = await axios.get(
        `${apiUrl}/steam/logout/`,
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status === 200) {
        console.log("Logout successful!");
        window.location.href = "/";
        window.location.reload();
      } else {
        console.error("Logout failed:", response.statusText);
      }
    } catch (error) {
      console.error("Error during Steam logout:", error);
    }
  };
