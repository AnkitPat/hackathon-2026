import React from 'react';

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

export const CampsiteDetailSection: React.FC<SectionProps> = ({ title, children }) => {
  return (
    <div className="mb-6 p-4 border border-gray-200 rounded-lg shadow-sm bg-white">
      <h2 className="text-2xl font-semibold mb-3 text-gray-700">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {children}
      </div>
    </div>
  );
};

interface FacilityItemProps {
  label: string;
  value: string | number | boolean | string[] | null | undefined;
  isBoolean?: boolean;
  isList?: boolean;
}

export const FacilityItem: React.FC<FacilityItemProps> = ({ label, value, isBoolean, isList }) => {
  let displayValue: React.ReactNode;

  if (isBoolean) {
    displayValue = value ? (
      <span className="text-green-600 font-bold">Yes</span>
    ) : (
      <span className="text-red-600 font-bold">No</span>
    );
  } else if (isList && Array.isArray(value)) {
    displayValue = (
      <ul className="list-disc list-inside">
        {value.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    );
  } else {
    displayValue = String(value);
  }

  return (
    <div className="flex items-center justify-between py-1 border-b border-gray-50 last:border-0">
      <span className="text-gray-600">{label}:</span>
      <span className="font-medium text-gray-800">{displayValue}</span>
    </div>
  );
};
