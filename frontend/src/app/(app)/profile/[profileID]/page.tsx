// src/app/(app)/profile/[profileID]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { userService } from "@/services/user/user-api";
import { UserProfile } from "@/services/user/user-api-types";
import { cn } from "@/lib/utils";

export default function ProfilePage() {
  const params = useParams();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Validate UUID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(params.profileID as string)) {
      setError("Invalid profile ID");
      setLoading(false);
      return;
    }

    const fetchProfile = async () => {
      try {
        const data = await userService.getUserProfile(params.profileID as string);
        setProfile(data);
      } catch (err: any) {
        setError(err.message || "Failed to load profile. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [params.profileID]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <p className="text-lg text-red-600">{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white py-16">
        <div className="mx-auto max-w-2xl px-4">
          <div className="animate-pulse space-y-8">
            <div className="flex items-center space-x-6">
              <div className="h-32 w-32 rounded-full bg-gray-200" />
              <div className="space-y-3">
                <div className="h-6 w-48 rounded bg-gray-200" />
                <div className="h-4 w-32 rounded bg-gray-200" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <p className="text-lg text-gray-600">Profile not found</p>
      </div>
    );
  }

  const initials = profile.name
    ? profile.name.split(" ").map((n) => n[0]).join("")
    : profile.first_name && profile.last_name
    ? `${profile.first_name[0]}${profile.last_name[0]}`
    : "?";

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-2xl px-4 py-16">
        <div className="space-y-12">
          {/* Profile Header */}
          <div className="flex items-start space-x-8">
            <div className="relative flex h-32 w-32 shrink-0 items-center justify-center overflow-hidden rounded-full bg-[#F0F7FF] text-2xl font-medium text-[#0066CC]">
              {initials}
            </div>
            <div className="space-y-1 pt-2">
              <h1 className="font-inter text-3xl font-light tracking-tight text-gray-900">
                {profile.name || `${profile.first_name || ""} ${profile.last_name || ""}`.trim() || "Unnamed User"}
              </h1>
              <p className="font-inter text-base text-gray-500">{profile.role}</p>
              {profile.email && (
                <p className="mt-2 font-inter text-sm text-gray-600">{profile.email}</p>
              )}
            </div>
          </div>

          {/* Profile Details */}
          <div className="space-y-8 border-t border-gray-100 pt-8">
            <div>
              <h2 className="font-inter text-sm font-medium uppercase tracking-wider text-gray-500">
                Account Information
              </h2>
              <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="space-y-1 rounded-lg bg-gray-50 p-4">
                  <dt className="text-sm text-gray-500">User ID</dt>
                  <dd className="text-sm font-medium text-gray-900">{profile.id}</dd>
                </div>
                <div className="space-y-1 rounded-lg bg-gray-50 p-4">
                  <dt className="text-sm text-gray-500">Role</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {profile.role.charAt(0).toUpperCase() + profile.role.slice(1)}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}