# Social Media Expansion Plan

This plan details the integration of Bluesky (Lightweight) and Instagram (Advanced) for marketing and customer engagement.

## 🦋 Phase 1: Bluesky Integration (Quick Win)

Bluesky uses the AT Protocol and is excellent for rapid "Deal of the Day" broadcasts.

### 1. Credentials Needed

- **Handle**: Your Bluesky username (e.g., `user.bsky.social`).
- **App Password**: Created in _Settings > App Passwords_ (Do NOT use your main password).

### 2. Implementation Steps

- **[NEW]** `integrations/bluesky_tool.py`:
  - `post_content`: Send text/image updates.
  - `read_mentions`: Fetch recent comments for the agent to reply to.
- **[MODIFY]** `TOOL_REGISTRY`: Register the `bluesky` service.
- **[MODIFY]** `WorkflowArchitect`: Update prompt to handle social posting intents.

---

## 📸 Phase 2: Instagram Business Integration (Advanced)

This enables "Conversational Commerce"—chatting with customers and taking orders directly on IG.

### 1. Prerequisites (Crucial)

You must perform these steps in the [Facebook Developer Console](https://developers.facebook.com/):

1. **Business Account**: Your Instagram must be a **Professional/Business Account**.
2. **Linked Page**: Connect your Instagram to a **Facebook Page**.
3. **App Setup**: Create a Meta App with the "Instagram Graph API" product.
4. **Permissions**: You will need `instagram_manage_messages` and `pages_manage_metadata` (for webhooks).

### 2. Credentials Needed

- `INSTAGRAM_BUSINESS_ID`: Found in Facebook Page settings.
- `IG_ACCESS_TOKEN`: A Long-lived User Access Token.
- `IG_VERIFY_TOKEN`: A secret string you define for webhooks.

### 3. Implementation Steps (Chunks)

- **Chunk 1: Basics**: Implement `instagram_tool.py` for basic posting of "Grid Posts".
- **Chunk 2: Messaging Node**: Add logic to send DMs via the Workflow Engine.
- **Chunk 3: Human Takeover Logic**:
  - Implement a `is_bot_active` flag in Supabase `sessions`.
  - Create an endpoint `POST /instagram/takeover` to pause the AI so you can chat manually.
- **Chunk 4: Order Intent**: Update `IntentService` to detect "Size/Color" and "Quantity" from IG DMs to create Invoices.

---

## 📂 3. Folder & File Structure

- `backend/app/integrations/bluesky_tool.py`
- `backend/app/integrations/instagram_tool.py`
- `backend/app/tests/test_social.py`
- `backend/app/webhooks/instagram.py` (For real-time chat replies)

---

## 🖥️ Phase 3: Omni-channel Command Center (Phase 3)

A unified dashboard for the shop owner to visualize presence and manage high-stakes conversations.

### 1. Unified Message Architecture

Instead of checking each app, we sync everything to a Supabase table:

- **`unified_messages` Table**: `id`, `platform` (IG/BSKY), `sender_id`, `text`, `status` (Bot/Human), `session_id`.

### 2. Core Features (Roadmap)

- **Unified Inbox**: See all Bluesky mentions and Instagram DMs in one real-time thread.
- **Agent Supervised Mode**: The UI shows what the agent _wants_ to say. The owner can click "Approve" or edit the reply.
- **The Kill Switch**: A "Takeover" button that pauses the AI for 30 minutes so the owner can handle a complex sale manually.
- **Visual Analytics**: Quick stats like "Total DMs Today", "Successful Orders from IG", and "Sentiment of Comments".

### 3. Implementation Steps

- **Step 1: DB Sync**: Create workers that fetch new messages/mentions and write to `unified_messages`.
- **Step 2: WebSocket Layer**: Real-time push to the dashboard using Supabase Realtime or Socket.io.
- **Step 3: Frontend Interface**: A "Command Center" page with:
  - Sidebar for unread platform counts.
  - Central chat window with "AI Intention" previews.
  - "Close Sale" shortcut buttons that trigger `ActionService` directly.

## 🔄 4. How it works with Nodes

- **Trigger**: "Comment on my post" or "New DM received".
- **Node 1**: `instagram` tool reads the message.
- **Node 2**: `IntentService` parses the intent (Check Stock? Order?).
- **Node 3**: `ActionService` confirms stock.
- **Node 4**: `instagram` tool sends back: "Yes, we have Red Paint! Click here to pay: {{razorpay_1.url}}".
