import { DesktopNav, MobileNav } from "@/components/layout/nav";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <DesktopNav />
      <MobileNav />
      <main className="md:ml-56 pb-20 md:pb-0">
        {children}
      </main>
    </div>
  );
}
