"use client";

import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { chatService } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Send, Bot, User, Loader2, FileText } from "lucide-react";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: any[];
}

function ChatContent() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const searchParams = useSearchParams();
    const hasAutoRun = useRef(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Auto-run query from history redirect
    useEffect(() => {
        const query = searchParams.get("query");
        if (query && !hasAutoRun.current) {
            hasAutoRun.current = true;
            runQuery(query);
        }
    }, [searchParams]);

    const runQuery = async (queryText: string) => {
        if (!queryText.trim() || loading) return;

        const userMessage: Message = { role: "user", content: queryText };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const response = await chatService.chat(queryText, 3, "advice");
            const assistantMessage: Message = {
                role: "assistant",
                content: response.answer,
                sources: response.sources,
            };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err: any) {
            const errorMessage: Message = {
                role: "assistant",
                content: "Sorry, I encountered an error. Please try again.",
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await runQuery(input);
    };

    return (
        <div className="max-w-4xl h-[calc(100vh-12rem)]">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Legal Assistant</h1>
                <p className="text-gray-600">Ask legal questions in natural language</p>
            </div>

            <Card className="flex flex-col h-full">
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 && (
                        <div className="flex-1 flex items-center justify-center h-full">
                            <p className="text-gray-400 italic">No messages yet. Ask a legal question to start the conversation.</p>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <div
                            key={index}
                            className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            {message.role === "assistant" && (
                                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                    <Bot className="h-5 w-5 text-white" />
                                </div>
                            )}

                            <div
                                className={`max-w-[70%] rounded-lg px-4 py-3 ${
                                    message.role === "user"
                                        ? "bg-blue-600 text-white"
                                        : "bg-gray-100 text-gray-900"
                                }`}
                            >
                                <p className="whitespace-pre-wrap">{message.content}</p>

                                {message.sources && message.sources.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-gray-300">
                                        <p className="text-xs font-semibold mb-2 text-gray-700">Sources:</p>
                                        <div className="space-y-1">
                                            {message.sources.slice(0, 3).map((source, idx) => (
                                                <div key={idx} className="text-xs text-gray-600">
                                                    <FileText className="h-3 w-3 inline mr-1" />
                                                    {source.title || "Legal Document"}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {message.role === "user" && (
                                <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                                    <User className="h-5 w-5 text-white" />
                                </div>
                            )}
                        </div>
                    ))}

                    {loading && (
                        <div className="flex gap-3 justify-start">
                            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                <Bot className="h-5 w-5 text-white" />
                            </div>
                            <div className="bg-gray-100 rounded-lg px-4 py-3">
                                <Loader2 className="h-5 w-5 animate-spin text-gray-600" />
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="border-t bg-white p-4">
                    <form onSubmit={handleSubmit} className="flex gap-2">
                        <Input
                            type="text"
                            placeholder="Ask a legal question..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={loading}
                            className="flex-1"
                        />
                        <Button type="submit" disabled={loading}>
                            <Send className="h-4 w-4" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
        }>
            <ChatContent />
        </Suspense>
    );
}
