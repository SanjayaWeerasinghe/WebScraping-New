import { Link, useLocation } from "react-router-dom";
import { Home, Database, TrendingUp, Palette } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/scraping", label: "Web Scraping", icon: Database },
  { path: "/price-analysis", label: "Price Analysis", icon: TrendingUp },
  { path: "/color-trends", label: "Color Trends", icon: Palette },
];

export const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-primary" />
            <span className="font-bold text-xl">ScrapeVision</span>
          </div>
          
          <div className="flex gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-md"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};
