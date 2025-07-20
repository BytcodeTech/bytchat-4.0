import { type ClassValue, clsx } from "clsx"; 
import { twMerge } from "tailwind-merge"; 

export function cn(...inputs: ClassValue[]) { 
  return twMerge(clsx(inputs)); 
}

export function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num);
}
