import { Navigate } from "react-router-dom";
import jwtDecode from "jwt-decode"; // Correct import statement
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import { useState, useEffect } from "react";

function ProtectedRoute({ children }) {
  const [isAuthorized, setIsAuthorized] = useState(null);

  // Check user's authentication status
  useEffect(() => {
    auth().catch(() => setIsAuthorized(false));
  }, []);

  // Refresh AccessToken
  const refreshToken = async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN);
    try {
      const res = await api.post("/api/token/refresh/", {
        refresh: refreshToken, // Send refresh token to backend
      });
      if (res.status === 200) {
        localStorage.setItem(ACCESS_TOKEN, res.data.access); // Store new access token
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
    } catch (error) {
      console.log(error);
      setIsAuthorized(false);
    }
  };

  // Check AccessToken & Expiration Time
  const auth = async () => {
    const token = localStorage.getItem(ACCESS_TOKEN);

    if (!token) {
      setIsAuthorized(false);
      return;
    }

    const decoded = jwtDecode(token); // Decode JWT token
    const tokenExpiration = decoded.exp; // Get token expiration time
    const now = Date.now() / 1000; // Current time in seconds

    if (tokenExpiration < now) {
      await refreshToken(); // Refresh token if expired
    } else {
      setIsAuthorized(true); // Set authorized if token is valid
    }
  };

  if (isAuthorized === null) {
    return <div>Loading...</div>; // Show loading indicator while checking auth status
  }

  return isAuthorized ? children : <Navigate to="/login" />; // Redirect to login if not authorized
}

export default ProtectedRoute;
