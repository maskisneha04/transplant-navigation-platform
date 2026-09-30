import { useState, type FormEvent } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { login, extractErrorMessage } from "../services/authService";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const justRegistered = Boolean((location.state as { justRegistered?: boolean })?.justRegistered);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">
          <div className="flex items-center gap-2 mb-8">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white font-semibold text-sm">
              T
            </span>
            <span className="font-semibold text-slate-900 text-sm">Transplant Navigation Platform</span>
          </div>

          <h1 className="text-2xl font-semibold text-slate-900 mb-1">Sign in</h1>
          <p className="text-sm text-slate-500 mb-8">
            Coordination support for transplant-related administrative and document workflows.
          </p>

          {justRegistered && (
            <div className="rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm px-3 py-2 mb-4">
              Account created. You can sign in now.
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <Input
              label="Email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-[34px] text-xs text-slate-500 hover:text-slate-700 font-medium"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>

            {error && (
              <div role="alert" className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">
                {error}
              </div>
            )}

            <Button type="submit" isLoading={submitting} className="w-full justify-center">
              Sign in
            </Button>
          </form>

          <p className="text-sm text-slate-500 mt-6 text-center">
            Need an account?{" "}
            <Link to="/register" className="text-brand-600 font-medium hover:underline">
              Register
            </Link>
          </p>

          <div className="mt-8 pt-5 border-t border-slate-200 text-xs text-slate-400 text-center">
            Academic/research prototype. Not a clinical decision-making system.
          </div>
        </div>
      </div>
    </div>
  );
}
