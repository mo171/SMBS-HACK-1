import { useState, useRef, useCallback } from "react";

export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const chunksRef = useRef([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm", // Use webm as it's widely supported and acceptable by Whisper
      });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      // You might want to handle this error in the UI
    }
  }, []);

  const stopRecording = useCallback(() => {
    return new Promise((resolve) => {
      if (!mediaRecorder) {
        resolve(null);
        return;
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = []; // Clear chunks for next recording
        setIsRecording(false);
        setMediaRecorder(null);

        // Stop all tracks to release microphone
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());

        resolve(audioBlob);
      };

      mediaRecorder.stop();
    });
  }, [mediaRecorder]);

  return {
    isRecording,
    startRecording,
    stopRecording,
  };
}
