// src/components/research/search/TypingIndicator.tsx

/* eslint-disable @next/next/no-img-element */
import React from 'react';
// import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'; // Commented out
import { Skeleton } from '@/components/ui/skeleton';
import { useAuth } from '@/contexts/auth-context'; 

// Assuming VirtualParalegal type is available or defined elsewhere
// import { VirtualParalegal } from '@/types'; 

export const TypingIndicator: React.FC = () => {
  // Destructure user to get VP ID if needed later, or remove if unused
  // const { user } = useAuth(); 
  
  // For now, we don't need the full VP object
  // const { virtualParalegal } = useAuth(); // Commented out

  // Simplified loading state - assumes indicator is always shown when rendered
  const isLoading = false; // Set to false as we are not loading VP data anymore

  // Use a generic name for now
  const vpName = 'Virtual Paralegal';
  // const vpProfilePictureUrl = virtualParalegal?.profile_picture_url; // Commented out
  // const vpNameInitial = vpName.charAt(0).toUpperCase(); // Commented out

  return (
    <div className="flex flex-col items-start space-y-1 group animate-fade-in">
      {/* Sender Info */}
      <div className="flex items-center space-x-2 pl-1">
        {/* Removed Skeleton and Avatar logic for now */}
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          {vpName}
        </span>
      </div>

      {/* Typing Bubble */}
      <div className="ml-7 flex items-center space-x-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2.5 shadow-sm max-w-md md:max-w-lg lg:max-w-xl">
        <div className="typing-dot animate-bounce delay-0"></div>
        <div className="typing-dot animate-bounce delay-150"></div>
        <div className="typing-dot animate-bounce delay-300"></div>
      </div>
      <style jsx>{`
        /* styles remain the same */
        .typing-dot {
          width: 6px;
          height: 6px;
          background-color: #a0aec0; /* gray-500 */
          border-radius: 50%;
          display: inline-block;
        }
        @media (prefers-color-scheme: dark) {
          .typing-dot {
            background-color: #718096; /* gray-600 */
          }
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
        .animate-bounce {
          animation: bounce 1s infinite;
        }
        .delay-0 { animation-delay: 0s; }
        .delay-150 { animation-delay: 0.15s; }
        .delay-300 { animation-delay: 0.3s; }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};


