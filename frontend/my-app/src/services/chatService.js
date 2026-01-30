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
};
