"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Search,
    MessageSquare,
    History,
    User,
    Menu,
    Scale
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useState } from "react";

const sidebarItems = [
    { icon: Search, label: "Search Judgments", href: "/dashboard/search" },
    { icon: MessageSquare, label: "AI Lawyer Chat", href: "/dashboard/chat" },
    { icon: History, label: "History", href: "/dashboard/history" },
];

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Desktop Sidebar */}
            <aside className="hidden md:flex w-64 flex-col bg-slate-900 text-white fixed h-full z-10">
                <div className="p-6 border-b border-slate-800 flex items-center gap-2">
                    <Scale className="h-6 w-6 text-blue-400" />
                    <span className="font-bold text-xl">LexQuery</span>
                </div>

                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    {sidebarItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                                    isActive
                                        ? "bg-blue-600 text-white"
                                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                                )}
                            >
                                <item.icon className="h-5 w-5" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-slate-800">
                    <div className="px-4 py-2 text-sm text-slate-400">
                        Public Access Mode
                    </div>
                </div>
            </aside>

            {/* Mobile Sidebar (Sheet) */}
            <div className="md:hidden fixed top-4 left-4 z-50">
                <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                    <SheetTrigger asChild>
                        <Button variant="outline" size="icon" className="bg-slate-900 text-white border-none hover:bg-slate-800">
                            <Menu className="h-6 w-6" />
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="w-64 bg-slate-900 text-white border-r-slate-800 p-0">
                        <div className="p-6 border-b border-slate-800 flex items-center gap-2">
                            <Scale className="h-6 w-6 text-blue-400" />
                            <span className="font-bold text-xl">LexQuery</span>
                        </div>
                        <nav className="p-4 space-y-2">
                            {sidebarItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={cn(
                                        "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                                        pathname === item.href
                                            ? "bg-blue-600 text-white"
                                            : "text-slate-300 hover:bg-slate-800 hover:text-white"
                                    )}
                                >
                                    <item.icon className="h-5 w-5" />
                                    <span>{item.label}</span>
                                </Link>
                            ))}
                        </nav>
                    </SheetContent>
                </Sheet>
            </div>

            {/* Main Content */}
            <main className="flex-1 md:ml-64 p-4 md:p-8 pt-16 md:pt-8 w-full">
                <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
                    {children}
                </div>
            </main>
        </div>
    );
}
