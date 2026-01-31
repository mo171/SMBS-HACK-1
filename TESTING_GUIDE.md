# Complete Testing Guide: Workflow System with ngrok

## 🚀 **Setup Instructions**

### **1. Environment Setup**

#### **Backend Environment Variables**
Update `backend/app/.env` with your actual credentials:

```bash
# Razorpay Configuration (REQUIRED)
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here

# Existing configurations (already set)
OPENAI_API_KEY=your_openai_key
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_ACCOUNT_SID=your_twilio_sid
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

#### **Get Razorpay Test Credentials**
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Sign up/Login
3. Go to Settings → API Keys
4. Generate Test Keys
5. Copy Key ID and Key Secret to your `.env` file

### **2. Install Dependencies**

#### **Backend Dependencies**
```bash
cd backend
pip install razorpay  # Already installed
```

#### **Frontend Dependencies** (if needed)
```bash
cd frontend/my-app
npm install  # Should already be installed
```

### **3. Start Services**

#### **Terminal 1: Backend Server**
```bash
cd backend/app
python app.py
# Should start on http://127.0.0.1:8000
```

#### **Terminal 2: Frontend Server**
```bash
cd frontend/my-app
npm run dev
# Should start on http://localhost:3000
```

#### **Terminal 3: ngrok for Backend**
```bash
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

#### **Terminal 4: Inngest Dev Server**
```bash
# Install Inngest CLI if not installed
npm install -g inngest-cli

# Start Inngest dev server
inngest-cli dev
# Should start on http://localhost:8288
```

#### **Terminal 5: ngrok for Inngest**
```bash
ngrok http 8288
# Copy the HTTPS URL for Inngest webhooks
```

---

## 🧪 **Testing Scenarios**

### **Test 1: Basic Workflow Generation**

#### **Steps:**
1. Open frontend: `http://localhost:3000`
2. Navigate to Workflows page
3. In the AI prompt box, enter:
   ```
   When a customer makes a payment, create a Razorpay payment link for ₹1000, then send a WhatsApp message with the payment link, and finally update a Google Sheet with the transaction details.
   ```
4. Click "Generate Workflow"

#### **Expected Result:**
- ✅ 3 nodes should appear on canvas:
  - Razorpay node (blue, credit card icon)
  - WhatsApp node (green, message icon)  
  - Google Sheets node (green, spreadsheet icon)
- ✅ Nodes should be connected with edges
- ✅ Success toast message

#### **Troubleshooting:**
- If generation fails: Check OpenAI API key in backend `.env`
- If no nodes appear: Check browser console for errors
- If Supabase errors: Verify Supabase credentials

### **Test 2: Verify Automation (No Manual Configuration)**

#### **Steps:**
1. After generating the workflow, **DO NOT** double-click any nodes
2. The nodes should already be pre-configured with automation variables
3. Switch to "Monitor Mode" 
4. Click "Start Workflow" immediately

#### **Expected Result:**
- ✅ Workflow executes without any manual configuration
- ✅ Razorpay node creates payment link using sample data
- ✅ WhatsApp node sends message with actual payment link
- ✅ Google Sheets node logs transaction data
- ✅ All variable substitutions work automatically:
  - `{{trigger_data.customer_name}}` → "Test Customer"
  - `{{trigger_data.customer_phone}}` → "+919876543210"
  - `{{razorpay_1.payment_url}}` → actual Razorpay payment link

#### **Sample Execution Data:**
The system automatically provides this test data:
```json
{
  "customer_name": "Test Customer",
  "customer_email": "test@example.com",
  "customer_phone": "+919876543210",
  "order_id": "TEST1738234567890",
  "timestamp": "2024-01-30T10:30:00Z",
  "amount": 2500
}
```

### **Test 3: Optional Manual Configuration (Advanced)**

**Only if you want to customize the automation:**

#### **Steps:**
1. Double-click any node to see pre-filled automation values
2. Modify variables if needed (e.g., change phone number, message template)
3. The configuration panel shows the AI-generated automation
4. Save changes if you want to override defaults

### **Test 4: Save Workflow**

#### **Steps:**
1. In the sidebar, enter workflow name: "Payment Processing Workflow"
2. Click "Save Workflow"
3. Check "Saved Workflows" section

#### **Expected Result:**
- ✅ Success toast: "Workflow saved successfully!"
- ✅ Workflow appears in saved workflows list
- ✅ Shows correct node count and date

### **Test 5: Workflow Execution**

#### **Steps:**
1. Click "Monitor Mode" button (top-left of canvas)
2. Click "Start Workflow" button
3. Watch the real-time execution

#### **Expected Result:**
- ✅ Nodes change to monitor mode (different styling)
- ✅ Execution starts with "Running" status
- ✅ Each node shows progress:
  - Blue spinning icon = Running
  - Green checkmark = Completed
  - Red X = Failed
- ✅ Real-time updates via Supabase

#### **Expected Execution Flow:**
1. **Razorpay Node**: Creates payment link
2. **WhatsApp Node**: Sends message with payment link
3. **Google Sheets Node**: Updates spreadsheet

### **Test 6: Error Handling**

#### **Steps:**
1. Create workflow with invalid Razorpay credentials
2. Execute workflow
3. Check error handling

#### **Expected Result:**
- ✅ Node shows "Failed" status (red)
- ✅ Error message visible in node inspection
- ✅ Workflow stops at failed node
- ✅ Error logged in backend console

---

## 🔧 **ngrok Configuration for Webhooks**

### **1. Razorpay Webhook Setup**

#### **Steps:**
1. Get your ngrok backend URL: `https://abc123.ngrok.io`
2. Go to Razorpay Dashboard → Webhooks
3. Add webhook URL: `https://abc123.ngrok.io/webhooks/razorpay`
4. Select events: `payment.captured`, `payment.failed`
5. Save webhook

#### **Test Webhook:**
1. Create a test payment in Razorpay dashboard
2. Check backend logs for webhook received
3. Verify workflow triggers automatically

### **2. Inngest Webhook Setup**

#### **Steps:**
1. Get your ngrok Inngest URL: `https://def456.ngrok.io`
2. Configure Inngest to use ngrok URL for webhooks
3. Update backend Inngest client configuration:

```python
# In workflows/engine.py
inngest_client = Inngest(
    app_id="biz_flow_engine",
    event_key=os.getenv("INNGEST_EVENT_KEY"),
    base_url="https://def456.ngrok.io"  # Your ngrok URL
)
```

### **3. WhatsApp Webhook (Twilio)**

#### **Steps:**
1. Go to Twilio Console → WhatsApp Sandbox
2. Set webhook URL: `https://abc123.ngrok.io/whatsapp`
3. Test by sending WhatsApp message to sandbox number

---

## 📊 **Monitoring & Debugging**

### **Backend Logs to Watch:**
```bash
# Terminal 1 (Backend)
🚀 [/workflow/draft] Endpoint hit
🤖 [WorkflowArchitect] draft_workflow called
✅ [WorkflowArchitect] Blueprint generated successfully
💾 [/workflow/draft] Workflow saved with ID: 123

▶️ [/workflow/execute] Endpoint hit
📡 [/workflow/execute] Sending event to Inngest
✅ [/workflow/execute] Event sent to Inngest

🚀 [WorkflowEngine] execute_workflow function called
🔵 [RazorpayTool] Executing task: create_payment_link
✅ [RazorpayTool] Payment link created: plink_xyz
🔵 [WhatsAppTool] Executing task: send_message
✅ [WhatsAppTool] Message sent successfully
```

### **Frontend Console to Watch:**
```javascript
// Browser Console
🚀 [WorkflowSidebar] Generate button pressed
📡 [WorkflowSidebar] Calling /workflow/draft endpoint
✅ [WorkflowSidebar] Workflow generation complete!

▶️ [WorkflowCanvas] Execute Workflow button pressed
📡 [WorkflowCanvas] Calling /workflow/execute endpoint
🔴 [WorkflowCanvas] Initializing live monitor
📨 [workflowStore] Realtime update received
✅ [workflowStore] Node states updated
```

### **Supabase Tables to Monitor:**
1. **workflow_blueprints**: Saved workflows
2. **workflow_logs**: Execution history
3. **Real-time subscriptions**: Live execution updates

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: Razorpay Tool Not Found**
```
❌ Service 'razorpay' is not integrated
```
**Solution:**
- Check `backend/app/integrations/__init__.py` has `RazorpayTool` import
- Restart backend server
- Verify `razorpay` package installed

### **Issue 2: Node Configuration Not Saving**
```
Configuration panel doesn't update node
```
**Solution:**
- Check browser console for React errors
- Verify `useForm` is working properly
- Check `updateNodeData` function in store

### **Issue 3: Workflow Execution Fails**
```
❌ [WorkflowEngine] Workflow failed with error
```
**Solution:**
- Check Razorpay credentials in `.env`
- Verify Inngest is running
- Check ngrok URLs are accessible
- Review backend logs for specific errors

### **Issue 4: Real-time Updates Not Working**
```
Nodes don't update during execution
```
**Solution:**
- Check Supabase real-time is enabled
- Verify WebSocket connection in browser
- Check `workflow_logs` table permissions
- Restart frontend development server

### **Issue 5: ngrok Connection Issues**
```
ngrok tunnel not accessible
```
**Solution:**
- Restart ngrok with `ngrok http 8000`
- Update webhook URLs with new ngrok URL
- Check ngrok account limits
- Verify firewall settings

---

## ✅ **Success Criteria**

**Your workflow system is working correctly when:**

1. ✅ **AI Generation**: Prompt creates 3 connected nodes (Razorpay → WhatsApp → Google Sheets)
2. ✅ **Node Configuration**: Double-click opens service-specific configuration panels
3. ✅ **Workflow Saving**: Can save and load workflows from sidebar
4. ✅ **Execution**: "Start Workflow" creates payment link, sends WhatsApp, updates sheet
5. ✅ **Real-time Monitoring**: Nodes show live execution status with colors/icons
6. ✅ **Error Handling**: Failed nodes show red status with error details
7. ✅ **Webhooks**: External Razorpay payments trigger workflows automatically

---

## 🎯 **Next Steps After Testing**

Once basic testing works:

1. **Add More Services**: Email, Slack, Database operations
2. **Advanced Features**: Conditional logic, loops, scheduling
3. **Production Setup**: Replace ngrok with proper domain
4. **Security**: Add authentication, rate limiting
5. **Analytics**: Workflow performance metrics
6. **Templates**: Pre-built workflow templates

---

## 📞 **Support**

If you encounter issues:

1. **Check Logs**: Backend terminal and browser console
2. **Verify Credentials**: All API keys in `.env` files
3. **Test Individually**: Each service (Razorpay, WhatsApp, Sheets) separately
4. **Network Issues**: Ensure ngrok tunnels are active
5. **Database**: Check Supabase table structure and permissions

**Your workflow system is now ready for comprehensive testing!** 🚀