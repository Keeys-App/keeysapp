import { Fragment, type FC } from 'react';
import { Outlet } from 'react-router-dom';
import { AppSidebar } from './AppSidebar';
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { useBreadcrumbs } from '@/contexts';

export const Layout: FC = () => {
  const { breadcrumbs } = useBreadcrumbs();

  const getBreadcrumbs = () => {
    if (breadcrumbs.length === 0) {
      return (
        <BreadcrumbItem>
          <BreadcrumbPage>Dashboard</BreadcrumbPage>
        </BreadcrumbItem>
      );
    }

    return breadcrumbs.map((item, index) => {
      const isLast = index === breadcrumbs.length - 1;

      return (
        <Fragment key={`breadcrumb-${index}`}>
          {index > 0 ? <BreadcrumbSeparator className="hidden md:block" /> : null}
          <BreadcrumbItem className={index > 0 ? 'hidden md:block' : ''}>
            {isLast || !item.href ? (
              <BreadcrumbPage>{item.label}</BreadcrumbPage>
            ) : (
              <BreadcrumbLink href={item.href}>{item.label}</BreadcrumbLink>
            )}
          </BreadcrumbItem>
        </Fragment>
      );
    });
  };

  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>
        <header className="bg-background sticky top-0 flex shrink-0 items-center gap-2 border-b px-4 py-3.5">
          {/* <SidebarTrigger className="-ml-1" /> */}
          {/* <Separator orientation="vertical" className="mr-2 h-4" /> */}
          <Breadcrumb>
            <BreadcrumbList>{getBreadcrumbs()}</BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex flex-1 flex-col">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
};
