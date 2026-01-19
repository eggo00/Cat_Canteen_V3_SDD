/**
 * CheckoutForm component
 * Form for collecting customer information during checkout
 */

import React, { useState } from 'react';

/**
 * Customer info form data
 */
export interface CustomerFormData {
  customerName: string;
  customerPhone: string;
  customerEmail?: string;
  notes?: string;
}

/**
 * CheckoutForm props
 */
interface CheckoutFormProps {
  /** Submit handler */
  onSubmit: (data: CustomerFormData) => void;
  /** Loading state */
  isLoading?: boolean;
  /** Error message */
  error?: string | null;
  /** Cancel handler */
  onCancel?: () => void;
}

/**
 * Validate Taiwan mobile phone number
 */
function validatePhone(phone: string): boolean {
  // Taiwan mobile: 09XXXXXXXX
  const cleaned = phone.replace(/[\s-]/g, '');
  return /^09\d{8}$/.test(cleaned);
}

/**
 * Validate email format
 */
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * CheckoutForm component
 */
export function CheckoutForm({
  onSubmit,
  isLoading = false,
  error,
  onCancel,
}: CheckoutFormProps): JSX.Element {
  const [formData, setFormData] = useState<CustomerFormData>({
    customerName: '',
    customerPhone: '',
    customerEmail: '',
    notes: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user types
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customerName.trim()) {
      newErrors.customerName = '請輸入姓名';
    }

    if (!formData.customerPhone.trim()) {
      newErrors.customerPhone = '請輸入手機號碼';
    } else if (!validatePhone(formData.customerPhone)) {
      newErrors.customerPhone = '請輸入有效的手機號碼 (09XXXXXXXX)';
    }

    if (formData.customerEmail && !validateEmail(formData.customerEmail)) {
      newErrors.customerEmail = '請輸入有效的電子郵件';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({
        ...formData,
        customerPhone: formData.customerPhone.replace(/[\s-]/g, ''),
        customerEmail: formData.customerEmail || undefined,
        notes: formData.notes || undefined,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Error banner */}
      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          <p className="font-medium">訂單提交失敗</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Customer name */}
      <div>
        <label
          htmlFor="customerName"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          姓名 <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="customerName"
          name="customerName"
          value={formData.customerName}
          onChange={handleChange}
          className={`w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-opacity-50 ${
            errors.customerName
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="請輸入姓名"
          disabled={isLoading}
        />
        {errors.customerName && (
          <p className="mt-1 text-sm text-red-500">{errors.customerName}</p>
        )}
      </div>

      {/* Phone number */}
      <div>
        <label
          htmlFor="customerPhone"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          手機號碼 <span className="text-red-500">*</span>
        </label>
        <input
          type="tel"
          id="customerPhone"
          name="customerPhone"
          value={formData.customerPhone}
          onChange={handleChange}
          className={`w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-opacity-50 ${
            errors.customerPhone
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="09XXXXXXXX"
          disabled={isLoading}
        />
        {errors.customerPhone && (
          <p className="mt-1 text-sm text-red-500">{errors.customerPhone}</p>
        )}
      </div>

      {/* Email (optional) */}
      <div>
        <label
          htmlFor="customerEmail"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          電子郵件 <span className="text-gray-400">(選填)</span>
        </label>
        <input
          type="email"
          id="customerEmail"
          name="customerEmail"
          value={formData.customerEmail}
          onChange={handleChange}
          className={`w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-opacity-50 ${
            errors.customerEmail
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="example@email.com"
          disabled={isLoading}
        />
        {errors.customerEmail && (
          <p className="mt-1 text-sm text-red-500">{errors.customerEmail}</p>
        )}
      </div>

      {/* Notes (optional) */}
      <div>
        <label
          htmlFor="notes"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          備註 <span className="text-gray-400">(選填)</span>
        </label>
        <textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="w-full resize-none rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          placeholder="特殊需求或備註..."
          disabled={isLoading}
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-lg border border-gray-300 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
            disabled={isLoading}
          >
            返回
          </button>
        )}
        <button
          type="submit"
          className="flex-1 rounded-lg py-3 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              處理中...
            </span>
          ) : (
            '確認送出'
          )}
        </button>
      </div>
    </form>
  );
}

export default CheckoutForm;
