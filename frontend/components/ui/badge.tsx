import { cn } from "@/lib/utils"

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "destructive" | "outline"
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        {
          "bg-primary text-primary-foreground": variant === "default",
          "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100": variant === "success",
          "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100": variant === "destructive",
          "border border-input": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}
