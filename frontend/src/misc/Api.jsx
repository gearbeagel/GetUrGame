import axios from "axios";

export const getCsrfToken = async () => {
  try {
    const response = await axios.get("http://127.0.0.1:8000/api/csrf/", {
      withCredentials: true, // Ensure cookies are included
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
        "http://127.0.0.1:8000/api/steam/logout/",
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status === 200) {
        console.log("Logout successful!")
        navigate(`/`);
        window.location.reload();
      } else {
        console.error("Logout failed:", response.statusText);
      }
    } catch (error) {
      console.error("Error during Steam logout:", error);
    }
  };
