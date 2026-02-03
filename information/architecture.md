# Frontend Architecture for Backend Developers

## Authentication System

### Auth State Management (Zustand Store)
The authentication is centrally managed through `src/store/authStore.js` using Zustand:

**State Properties:**
```javascript
{
  user: null,              // Supabase user object
  userProfile: null,       // Extended user profile data
  session: null,           // Supabase session with tokens
  loading: true,           // Loading state for auth operations
  isAuthenticated: false,  // Boolean auth status
  error: null,             // General error messages
  authError: {             // Specific error states
    signup: undefined,
    login: undefined,
    logout: undefined,
    updateProfile: undefined
  }
}
```

**Key Auth Actions:**
- `signUp(email, password)` - Creates new user account
- `signIn(email, password)` - Authenticates existing user
- `signOut()` - Logs out user and clears state
- `resetPassword(email)` - Sends password reset email
- `initializeAuth()` - Sets up real-time auth listener

### Auth Provider Setup
`AuthProvider.jsx` wraps the entire app and initializes authentication:
- Calls `initializeAuth()` on mount to listen for auth state changes
- Automatically updates store when user logs in/out
- Provides cleanup function for auth listeners

### How Backend Can Use Auth State
```javascript
// In any component, access auth state:
import { useAuthStore } from '@/store/authStore'

// Read auth state
const { user, isAuthenticated, loading } = useAuthStore()

// Access auth actions
const { signIn, signOut } = useAuthStore()
```

---

## API Integration Setup

### Axios Configuration (`src/lib/axios.js`)
The API client is pre-configured with authentication:

```javascript
// Base configuration
baseURL: process.env.NEXT_PUBLIC_API_URL
headers: { 'Content-Type': 'application/json' }

// Automatic auth token injection
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})
```

**Backend Integration Points:**
- All API requests automatically include `Authorization: Bearer <token>` header
- Token is fetched from Supabase session in real-time
- Error responses are logged for debugging
- Base URL should be set in `NEXT_PUBLIC_API_URL` environment variable

### How to Use API Client
```javascript
import { api } from '@/lib/axios'

// GET request with auto auth
const response = await api.get('/users/profile')

// POST request with auto auth
const result = await api.post('/workflows', { name: 'New Workflow' })
```

---

## State Management Architecture

### Zustand Store Pattern
The app uses Zustand for state management with this pattern:

```javascript
// Store structure
export const useStore = create((set, get) => ({
  // State
  data: null,
  loading: false,
  
  // Actions
  setData: (data) => set({ data }),
  fetchData: async () => {
    set({ loading: true })
    // API call
    set({ data: result, loading: false })
  }
}))

// Usage in components
const { data, loading, fetchData } = useStore()
```

### Key State Stores

**Auth Store** (`src/store/authStore.js`)
- Manages user authentication state
- Handles login/logout/signup operations
- Provides real-time auth status updates

**Expected Additional Stores** (based on components):
- Chat Store - Message history and chat state
- Workflow Store - Workflow builder state
- UI Store - Global UI state (sidebar collapsed, etc.)

---

## Form Handling System

### React Hook Form Integration
Forms use React Hook Form for validation and state management:

```javascript
import { useForm } from 'react-hook-form'

const { register, handleSubmit, formState: { errors } } = useForm()

const onSubmit = async (data) => {
  // Form data is validated and ready for API
  await api.post('/endpoint', data)
}
```

**Backend Considerations:**
- Form data is pre-validated on frontend
- Consistent data structure sent to API
- Error handling integrated with form state

---

## Component Communication Patterns

### Data Flow Architecture
```
Supabase Auth → Zustand Store → Components → API Calls → Backend
     ↑                                                        ↓
     └─────────── Real-time Updates ←─────────────────────────┘
```

### Key Integration Points for Backend

**1. Authentication Flow:**
- User logs in → Supabase generates JWT token
- Token stored in Zustand store and Supabase session
- All API requests include token in Authorization header
- Backend validates JWT token for protected routes

**2. Real-time Updates:**
- Supabase provides real-time auth state changes
- Frontend automatically updates when auth status changes
- Backend can push updates through Supabase real-time subscriptions

**3. API Request Pattern:**
```javascript
// Frontend sends requests like this:
Headers: {
  'Authorization': 'Bearer <supabase_jwt_token>',
  'Content-Type': 'application/json'
}

// Backend should:
// 1. Validate JWT token
// 2. Extract user ID from token
// 3. Return appropriate data for that user
```

---

## Environment Variables Required

### Frontend Environment Variables
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=your_backend_api_url
```

### Backend Integration Requirements
- Accept and validate Supabase JWT tokens
- Extract user information from JWT payload
- Implement CORS for frontend domain
- Handle preflight OPTIONS requests
- Return consistent JSON error responses

---

## Key State Changes That Affect Backend

### Authentication State Changes
- `isAuthenticated: true/false` - Controls route access
- `user.id` - Used for user-specific API calls
- `session.access_token` - JWT token for API authentication

### Chat State Changes
- New messages trigger API calls to save/retrieve chat history
- Chat sessions may need backend persistence

### Workflow State Changes
- Workflow creation/editing triggers API calls to save workflow data
- Workflow execution may trigger backend processing

### Form Submissions
- All forms validate data before sending to backend
- Consistent error handling expected from backend API responses

---

## API Endpoints Expected by Frontend

Based on the component structure, the backend should provide:

**Authentication Endpoints:**
- User profile management (if extending Supabase auth)

**Chat Endpoints:**
- `GET /chat/messages` - Retrieve chat history
- `POST /chat/messages` - Send new message
- `POST /chat/sessions` - Create chat session

**Workflow Endpoints:**
- `GET /workflows` - List user workflows
- `POST /workflows` - Create new workflow
- `PUT /workflows/:id` - Update workflow
- `DELETE /workflows/:id` - Delete workflow
- `POST /workflows/:id/execute` - Execute workflow

**Integration Endpoints:**
- `GET /integrations` - List available integrations
- `POST /integrations` - Connect new integration
- `GET /integrations/status` - Check integration status