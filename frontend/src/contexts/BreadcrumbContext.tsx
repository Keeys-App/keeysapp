import { createContext, useContext, useState, useMemo, useCallback, type FC, type ReactNode } from 'react';

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
  const [breadcrumbs, setBreadcrumbsState] = useState<BreadcrumbItem[]>([]);

  // Memoize setBreadcrumbs to prevent useEffect loops
  const setBreadcrumbs = useCallback((newBreadcrumbs: BreadcrumbItem[]) => {
    setBreadcrumbsState(newBreadcrumbs);
  }, []);

  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(() => {
    return { breadcrumbs, setBreadcrumbs };
  }, [breadcrumbs, setBreadcrumbs]);

  return (
    <BreadcrumbContext.Provider value={value}>
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

