import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
        destructive:
          "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        purple:
          "border-transparent bg-purple-600 text-white [a&]:hover:bg-purple-600/90 focus-visible:ring-purple-600/20 dark:focus-visible:ring-purple-600/40 dark:bg-purple-600/60",
        orange:
          "border-transparent bg-orange-600 text-white [a&]:hover:bg-orange-600/90 focus-visible:ring-orange-600/20 dark:focus-visible:ring-orange-600/40 dark:bg-orange-600/60",
        green:
          "border-transparent bg-green-600 text-white [a&]:hover:bg-green-600/90 focus-visible:ring-green-600/20 dark:focus-visible:ring-green-600/40 dark:bg-green-600/60",
        blue: "border-transparent bg-blue-600 text-white [a&]:hover:bg-blue-600/90 focus-visible:ring-blue-600/20 dark:focus-visible:ring-blue-600/40 dark:bg-blue-600/60",
        pink: "border-transparent bg-pink-600 text-white [a&]:hover:bg-pink-600/90 focus-visible:ring-pink-600/20 dark:focus-visible:ring-pink-600/40 dark:bg-pink-600/60",
        gray: "border-transparent bg-gray-600 text-white [a&]:hover:bg-gray-600/90 focus-visible:ring-gray-600/20 dark:focus-visible:ring-gray-600/40 dark:bg-gray-600/60",
        teal: "border-transparent bg-teal-600 text-white [a&]:hover:bg-teal-600/90 focus-visible:ring-teal-600/20 dark:focus-visible:ring-teal-600/40 dark:bg-teal-600/60",
        indigo:
          "border-transparent bg-indigo-600 text-white [a&]:hover:bg-indigo-600/90 focus-visible:ring-indigo-600/20 dark:focus-visible:ring-indigo-600/40 dark:bg-indigo-600/60",
        yellow:
          "border-transparent bg-yellow-600 text-white [a&]:hover:bg-yellow-600/90 focus-visible:ring-yellow-600/20 dark:focus-visible:ring-yellow-600/40 dark:bg-yellow-600/60",
        lime: "border-transparent bg-lime-600 text-white [a&]:hover:bg-lime-600/90 focus-visible:ring-lime-600/20 dark:focus-visible:ring-lime-600/40 dark:bg-lime-600/60",
        cyan: "border-transparent bg-cyan-600 text-white [a&]:hover:bg-cyan-600/90 focus-visible:ring-cyan-600/20 dark:focus-visible:ring-cyan-600/40 dark:bg-cyan-600/60",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span";

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  );
}

export { Badge, badgeVariants };
