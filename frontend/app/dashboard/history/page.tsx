"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { historyService } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { MessageSquare, Search, Clock, Loader2, Trash2, Trash } from "lucide-react";

export default function HistoryPage() {
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [deletingId, setDeletingId] = useState<string | null>(null);
    const [clearingAll, setClearingAll] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const router = useRouter();

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

    const handleDelete = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation(); // Prevent card click when deleting
        setDeletingId(id);
        try {
            await historyService.deleteHistory(id);
            setHistory((prev) => prev.filter((item) => item.id !== id));
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to delete entry");
        } finally {
            setDeletingId(null);
        }
    };

    const handleClearAll = async () => {
        setClearingAll(true);
        try {
            await historyService.clearAllHistory();
            setHistory([]);
            setShowConfirm(false);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to clear history");
        } finally {
            setClearingAll(false);
        }
    };

    const handleReopenConversation = (item: any) => {
        const query = encodeURIComponent(item.query);
        if (item.mode === "chat") {
            router.push(`/dashboard/chat?query=${query}`);
        } else {
            router.push(`/dashboard/search?query=${query}`);
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
            <div className="mb-8 flex items-start justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Your History</h1>
                    <p className="text-gray-600">View your past searches and conversations</p>
                </div>

                {/* Clear All Button */}
                {!loading && history.length > 0 && (
                    <div className="relative">
                        {!showConfirm ? (
                            <button
                                onClick={() => setShowConfirm(true)}
                                className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition"
                            >
                                <Trash className="h-4 w-4" />
                                Clear All
                            </button>
                        ) : (
                            <div className="flex items-center gap-2 bg-white border border-red-300 rounded-lg px-3 py-2 shadow-md">
                                <span className="text-sm text-gray-700">Are you sure?</span>
                                <button
                                    onClick={handleClearAll}
                                    disabled={clearingAll}
                                    className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition disabled:opacity-50 flex items-center gap-1"
                                >
                                    {clearingAll && <Loader2 className="h-3 w-3 animate-spin" />}
                                    Yes, clear
                                </button>
                                <button
                                    onClick={() => setShowConfirm(false)}
                                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
                                >
                                    Cancel
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {loading && (
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                </div>
            )}

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
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
                        <Card
                            key={item.id}
                            onClick={() => handleReopenConversation(item)}
                            className="cursor-pointer hover:shadow-md hover:border-blue-300 transition-all duration-200 group"
                        >
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

                                    <div className="flex items-center gap-3">
                                        <div className="flex items-center gap-2 text-sm text-gray-500">
                                            <Clock className="h-4 w-4" />
                                            {formatDate(item.created_at)}
                                        </div>

                                        {/* Delete Button */}
                                        <button
                                            onClick={(e) => handleDelete(e, item.id)}
                                            disabled={deletingId === item.id}
                                            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition opacity-0 group-hover:opacity-100 disabled:opacity-50"
                                            title="Delete this entry"
                                        >
                                            {deletingId === item.id ? (
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                            ) : (
                                                <Trash2 className="h-4 w-4" />
                                            )}
                                        </button>
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

                                    {/* Reopen hint */}
                                    <p className="text-xs text-blue-500 opacity-0 group-hover:opacity-100 transition">
                                        Click to reopen this conversation →
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
