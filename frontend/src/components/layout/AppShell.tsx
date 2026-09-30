import { type ReactNode, useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { logout, me } from "../../services/authService";
import type { AuthUser } from "../../types/auth";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Overview" },
  { to: "/cases", label: "My Cases" },
];

export default function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    me().then(setUser).catch(() => {});
  }, []);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:bg-white focus:px-3 focus:py-2 focus:rounded-md focus:shadow"
      >
        Skip to content
      </a>

      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/dashboard" className="flex items-center gap-2">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white font-semibold text-sm">
                T
              </span>
              <span className="font-semibold text-slate-900 text-sm hidden sm:inline">
                Transplant Navigation Platform
              </span>
            </Link>

            <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">
              {NAV_ITEMS.map((item) => {
                const active = location.pathname.startsWith(item.to);
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      active ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {user && (
              <span className="hidden sm:inline text-xs text-slate-500">
                {user.email} · <span className="capitalize">{user.role.replace("_", " ")}</span>
              </span>
            )}
            <button
              onClick={handleLogout}
              className="text-sm text-slate-500 hover:text-slate-800 font-medium px-3 py-2 rounded-lg hover:bg-slate-100"
            >
              Log out
            </button>
            <button
              className="md:hidden p-2 rounded-lg hover:bg-slate-100"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label="Toggle menu"
              aria-expanded={menuOpen}
            >
              <svg className="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {menuOpen && (
          <nav className="md:hidden border-t border-slate-200 px-4 py-2 space-y-1" aria-label="Main navigation">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setMenuOpen(false)}
                className="block px-3 py-2 text-sm font-medium rounded-lg text-slate-600 hover:bg-slate-100"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        )}
      </header>

      <main id="main-content" className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {children}
      </main>
    </div>
  );
}
