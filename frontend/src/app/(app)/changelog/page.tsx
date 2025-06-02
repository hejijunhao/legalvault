// src/app/(app)/changelog/page.tsx

import React from 'react';

const ChangelogPage = () => {
  const changelogData = [
    {
      version: '1.0.8-beta',
      date: 'June 2, 2025',
      changes: [
        { type: 'Feature', description: 'Implemented mounting logic for Paralegal model.' },
        { type: 'Fix', description: 'Updated API Routes to prepare for Workspace v1 rollout.' },
        { type: 'Feature', description: 'Included API Routes for LawNet integration while awaiting Lawnet docs.' },
      ],
    },
    {
      version: '1.0.7-beta',
      date: 'May 30, 2025',
      changes: [
        { type: 'Improvement', description: 'Enhanced LLM API integrations for more robust follow-up queries in Research.' },
        { type: 'Feature', description: 'Implemented bookmarking and highlighting features within Research messages.' },
        { type: 'Fix', description: 'Optimized message counting in Research for better performance when listing searches.' },
      ],
    },
    {
      version: '1.0.6-beta',
      date: 'May 23, 2025',
      changes: [
        { type: 'Feature', description: 'Redesigned chat interface to mirror iMessage group chat style for a familiar user experience.' },
        { type: 'Improvement', description: 'Updated message bubble styling and status indicators for a cleaner, more elegant look.' },
        { type: 'Fix', description: 'Addressed pgBouncer prepared statement errors with comprehensive configuration updates for SQLAlchemy and asyncpg.' },
      ],
    },
    {
      version: '1.0.5-beta',
      date: 'May 15, 2025',
      changes: [
        { type: 'Feature', description: 'Implemented initial LLM API integration for AI-powered legal research capabilities.' },
        { type: 'Improvement', description: 'Advanced client-side caching system for Research API to enhance performance and reduce server load.' },
        { type: 'Fix', description: 'Resolved OAuth2PasswordBearer tokenUrl mismatch in core authentication, preventing 401 Unauthorized errors.' },
      ],
    },
    {
      version: '1.0.4-beta',
      date: 'May 5, 2025',
      changes: [
        { type: 'Feature', description: 'Developed a robust message handling system for the Research feature, including domain models, DTOs, and API schemas.' },
        { type: 'Improvement', description: 'Migrated core database operations to a fully asynchronous approach using asyncpg for better scalability and performance.' },
        { type: 'Security', description: 'Implemented a secure webhook system for synchronizing user email changes from Supabase Auth to the application database.' },
      ],
    },
    {
      version: '1.0.3-beta',
      date: 'April 26, 2025',
      changes: [
        { type: 'Feature', description: 'Integrated Supabase Authentication API for streamlined user registration and login processes.' },
        { type: 'Improvement', description: 'Enhanced `get_current_user` function for pgBouncer compatibility and robust error handling in authentication flow.' },
        { type: 'Security', description: 'Added password length validation (minimum 6 characters) during user registration, aligning with Supabase Auth requirements.' },
      ],
    },
    {
      version: '1.0.2-beta',
      date: 'April 18, 2025',
      changes: [
        { type: 'Feature', description: 'Established core JWT-based authentication system with configurable token expiration (default 30 minutes).' },
        { type: 'Improvement', description: 'Implemented a database trigger to automatically create user profiles in `public.users` upon new entries in `auth.users`.' },
        { type: 'Fix', description: 'Corrected JWT exception handling in UserOperations to properly catch and log errors from the `jose` library.' },
      ],
    },
    {
      version: '1.0.1-beta',
      date: 'April 10, 2025',
      changes: [
        { type: 'Infrastructure', description: 'Configured SQLAlchemy with asyncpg for Supabase, addressing initial pgBouncer compatibility challenges.' },
        { type: 'Security', description: 'Initial setup of user authentication and authorization mechanisms, including role-based access considerations.' },
        { type: 'Feature', description: 'Implemented basic user profile management capabilities, allowing users to view their information.' },
      ],
    },
    {
      version: '1.0.0-beta',
      date: 'April 4, 2025',
      changes: [
        { type: 'Feature', description: 'Initial beta release of the LegalVault platform, focusing on core research functionalities.' },
        { type: 'Infrastructure', description: 'Core application scaffolding, database schema design, and initial Supabase integration.' },
        { type: 'Infrastructure', description: 'Deployed initial version with basic user registration and login capabilities.' },
      ],
    },
  ];

  return (
    <div className="min-h-screen text-gray-900 dark:text-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-3xl mx-auto">
        <header className="mb-12 pt-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-800 dark:text-gray-100 sm:text-5xl leading-snug">
            Changelog
          </h1>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Stay updated with the latest features, improvements, and fixes in LegalVault.
          </p>
        </header>

        <div className="space-y-12">
          {changelogData.map((entry, sectionIndex) => (
            <section 
              key={entry.version} 
              aria-labelledby={`version-${entry.version.replace(/\./g, '-')}`}
              className="border-t border-gray-200 dark:border-gray-700 pt-12 first:border-t-0 first:pt-0"
            >
              <div className="md:flex">
                <div className="md:w-1/4 mb-2 md:mb-0">
                  <h2 id={`version-${entry.version.replace(/\./g, '-')}`} className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
                    {entry.version}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{entry.date}</p>
                </div>
                <div className="md:w-3/4 md:pl-8">
                  <ul className="space-y-2 list-disc list-inside text-gray-700 dark:text-gray-300">
                    {entry.changes.map((change, index) => (
                      <li key={index} className="leading-relaxed">
                        {change.description}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChangelogPage;