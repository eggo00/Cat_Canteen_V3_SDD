/**
 * DateRangePicker component
 * Quick date range selection for analytics
 */


interface DateRangePickerProps {
  days: number;
  onDaysChange: (days: number) => void;
  className?: string;
}

const PRESET_RANGES = [
  { label: '今日', days: 1 },
  { label: '7 天', days: 7 },
  { label: '30 天', days: 30 },
  { label: '90 天', days: 90 },
];

/**
 * DateRangePicker component
 */
export function DateRangePicker({
  days,
  onDaysChange,
  className = '',
}: DateRangePickerProps): JSX.Element {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-sm text-gray-500">時間範圍：</span>
      <div className="flex rounded-lg border border-gray-200 overflow-hidden">
        {PRESET_RANGES.map((range) => (
          <button
            key={range.days}
            onClick={() => onDaysChange(range.days)}
            className={`px-3 py-1.5 text-sm font-medium transition-colors ${
              days === range.days
                ? 'text-white'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
            style={
              days === range.days
                ? { backgroundColor: 'var(--color-primary, #FF6B6B)' }
                : undefined
            }
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default DateRangePicker;
