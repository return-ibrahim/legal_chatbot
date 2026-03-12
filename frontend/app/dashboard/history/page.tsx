"use client";

import { useState, useEffect } from "react";
import { historyService } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { MessageSquare, Search, Clock, Loader2 } from "lucide-react";

export default function HistoryPage() {
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const data = await historyService.getHistory();
            setHistory(data.history || []);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Your History</h1>
                <p className="text-gray-600">View your past searches and conversations</p>
            </div>

            {loading && (
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                </div>
            )}

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            )}

            {!loading && !error && history.length === 0 && (
                <div className="text-center py-12">
                    <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No history yet</h3>
                    <p className="text-gray-600">
                        Your searches and conversations will appear here
                    </p>
                </div>
            )}

            {!loading && history.length > 0 && (
                <div className="space-y-4">
                    {history.map((item) => (
                        <Card key={item.id}>
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-2">
                                        {item.mode === "chat" ? (
                                            <MessageSquare className="h-5 w-5 text-blue-600" />
                                        ) : (
                                            <Search className="h-5 w-5 text-green-600" />
                                        )}
                                        <CardTitle className="text-lg">
                                            {item.mode === "chat" ? "AI Chat" : "Search"}
                                        </CardTitle>
                                    </div>
                                    <div className="flex items-center gap-2 text-sm text-gray-500">
                                        <Clock className="h-4 w-4" />
                                        {formatDate(item.created_at)}
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    <div>
                                        <p className="text-sm font-medium text-gray-700 mb-1">Query:</p>
                                        <p className="text-gray-900">{item.query}</p>
                                    </div>

                                    {item.mode === "chat" && (
                                        <div>
                                            <p className="text-sm font-medium text-gray-700 mb-1">Response:</p>
                                            <p className="text-gray-900 line-clamp-3">{item.response}</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
