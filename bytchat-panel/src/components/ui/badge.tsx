import React, { ReactNode } from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  className?: string;
}

export const Badge = ({ children, className = '', ...props }: BadgeProps) => (
  <span
    className={`inline-block px-2 py-1 text-xs font-semibold rounded bg-gray-200 text-gray-800 ${className}`}
    {...props}
  >
    {children}
  </span>
);

export default Badge; 