# LegalVault Frontend Documentation

## Overview

The LegalVault frontend is a modern, responsive web application built with Next.js and React. It serves as the user interface for the LegalVault platform, providing lawyers with an AI-powered workstation for legal research, document management, and virtual paralegal assistance.

## Tech Stack

- **Framework**: Next.js 15.x (React 18.x)
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: Context API and Zustand
- **Form Handling**: React Hook Form with Zod validation
- **Authentication**: Supabase Auth with JWT tokens
- **UI Components**: Custom components built on Radix UI primitives
- **Data Fetching**: Custom API client with caching
- **Routing**: Next.js App Router
- **Animations**: Framer Motion
- **Notifications**: Sonner
- **Charts and Visualizations**: Tremor
- **Markdown Rendering**: React Markdown

## Directory Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── app/            # Next.js App Router pages
│   │   ├── (app)/      # Protected application routes
│   │   ├── (auth)/     # Authentication routes
│   │   ├── globals.css # Global styles
│   │   └── layout.tsx  # Root layout
│   ├── components/     # Reusable UI components
│   │   ├── abilities/  # Virtual paralegal abilities
│   │   ├── auth/       # Authentication components
│   │   ├── chat/       # Chat interface components
│   │   ├── library/    # Document library components
│   │   ├── research/   # Legal research components
│   │   ├── ui/         # Base UI components
│   │   └── workspace/  # Workspace components
│   ├── contexts/       # React context providers
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions and libraries
│   ├── services/       # API services
│   ├── store/          # Zustand state stores
│   ├── styles/         # Additional styles
│   └── types/          # TypeScript type definitions
├── next.config.ts      # Next.js configuration
├── tailwind.config.ts  # Tailwind CSS configuration
└── tsconfig.json       # TypeScript configuration
```

## Core Components

### Authentication

Authentication is implemented using Supabase Auth with JWT tokens. The system includes:

- **AuthContext**: Provides authentication state and methods throughout the application
- **AuthProvider**: Manages authentication state, session persistence, and token refresh
- **ProtectedRoute**: HOC that redirects unauthenticated users to the login page
- **AuthManager**: Singleton that handles auth events, token refresh, and listener management

```typescript
// Example of using authentication
const { user, isAuthenticated, login, logout } = useAuth();

// Protected routes implementation
<ProtectedRoute>
  <AppContent />
</ProtectedRoute>
```

### Routing and Layouts

The application uses Next.js App Router with nested layouts:

- **Root Layout**: Base HTML structure and global providers
- **App Layout**: Protected layout with main header and navigation
- **Feature-specific Layouts**: Specialized layouts for specific sections

### Research Feature

The Research feature allows users to perform legal research using AI:

- **ResearchContext**: Manages research sessions, messages, and API interactions
- **ResearchProvider**: Provides research functionality throughout the application
- **ResearchPage**: Main page for conducting research and viewing results
- **ResearchInput**: Input component for submitting research queries
- **UserMessages**: Component for displaying conversation history

The research feature implements a chat-like interface where users can ask legal questions and receive AI-generated responses with citations.

```typescript
// Example of using the research context
const { 
  sessions, 
  currentSession, 
  sendMessage, 
  createSession 
} = useResearch();
```

### API Integration

The frontend communicates with the backend through a custom API client:

- **Research API**: Services for managing research sessions and messages
- **Caching Layer**: Client-side caching for improved performance
- **Error Handling**: Consistent error handling and retry mechanisms
- **Authentication Headers**: Automatic inclusion of auth tokens

```typescript
// Example of API service usage
import { fetchSessions, createNewSession } from "@/services/research/research-api";

// Fetch sessions with caching
const sessions = await fetchSessions({ featuredOnly: true });

// Create a new session
const newSession = await createNewSession("What is the legal standard for negligence?");
```

## State Management

The application uses a combination of React Context and Zustand for state management:

- **Context API**: Used for global state that needs to be accessed throughout the component tree
- **Zustand**: Used for more complex state management with actions and selectors

## UI Components

The UI is built with a combination of custom components and Radix UI primitives, styled with Tailwind CSS:

- **Base Components**: Button, Input, Select, etc.
- **Composite Components**: Cards, Dialogs, Dropdowns, etc.
- **Page-specific Components**: Research input, Document viewer, etc.

## Error Handling

The application implements comprehensive error handling:

- **API Errors**: Structured error responses with status codes and messages
- **React Error Boundary**: Catches and displays errors in the UI
- **Toast Notifications**: User-friendly error messages

## Development Guidelines

### Code Style

- Use TypeScript for all components and functions
- Follow the React Hooks pattern for stateful logic
- Use functional components with explicit type definitions
- Implement proper error handling for all async operations
- Use descriptive variable and function names

### Component Structure

- Keep components focused on a single responsibility
- Use composition over inheritance
- Extract reusable logic into custom hooks
- Implement proper prop validation with TypeScript

### State Management

- Use local state for component-specific state
- Use context for shared state across components
- Consider performance implications when updating context
- Use memoization to prevent unnecessary re-renders

### API Integration

- Implement proper error handling for all API calls
- Use caching to improve performance
- Handle loading and error states in the UI
- Implement retry mechanisms for transient failures

## Performance Optimization

- **Code Splitting**: Implemented via Next.js dynamic imports
- **Image Optimization**: Using Next.js Image component
- **Memoization**: Using React.memo, useMemo, and useCallback
- **Caching**: Client-side caching for API responses

## Deployment

The frontend is deployed on Vercel, which provides:

- Automatic deployments from Git
- Preview deployments for pull requests
- Edge caching and CDN distribution
- Environment variable management

## Common Issues and Solutions

### Authentication Issues

- **Token Expiration**: The system automatically refreshes tokens before expiration
- **Session Persistence**: Sessions are stored in localStorage and restored on page load
- **CORS Issues**: Ensure the backend CORS configuration allows requests from the frontend domain

### API Connection Issues

- **SSL Certificate Errors**: The application includes custom handling for self-signed certificates
- **Network Failures**: Implement retry mechanisms with exponential backoff
- **Timeout Errors**: Configure appropriate timeout values for API requests

## Future Enhancements

- **Offline Support**: Implement service workers for offline functionality
- **Progressive Web App**: Convert to a full PWA with installability
- **Real-time Collaboration**: Enhance WebSocket integration for collaborative features
- **Accessibility Improvements**: Enhance keyboard navigation and screen reader support
- **Mobile Optimization**: Further improve the mobile user experience
- **Performance Monitoring**: Implement client-side performance tracking