# Frontend Tech Stack Overview

## Core Technologies

### Framework & Runtime
- **Next.js 16.1.6** - React framework with SSR, routing, and API routes
- **React 19.2.3** - UI library for building components
- **React DOM 19.2.3** - React renderer for web

### Styling & UI
- **Tailwind CSS 4** - Utility-first CSS framework for styling
- **PostCSS** - CSS processor for Tailwind
- **Radix UI** - Headless UI components for accessibility
  - `@radix-ui/react-checkbox` - Checkbox component
  - `@radix-ui/react-label` - Label component  
  - `@radix-ui/react-slot` - Slot component for composition
  - `@radix-ui/react-switch` - Toggle switch component
- **Class Variance Authority (CVA)** - Utility for creating component variants
- **clsx** - Utility for conditional className joining
- **tailwind-merge** - Utility for merging Tailwind classes
- **Lucide React** - Icon library with React components

### State Management
- **Zustand 5.0.10** - Lightweight state management library
- **React Hook Form 7.71.1** - Form state management and validation

### Data Fetching & API
- **Axios 1.13.4** - HTTP client for API requests
- **SWR 2.3.8** - Data fetching library with caching and revalidation
- **Supabase JS 2.93.3** - Backend-as-a-Service client for auth and database

### UI Enhancements
- **Sonner 2.0.7** - Toast notification library

### Development Tools
- **ESLint** - Code linting
- **ESLint Config Next** - Next.js specific ESLint rules

---

## Frontend Structure Breakdown

### Core Architecture
The frontend is organized into a clean, modular structure with clear separation of concerns:

```
src/
├── app/                    # Next.js App Router structure
│   ├── (auth)/            # Authentication pages (login, signup)
│   ├── (shared-layout)/   # Protected pages with sidebar layout
│   ├── api/               # API routes
│   ├── layout.jsx         # Root layout with AuthProvider
│   └── page.jsx           # Landing page
├── components/            # Reusable UI components
├── hooks/                 # Custom React hooks
├── lib/                   # Utility libraries and configurations
└── store/                 # Zustand state stores
```

### Component Categories

#### Dumb/Presentational Components (Backend developers can ignore these)
These components only handle UI rendering and receive data via props:

**UI Components** (`src/components/ui/`)
- `button.jsx` - Styled button with variants
- `card.jsx` - Card container component
- `checkbox.jsx` - Checkbox input
- `input.jsx` - Text input field
- `label.jsx` - Form label
- `switch.jsx` - Toggle switch
- `particle-background.jsx` - Animated background effect

**Landing Page Components** (`src/components/landing/`)
- `Hero.jsx` - Hero section with animations
- `Features.jsx` - Features showcase section
- `FeatureCard.jsx` - Individual feature display
- `Footer.jsx` - Site footer

**Chat UI Components** (`src/components/chat/`)
- `MessageList.jsx` - Displays list of messages
- `ChatInput.jsx` - Message input interface
- `MessageBubble.jsx` - Individual message display

**Workflow UI Components** (`src/components/workflow/`)
- `WorkflowNode.jsx` - Visual workflow node
- `WorkflowSidebar.jsx` - Workflow tools sidebar

#### Smart/Container Components (Backend developers should understand these)
These components contain business logic and state management:

**Core Layout**
- `Sidebar.jsx` - Main navigation with auth integration
- `(shared-layout)/layout.jsx` - Protected pages layout

**Functional Components**
- `AuthProvider.jsx` - Authentication context provider
- `ChatInterface.jsx` - Chat functionality and state
- `WorkflowBuilder.jsx` - Workflow creation logic
- `Navbar.jsx` - Navigation with conditional auth display