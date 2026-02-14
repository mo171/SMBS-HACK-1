import { api } from "@/lib/axios";

export const chatService = {
  /**
   * Sends a voice command to the backend intent parser.
   * @param {Blob} audioBlob - The recorded audio file (webm).
   * @param {string} sessionId - The current session ID.
   * @param {string} language - The user's preferred language.
   * @returns {Promise<Object>} - The JSON response from the backend.
   */
  sendVoiceCommand: async (
    audioBlob,
    sessionId = "default_user",
    language = "Marathi",
  ) => {
    const formData = new FormData();
    // Append the file with a filename including extension
    formData.append("audio_file", audioBlob, "voice_command.webm");
    formData.append("session_id", sessionId);
    formData.append("user_lang", language);

    // Axios automatic content-type handling for FormData is usually sufficient,
    // but explicit setting can sometimes be safer depending on the environment.
    // However, Axios sets the boundary correctly when content-type is undefined for FormData.
    const response = await api.post("/intent-parser", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  sendTextCommand: async (text, sessionId) => {
    // Placeholder if text endpoint is different or same
    console.warn("Text command not yet fully implemented in backend");
    return null;
  },

  /**
   * Confirms an invoice.
   * @param {string} invoiceId - The ID of the invoice to confirm.
   */
  confirmInvoice: async (invoiceId) => {
    const response = await api.patch(`/invoices/${invoiceId}/confirm`);
    return response.data;
  },

  /**
   * Deletes an invoice.
   * @param {string} invoiceId - The ID of the invoice to delete.
   */
  deleteInvoice: async (invoiceId) => {
    const response = await api.delete(`/invoices/${invoiceId}`);
    return response.data;
  },

  /**
   * Triggers a file download.
   * @param {string} endpoint - The API endpoint to fetch the file from.
   * @param {string} filename - The name to save the file as.
   */
  downloadFile: async (endpoint, filename) => {
    const response = await api.get(endpoint, {
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  /**
   * Downloads the inventory report as Excel.
   */
  downloadInventory: async () => {
    return chatService.downloadFile("/export/inventory", "inventory.xlsx");
  },

  /**
   * Downloads a specific invoice as PDF.
   * @param {string} invoiceId - The ID of the invoice.
   */
  downloadInvoice: async (invoiceId) => {
    return chatService.downloadFile(
      `/export/invoice/${invoiceId}`,
      `invoice_${invoiceId}.pdf`,
    );
  },

  /**
   * Downloads a specific invoice as Excel.
   * @param {string} invoiceId - The ID of the invoice.
   */
  downloadInvoiceExcel: async (invoiceId) => {
    return chatService.downloadFile(
      `/export/invoice-excel/${invoiceId}`,
      `invoice_${invoiceId}.xlsx`,
    );
  },

  /**
   * Downloads the overall ledger as PDF.
   */
  downloadLedgerPDF: async () => {
    return chatService.downloadFile("/export/overall-ledger", "ledger.pdf");
  },

  /**
   * Downloads the overall ledger as Excel.
   */
  downloadLedgerExcel: async () => {
    return chatService.downloadFile(
      "/export/overall-ledger-excel",
      "ledger.xlsx",
    );
  },

  /**
   * Downloads the aging debtors report as Excel.
   */
  downloadDebtorsExcel: async () => {
    return chatService.downloadFile(
      "/export/aging-debtors",
      "aging_debtors.xlsx",
    );
  },
  /**
   * Confirms a drafted social post.
   */
  confirmSocialPost: async (sessionId, platform, content, imageUrl) => {
    const response = await api.post("/chat/confirm-social", {
      session_id: sessionId,
      platform,
      content,
      image_url: imageUrl,
    });
    return response.data;
  },

  /**
   * Rejects a drafted social post and clears the session.
   */
  rejectSocialPost: async (sessionId) => {
    const response = await api.post("/chat/reject-social", {
      session_id: sessionId,
    });
    return response.data;
  },
};
