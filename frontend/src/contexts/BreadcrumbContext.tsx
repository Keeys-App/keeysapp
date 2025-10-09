import { createContext, useContext, useState, type FC, type ReactNode } from 'react';

/**
 * Breadcrumb item interface
 */
export interface BreadcrumbItem {
  label: string;
  href?: string;
}

/**
 * Breadcrumb context interface
 */
interface BreadcrumbContextType {
  breadcrumbs: BreadcrumbItem[];
  setBreadcrumbs: (breadcrumbs: BreadcrumbItem[]) => void;
}

/**
 * Breadcrumb context
 */
const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined);

/**
 * Breadcrumb provider props
 */
interface BreadcrumbProviderProps {
  children: ReactNode;
}

/**
 * Breadcrumb provider component
 */
export const BreadcrumbProvider: FC<BreadcrumbProviderProps> = ({ children }) => {
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);

  return (
    <BreadcrumbContext.Provider value={{ breadcrumbs, setBreadcrumbs }}>
      {children}
    </BreadcrumbContext.Provider>
  );
};

/**
 * Hook to use breadcrumb context
 */
export const useBreadcrumbs = () => {
  const context = useContext(BreadcrumbContext);
  if (!context) {
    throw new Error('useBreadcrumbs must be used within BreadcrumbProvider');
  }
  return context;
};

