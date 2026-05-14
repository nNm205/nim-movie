import { Navigate, useLocation } from "react-router-dom";
import { authService } from "../../services/authService";

const PrivateRoute = ({ children }) => {
  const location = useLocation();

  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
};

export default PrivateRoute;
