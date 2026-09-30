import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, extractErrorMessage } from "../services/authService";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";

function getPasswordIssues(password: string): string[] {
  const issues: string[] = [];
  if (password.length > 0 && password.length < 8) issues.push("At least 8 characters");
  return issues;
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const passwordIssues = getPasswordIssues(password);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setSubmitting(true);
    try {
      await register(email, password);
      navigate("/login", { state: { justRegistered: true } });
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

          <h1 className="text-2xl font-semibold text-slate-900 mb-1">Create a patient account</h1>
          <p className="text-sm text-slate-500 mb-8">
            This is a research/academic prototype. Please do not enter real personal information.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <Input
              label="Email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                helpText="Minimum 8 characters."
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

            {passwordIssues.length > 0 && (
              <ul className="text-xs text-amber-600 space-y-0.5" aria-live="polite">
                {passwordIssues.map((issue) => (
                  <li key={issue}>• {issue}</li>
                ))}
              </ul>
            )}

            {error && (
              <div role="alert" className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">
                {error}
              </div>
            )}

            <Button type="submit" isLoading={submitting} className="w-full justify-center">
              Create account
            </Button>
          </form>

          <p className="text-sm text-slate-500 mt-6 text-center">
            Already have an account?{" "}
            <Link to="/login" className="text-brand-600 font-medium hover:underline">
              Log in
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
