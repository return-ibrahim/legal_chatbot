import Link from "next/link";
import { Scale, Search, MessageSquare, FileText, Shield } from "lucide-react";

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
            {/* Header */}
            <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Scale className="h-8 w-8 text-blue-600" />
                        <span className="text-2xl font-bold text-gray-900">LexQuery</span>
                    </div>
                    <div className="flex gap-4">
                        <Link
                            href="/dashboard/search"
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="container mx-auto px-4 py-20 text-center">
                <div className="max-w-3xl mx-auto">
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">
                        LexQuery: Legal Intelligence
                        <br />
                        <span className="text-blue-600">Made Simple</span>
                    </h1>
                    <p className="text-xl text-gray-600 mb-8">
                        Precision-engineered legal reasoning for Indian Law. Get instant, verified answers
                        grounded in thousands of legal provisions and judicial precedents.
                    </p>
                    <Link
                        href="/dashboard/search"
                        className="inline-block px-8 py-4 bg-blue-600 text-white text-lg rounded-lg hover:bg-blue-700 transition shadow-lg"
                    >
                        Start Your Research
                    </Link>
                </div>
            </section>

            {/* Features Section */}
            <section className="container mx-auto px-4 py-16">
                <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
                    Advanced Legal Research Infrastructure
                </h2>
                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                    <div className="bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition">
                        <Search className="h-12 w-12 text-blue-600 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-3">
                            Semantic Legal Search
                        </h3>
                        <p className="text-gray-600">
                            Find relevant Indian statutes and judgments instantly with AI-powered semantic intelligence.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition">
                        <MessageSquare className="h-12 w-12 text-blue-600 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-3">
                            Hierarchical AI Assistant
                        </h3>
                        <p className="text-gray-600">
                            Get structured legal reasoning with explicit source labeling from local data and verified web exports.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl border border-gray-200 hover:shadow-lg transition">
                        <FileText className="h-12 w-12 text-blue-600 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-3">
                            Research Repository
                        </h3>
                        <p className="text-gray-600">
                            Securely track and manage your entire legal research journey with persistent conversation history.
                        </p>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="bg-blue-50 py-16">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
                        How It Works
                    </h2>
                    <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                                1
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Query Input
                            </h3>
                            <p className="text-gray-600">
                                Enter a specific legal question or keywords. Choose between Research or Advice mode.
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                                2
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Hierarchical RAG
                            </h3>
                            <p className="text-gray-600">
                                Our system searches the local legal database with a fallback to verified web sources.
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                                3
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                Verified Answers
                            </h3>
                            <p className="text-gray-600">
                                Receive structured legal reasoning with explicit source labeling for transparency.
                            </p>
                        </div>
                    </div>
                </div>
            </section>


            {/* Footer */}
            <footer className="border-t bg-white py-8">
                <div className="container mx-auto px-4 text-center text-gray-600">
                    <p>© 2026 LexQuery. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}
