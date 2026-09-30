import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import DashboardPage from "./pages/Dashboard";
import CaseListPage from "./pages/CaseList";
import CaseNewPage from "./pages/CaseNew";
import CaseDetailPage from "./pages/CaseDetail";
import ProtectedRoute from "./components/ProtectedRoute";
import { ToastProvider } from "./components/ui/Toast";

export default function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cases"
            element={
              <ProtectedRoute>
                <CaseListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cases/new"
            element={
              <ProtectedRoute>
                <CaseNewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cases/:id"
            element={
              <ProtectedRoute>
                <CaseDetailPage />
              </ProtectedRoute>
            }
          />
          {/* Phase 3+ will add /coordinator/*, /admin/* */}
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}
