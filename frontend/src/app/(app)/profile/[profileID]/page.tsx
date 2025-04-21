// src/app/(app)/profile/[profileID]/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { userService } from "@/services/user/user-api";
import { UserProfile } from "@/services/user/user-api-types";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { 
  EnvelopeIcon, 
  BuildingOfficeIcon, 
  UserCircleIcon, 
  CalendarIcon,
  PhoneIcon,
  PencilIcon,
  MapPinIcon,
  LinkIcon
} from "@heroicons/react/24/outline";

export default function ProfilePage() {
  const params = useParams();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
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
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-base text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 mb-6" />
        <div className="space-y-6 animate-pulse">
          <div className="h-48 bg-gray-100 rounded-lg" />
          <div className="space-y-4">
            <div className="h-24 w-24 -mt-12 ml-6 rounded-lg bg-gray-200 ring-4 ring-white" />
            <div className="px-6 space-y-4">
              <div className="h-8 w-64 rounded bg-gray-200" />
              <div className="h-4 w-48 rounded bg-gray-200" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1440px]">
      <div className="relative bg-white rounded-lg shadow-sm">
        {/* Header Area */}
        <div className="h-48 bg-gradient-to-r from-gray-50 to-gray-100 rounded-t-lg" />
        
        <div className="relative px-6">
          {/* Profile Picture & Actions */}
          <div className="flex items-start justify-between">
            <div className="absolute -mt-12 h-24 w-24 overflow-hidden rounded-lg ring-4 ring-white bg-white shadow-sm">
              <div className="h-full w-full bg-[#F3F4F6] flex items-center justify-center">
                <UserCircleIcon className="h-16 w-16 text-gray-400" />
              </div>
            </div>
            <div className="flex-1" /> {/* Spacer */}
            <div className="py-4">
              <button
                onClick={() => setEditing(!editing)}
                className="rounded-full px-4 py-1.5 text-sm font-medium border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                {editing ? "Save Profile" : "Edit Profile"}
              </button>
            </div>
          </div>

          {/* Basic Info Section */}
          <div className="mt-16 space-y-2">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-semibold text-gray-900">
                {editing ? (
                  <input 
                    type="text" 
                    className="border rounded px-2 py-1 text-lg w-full focus:ring-1 focus:ring-[#0066CC] focus:border-[#0066CC] transition-colors"
                    defaultValue={profile?.name || ''}
                    placeholder="Full Name"
                  />
                ) : (
                  profile?.name || `${profile?.first_name || ''} ${profile?.last_name || ''}`
                )}
              </h1>
              {editing && <PencilIcon className="h-4 w-4 text-gray-400" />}
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>@{profile?.id.split('-')[0]}</span>
              <div className="flex items-center">
                <BuildingOfficeIcon className="h-4 w-4 mr-1.5" />
                <span>{profile?.role}</span>
              </div>
              <div className="flex items-center">
                <CalendarIcon className="h-4 w-4 mr-1.5" />
                <span>Joined {format(new Date(profile?.created_at || ''), 'MMMM yyyy')}</span>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <h2 className="text-sm font-medium text-gray-900 mb-3">Contact Information</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* Email */}
              <div className={cn(
                "flex items-center gap-2 p-2.5 rounded border border-transparent",
                editing ? "bg-gray-50 border-gray-100" : ""
              )}>
                <EnvelopeIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                {editing ? (
                  <input 
                    type="email" 
                    className="flex-1 bg-white border rounded px-2 py-1.5 focus:ring-1 focus:ring-[#0066CC] focus:border-[#0066CC] transition-colors"
                    defaultValue={profile?.email}
                    placeholder="Email"
                  />
                ) : (
                  <span className="truncate">{profile?.email}</span>
                )}
              </div>

              {/* Phone */}
              <div className={cn(
                "flex items-center gap-2 p-2.5 rounded border border-transparent",
                editing ? "bg-gray-50 border-gray-100" : ""
              )}>
                <PhoneIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                {editing ? (
                  <input 
                    type="tel" 
                    className="flex-1 bg-white border rounded px-2 py-1.5 focus:ring-1 focus:ring-[#0066CC] focus:border-[#0066CC] transition-colors"
                    placeholder="Phone Number"
                  />
                ) : (
                  <span className="text-gray-400">Add phone number</span>
                )}
              </div>
            </div>
          </div>

          {/* Personal Information */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <h2 className="text-sm font-medium text-gray-900 mb-3">Personal Information</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* First Name */}
              <div className={cn(
                "flex items-center gap-2 p-2.5 rounded border border-transparent",
                editing ? "bg-gray-50 border-gray-100" : ""
              )}>
                <UserCircleIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                {editing ? (
                  <input 
                    type="text" 
                    className="flex-1 bg-white border rounded px-2 py-1.5 focus:ring-1 focus:ring-[#0066CC] focus:border-[#0066CC] transition-colors"
                    defaultValue={profile?.first_name || ''}
                    placeholder="First Name"
                  />
                ) : (
                  <span className="truncate">{profile?.first_name || 'Add first name'}</span>
                )}
              </div>

              {/* Last Name */}
              <div className={cn(
                "flex items-center gap-2 p-2.5 rounded border border-transparent",
                editing ? "bg-gray-50 border-gray-100" : ""
              )}>
                <UserCircleIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                {editing ? (
                  <input 
                    type="text" 
                    className="flex-1 bg-white border rounded px-2 py-1.5 focus:ring-1 focus:ring-[#0066CC] focus:border-[#0066CC] transition-colors"
                    defaultValue={profile?.last_name || ''}
                    placeholder="Last Name"
                  />
                ) : (
                  <span className="truncate">{profile?.last_name || 'Add last name'}</span>
                )}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <div className="flex gap-6">
              <div>
                <span className="font-medium text-gray-900">0</span>{" "}
                <span className="text-sm text-gray-500">Following</span>
              </div>
              <div>
                <span className="font-medium text-gray-900">0</span>{" "}
                <span className="text-sm text-gray-500">Followers</span>
              </div>
              <div>
                <span className="font-medium text-gray-900">0</span>{" "}
                <span className="text-sm text-gray-500">Cases</span>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6">
            <div className="flex gap-8 border-b border-gray-100">
              <button className="border-b-2 border-[#0066CC] px-4 py-3 text-sm font-medium text-[#0066CC]">
                Cases
              </button>
              <button className="px-4 py-3 text-sm font-medium text-gray-500 hover:text-gray-700">
                Activity
              </button>
              <button className="px-4 py-3 text-sm font-medium text-gray-500 hover:text-gray-700">
                Network
              </button>
            </div>
          </div>

          {/* Content Area */}
          <div className="py-8 text-center text-sm text-gray-500">
            No cases yet
          </div>
        </div>
      </div>
    </div>
  );
}