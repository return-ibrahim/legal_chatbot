"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { searchService } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Search, Loader2, FileText, Calendar, Building2 } from "lucide-react";

export default function SearchPage() {
    const [query, setQuery] = useState("");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [searched, setSearched] = useState(false);
    const searchParams = useSearchParams();

    // Auto-run query from history redirect
    useEffect(() => {
        const param = searchParams.get("query");
        if (param) {
            setQuery(param);
            runSearch(param);
        }
    }, [searchParams]);

    const runSearch = async (queryText: string) => {
        if (!queryText.trim()) return;

        setLoading(true);
        setError("");
        setSearched(true);
        setResult(null);

        try {
            const data = await searchService.search(queryText, 8, "research");
            setResult(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to search. Please try again.");
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        await runSearch(query);
    };

    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Legal Judgments</h1>
                <p className="text-gray-600">Find exact legal passages and sections</p>
            </div>

            <Card className="mb-8">
                <CardContent className="pt-6">
                    <form onSubmit={handleSearch} className="flex gap-4">
                        <div className="flex-1">
                            <Input
                                type="text"
                                placeholder="Enter keywords (e.g., 'Section 302 IPC punishment', 'Article 21')"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="w-full"
                            />
                        </div>
                        <Button type="submit" disabled={loading}>
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Searching...
                                </>
                            ) : (
                                <>
                                    <Search className="mr-2 h-4 w-4" />
                                    Search
                                </>
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            )}

            {searched && !loading && !result && !error && (
                <div className="text-center py-12">
                    <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                    <p className="text-gray-600">Try different keywords or check spelling</p>
                </div>
            )}

            {result && (
                <div className="space-y-6">
                    {/* Legal Passage Card */}
                    <Card className="border-blue-200 shadow-md">
                        <CardHeader className="bg-blue-50 border-b border-blue-100 pb-4">
                            <CardTitle className="text-xl text-blue-800 flex items-center gap-2">
                                <Building2 className="h-5 w-5" />
                                Retrieved Legal Context
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6">
                            <div className="prose prose-blue max-w-none">
                                <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap font-serif">
                                    {result.answer}
                                </p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Sources Section */}
                    {result.results && result.results.length > 0 && (
                        <div className="mt-8">
                            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
                                Sources & References
                            </h3>
                            <div className="grid gap-3">
                                {result.results.slice(0, 5).map((source: any, index: number) => (
                                    <div key={index} className="bg-white border rounded-lg p-3 hover:bg-gray-50 transition flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <FileText className="h-4 w-4 text-gray-400" />
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">{source.title}</p>
                                                <p className="text-xs text-gray-500">{source.court} • {source.date}</p>
                                            </div>
                                        </div>
                                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                            Match: {Math.round(source.score * 100) / 100}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
