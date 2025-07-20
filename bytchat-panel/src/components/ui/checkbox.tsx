import * as React from "react"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

interface CheckboxProps {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
  className?: string
  id?: string
  disabled?: boolean
}

const Checkbox = React.forwardRef<
  HTMLDivElement,
  CheckboxProps
>(({ className, checked, onCheckedChange, disabled, ...props }, ref) => {
  const handleClick = () => {
    if (!disabled && onCheckedChange) {
      onCheckedChange(!checked)
    }
  }
  
  return (
    <div
      ref={ref}
      onClick={handleClick}
      className={cn(
        "h-4 w-4 shrink-0 rounded-sm border flex items-center justify-center cursor-pointer transition-all duration-200",
        checked 
          ? "bg-blue-600 border-blue-600 text-white" 
          : "bg-white border-gray-300 hover:border-blue-400",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
      {...props}
    >
      {checked && <Check className="h-3 w-3" />}
    </div>
  )
})
Checkbox.displayName = "Checkbox"

export { Checkbox } 