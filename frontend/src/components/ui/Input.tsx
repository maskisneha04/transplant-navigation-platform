import { type InputHTMLAttributes, forwardRef, useId } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helpText?: string;
  required?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helpText, required, id, className = "", ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const helpId = helpText ? `${inputId}-help` : undefined;
    const errorId = error ? `${inputId}-error` : undefined;

    return (
      <div>
        <label htmlFor={inputId} className="block text-sm font-medium text-slate-700 mb-1.5">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
          {!required && <span className="text-slate-400 font-normal ml-1">(optional)</span>}
        </label>
        <input
          ref={ref}
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={[helpId, errorId].filter(Boolean).join(" ") || undefined}
          className={`w-full rounded-lg border px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
            disabled:bg-slate-50 disabled:text-slate-500
            ${error ? "border-red-300" : "border-slate-300"} ${className}`}
          {...props}
        />
        {helpText && !error && (
          <p id={helpId} className="mt-1.5 text-xs text-slate-500">
            {helpText}
          </p>
        )}
        {error && (
          <p id={errorId} className="mt-1.5 text-xs text-red-600">
            {error}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";

export default Input;
