import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

/**
 * Reusable Input component with label, error, and icon support.
 *
 * Usage:
 * ```tsx
 * <Input
 *   label="Email"
 *   type="email"
 *   error={errors.email}
 *   placeholder="Enter your email"
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      hint,
      leftIcon,
      rightIcon,
      fullWidth = true,
      className = '',
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${label?.toLowerCase().replace(/\s/g, '-')}`;

    const baseInputStyles =
      'block rounded-lg border bg-white px-4 py-2.5 text-gray-900 placeholder-gray-400 transition-colors focus:outline-none focus:ring-2';

    const normalStyles =
      'border-gray-300 focus:border-primary focus:ring-primary/50';

    const errorStyles =
      'border-red-500 focus:border-red-500 focus:ring-red-500/50';

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1.5"
          >
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={`
              ${baseInputStyles}
              ${error ? errorStyles : normalStyles}
              ${leftIcon ? 'pl-10' : ''}
              ${rightIcon ? 'pr-10' : ''}
              ${fullWidth ? 'w-full' : ''}
              ${className}
            `}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={error ? `${inputId}-error` : undefined}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-red-600">
            {error}
          </p>
        )}
        {hint && !error && (
          <p className="mt-1.5 text-sm text-gray-500">{hint}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
