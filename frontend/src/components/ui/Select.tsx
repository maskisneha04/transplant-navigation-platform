import { type SelectHTMLAttributes, forwardRef, useId } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  error?: string;
  helpText?: string;
  required?: boolean;
  options: { value: string; label: string }[];
  placeholder?: string;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helpText, required, options, placeholder, id, className = "", ...props }, ref) => {
    const generatedId = useId();
    const selectId = id ?? generatedId;

    return (
      <div>
        <label htmlFor={selectId} className="block text-sm font-medium text-slate-700 mb-1.5">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
          {!required && <span className="text-slate-400 font-normal ml-1">(optional)</span>}
        </label>
        <select
          ref={ref}
          id={selectId}
          aria-invalid={Boolean(error)}
          className={`w-full rounded-lg border px-3 py-2.5 text-sm text-slate-900 bg-white
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
            ${error ? "border-red-300" : "border-slate-300"} ${className}`}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {helpText && !error && <p className="mt-1.5 text-xs text-slate-500">{helpText}</p>}
        {error && <p className="mt-1.5 text-xs text-red-600">{error}</p>}
      </div>
    );
  }
);
Select.displayName = "Select";

export default Select;
