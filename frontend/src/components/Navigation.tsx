"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Users, Sparkles } from "lucide-react";

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { name: "Discover", href: "/", icon: Compass },
    { name: "CRM Directory", href: "/crm", icon: Users },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-card-border glass py-4 px-6 md:px-12 flex justify-between items-center">
      <Link href="/" className="flex items-center space-x-2 text-xl font-bold tracking-tight">
        <Sparkles className="h-6 w-6 text-primary animate-pulse" />
        <span className="gradient-text font-extrabold">InfluenceAgent</span>
      </Link>
      
      <div className="flex items-center space-x-6">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-2 text-sm font-medium transition-all duration-300 px-3 py-2 rounded-lg ${
                isActive
                  ? "bg-primary/20 text-indigo-300 border border-primary/30"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
