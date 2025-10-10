import { type ComponentProps } from "react"
import { useTheme } from "@/contexts/ThemeContext"
import { Toaster as Sonner } from "sonner"

type ToasterProps = ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      position="bottom-right"
      richColors
      toastOptions={{
        classNames: {
          toast: "group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-muted-foreground",
          actionButton: "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
          cancelButton: "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
          success: "group-[.toast]:text-green-600 dark:group-[.toast]:text-green-400",
          error: "group-[.toast]:text-red-600 dark:group-[.toast]:text-red-400",
          info: "group-[.toast]:text-blue-600 dark:group-[.toast]:text-blue-400",
          warning: "group-[.toast]:text-yellow-600 dark:group-[.toast]:text-yellow-400",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
