import React from "react"

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface AlertDescriptionProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const Alert: React.FC<AlertProps> = ({ className = "", children, ...props }) => (
  <div
    role="alert"
    className={`relative w-full rounded-lg border p-4 bg-orange-50 border-orange-200 text-orange-800 ${className}`}
    {...props}
  >
    {children}
  </div>
)

const AlertDescription: React.FC<AlertDescriptionProps> = ({ className = "", children, ...props }) => (
  <div
    className={`text-sm ${className}`}
    {...props}
  >
    {children}
  </div>
)

export { Alert, AlertDescription } 