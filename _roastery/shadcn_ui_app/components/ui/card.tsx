import * as React from "react"

// A utility function to concatenate class names (handles falsy values as well)
const cn = (...classes: (string | undefined | false)[]) => classes.filter(Boolean).join(' ')

// Card component
const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-xl border bg-card text-card-foreground shadow",
      className
    )}
    {...props}
  >
    {children}
  </div>
))
Card.displayName = "Card"

// CardHeader component
const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  >
    {children}
  </div>
))
CardHeader.displayName = "CardHeader"

// CardTitle component
const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  >
    {children}
  </h3>
))
CardTitle.displayName = "CardTitle"

// CardDescription component
const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(({ className, children, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  >
    {children}
  </p>
))
CardDescription.displayName = "CardDescription"

// CardContent component
const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props}>
    {children}
  </div>
))
CardContent.displayName = "CardContent"

// CardFooter component
const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  >
    {children}
  </div>
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
