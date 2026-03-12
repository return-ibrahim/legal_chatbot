"use client";

import { useEffect, useState } from "react";
import { authService } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Search, MessageSquare, FileText, TrendingUp } from "lucide-react";

export default function DashboardPage() {
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const userData = authService.getUser();
        setUser(userData);
    }, []);

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">
                    Welcome back, {user?.username || "User"}!
                </h1>
                <p className="text-gray-600 mt-2">
                    Your AI-powered legal research dashboard
                </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-gray-600">
                            Total Searches
                        </CardTitle>
                        <Search className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-gray-900">0</div>
                        <p className="text-xs text-gray-500 mt-1">Start searching now</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-gray-600">
                            AI Conversations
                        </CardTitle>
                        <MessageSquare className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-gray-900">0</div>
                        <p className="text-xs text-gray-500 mt-1">Chat with AI lawyer</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-gray-600">
                            Cases Reviewed
                        </CardTitle>
                        <FileText className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-gray-900">0</div>
                        <p className="text-xs text-gray-500 mt-1">View case history</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-gray-600">
                            Accuracy Rate
                        </CardTitle>
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-gray-900">98%</div>
                        <p className="text-xs text-gray-500 mt-1">AI model accuracy</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            <a
                                href="/dashboard/search"
                                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
                            >
                                <div className="flex items-center gap-3">
                                    <Search className="h-5 w-5 text-blue-600" />
                                    <div>
                                        <div className="font-medium text-gray-900">Search Judgments</div>
                                        <div className="text-sm text-gray-500">Find relevant court cases</div>
                                    </div>
                                </div>
                            </a>

                            <a
                                href="/dashboard/chat"
                                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
                            >
                                <div className="flex items-center gap-3">
                                    <MessageSquare className="h-5 w-5 text-blue-600" />
                                    <div>
                                        <div className="font-medium text-gray-900">Ask AI Lawyer</div>
                                        <div className="text-sm text-gray-500">Get legal explanations</div>
                                    </div>
                                </div>
                            </a>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Getting Started</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ol className="space-y-3">
                            <li className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    1
                                </div>
                                <div>
                                    <div className="font-medium text-gray-900">Search for judgments</div>
                                    <div className="text-sm text-gray-500">Use keywords to find relevant cases</div>
                                </div>
                            </li>
                            <li className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    2
                                </div>
                                <div>
                                    <div className="font-medium text-gray-900">Ask questions</div>
                                    <div className="text-sm text-gray-500">Get AI-powered legal explanations</div>
                                </div>
                            </li>
                            <li className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    3
                                </div>
                                <div>
                                    <div className="font-medium text-gray-900">Review history</div>
                                    <div className="text-sm text-gray-500">Access your past searches and chats</div>
                                </div>
                            </li>
                        </ol>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
