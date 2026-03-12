"use client";

import { useState, useEffect } from "react";
import { profileService, authService } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { User, Mail, Calendar, Loader2 } from "lucide-react";

export default function ProfilePage() {
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const data = await profileService.getProfile();
            setProfile(data);
        } catch (err: any) {
            // Fallback to local storage if API fails
            const user = authService.getUser();
            setProfile(user);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("en-US", {
            month: "long",
            day: "numeric",
            year: "numeric",
        });
    };

    return (
        <div className="max-w-2xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
                <p className="text-gray-600">Manage your account information</p>
            </div>

            {loading && (
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                </div>
            )}

            {!loading && profile && (
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Account Information</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center gap-4 pb-4 border-b">
                                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
                                    <User className="h-8 w-8 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-semibold text-gray-900">
                                        {profile.username}
                                    </h2>
                                    <p className="text-gray-600">Legal Researcher</p>
                                </div>
                            </div>

                            <div className="grid gap-4">
                                <div className="flex items-center gap-3">
                                    <User className="h-5 w-5 text-gray-400" />
                                    <div>
                                        <p className="text-sm text-gray-500">Username</p>
                                        <p className="font-medium text-gray-900">{profile.username}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <Mail className="h-5 w-5 text-gray-400" />
                                    <div>
                                        <p className="text-sm text-gray-500">Email</p>
                                        <p className="font-medium text-gray-900">{profile.email}</p>
                                    </div>
                                </div>

                                {profile.created_at && (
                                    <div className="flex items-center gap-3">
                                        <Calendar className="h-5 w-5 text-gray-400" />
                                        <div>
                                            <p className="text-sm text-gray-500">Member Since</p>
                                            <p className="font-medium text-gray-900">
                                                {formatDate(profile.created_at)}
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Usage Statistics</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="text-center p-4 bg-blue-50 rounded-lg">
                                    <p className="text-2xl font-bold text-blue-600">-</p>
                                    <p className="text-sm text-gray-600">Total Searches</p>
                                </div>
                                <div className="text-center p-4 bg-green-50 rounded-lg">
                                    <p className="text-2xl font-bold text-green-600">-</p>
                                    <p className="text-sm text-gray-600">AI Conversations</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Subscription</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium text-gray-900">Free Plan</p>
                                    <p className="text-sm text-gray-600">Unlimited access to all features</p>
                                </div>
                                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                                    Active
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
