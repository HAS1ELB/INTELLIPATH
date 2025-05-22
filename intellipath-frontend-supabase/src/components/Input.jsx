export default function Input({
  type = 'text',
  label,
  name,
  value,
  onChange,
  placeholder = '',
  error = '',
  required = false,
  disabled = false,
  className = '',
  min,
  max,
  autoComplete = 'on'
}) {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        min={min}
        max={max}
        autoComplete={autoComplete}
        className={`w-full px-3 py-2 border ${
          error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
        } rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white ${
          disabled ? 'bg-gray-100 dark:bg-gray-800 cursor-not-allowed' : ''
        }`}
      />
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  );
}