import { Navigate } from "react-router-dom";
import { isLoggedIn } from "../services/authService";

// This guard is a UX convenience only (avoids flashing a protected page).
// It is NEVER the real security boundary — every backend endpoint independently
// verifies the JWT and role, per the project's RBAC architecture.
export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
