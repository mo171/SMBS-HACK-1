-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.chat_history (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  role text NOT NULL CHECK (role = ANY (ARRAY['user'::text, 'assistant'::text])),
  content text NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  profile_id uuid,
  CONSTRAINT chat_history_pkey PRIMARY KEY (id),
  CONSTRAINT chat_history_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.customers (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  full_name text NOT NULL,
  phone_number text UNIQUE,
  total_debt numeric DEFAULT 0,
  profile_id uuid,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT customers_pkey PRIMARY KEY (id),
  CONSTRAINT customers_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.invoice_items (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone DEFAULT now(),
  invoice_id uuid,
  description text,
  quantity numeric,
  unit_price numeric,
  product_id uuid,
  CONSTRAINT invoice_items_pkey PRIMARY KEY (id),
  CONSTRAINT invoice_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id),
  CONSTRAINT invoice_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
);
CREATE TABLE public.invoices (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  customer_id uuid,
  status text DEFAULT 'pending'::text,
  total_amount numeric,
  profile_id uuid,
  created_at timestamp with time zone DEFAULT now(),
  amount_paid numeric DEFAULT 0,
  CONSTRAINT invoices_pkey PRIMARY KEY (id),
  CONSTRAINT invoices_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id),
  CONSTRAINT invoices_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.payments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  customer_id uuid,
  amount_received numeric NOT NULL,
  payment_mode text,
  created_at timestamp without time zone DEFAULT now(),
  profile_id uuid,
  CONSTRAINT payments_pkey PRIMARY KEY (id),
  CONSTRAINT payments_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id),
  CONSTRAINT payments_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.products (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  current_stock integer DEFAULT 0 CHECK (current_stock >= 0),
  base_price numeric,
  profile_id uuid,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT products_pkey PRIMARY KEY (id),
  CONSTRAINT products_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.profiles (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_name text NOT NULL,
  owner_name text NOT NULL,
  gst_number text,
  industry text,
  preferred_language text DEFAULT 'English'::text,
  whatsapp_number text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT profiles_pkey PRIMARY KEY (id)
);
CREATE TABLE public.sessions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid,
  platform text NOT NULL,
  external_id text NOT NULL,
  is_bot_active boolean DEFAULT true,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT sessions_pkey PRIMARY KEY (id),
  CONSTRAINT sessions_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.shipments (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  invoice_id uuid,
  shiprocket_order_id text,
  awb_number text,
  carrier_name text,
  status text DEFAULT 'processing'::text,
  tracking_url text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT shipments_pkey PRIMARY KEY (id),
  CONSTRAINT shipments_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id)
);
CREATE TABLE public.unified_messages (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  session_id uuid,
  platform text NOT NULL,
  direction text NOT NULL,
  content text,
  external_id text,
  sender_handle text,
  status text DEFAULT 'sent'::text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unified_messages_pkey PRIMARY KEY (id),
  CONSTRAINT unified_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id)
);
CREATE TABLE public.workflow_blueprints (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid,
  name text NOT NULL,
  description text,
  nodes jsonb NOT NULL,
  edges jsonb NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT workflow_blueprints_pkey PRIMARY KEY (id),
  CONSTRAINT workflow_blueprints_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.workflow_logs (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  workflow_id uuid,
  run_id text NOT NULL,
  status text DEFAULT 'running'::text,
  trigger_data jsonb,
  step_results jsonb DEFAULT '{}'::jsonb,
  error_message text,
  started_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone,
  CONSTRAINT workflow_logs_pkey PRIMARY KEY (id),
  CONSTRAINT workflow_logs_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_blueprints(id)
);