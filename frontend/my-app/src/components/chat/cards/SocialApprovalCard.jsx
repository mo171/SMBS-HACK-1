import React, { useState } from "react";
import {
  Share2,
  Check,
  X,
  Edit2,
  Image as ImageIcon,
  ExternalLink,
  Loader2,
} from "lucide-react";

export default function SocialApprovalCard({ data, onConfirm, onReject }) {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(data?.content || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState("pending"); // pending, approved, rejected
  const [postUrl, setPostUrl] = useState(null);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      const result = await onConfirm(content);
      if (result && result.url) {
        setPostUrl(result.url);
      }
      setStatus("approved");
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      await onReject();
      setStatus("rejected");
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (status === "approved") {
    return (
      <div className="mt-3 w-full max-w-[320px] bg-green-500/10 border border-green-500/20 rounded-xl p-5 flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center shadow-lg shadow-green-500/20">
            <Check className="w-4 h-4 text-white" />
          </div>
          <p className="text-sm font-semibold text-white">
            Published Successfully!
          </p>
        </div>

        {postUrl && (
          <a
            href={postUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-green-600/10 mt-1"
          >
            <ExternalLink className="w-3 h-3" />
            View Live Post
          </a>
        )}
      </div>
    );
  }

  if (status === "rejected") {
    return (
      <div className="mt-3 w-full max-w-[320px] bg-red-500/10 border border-red-500/20 rounded-xl p-5 flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center">
            <X className="w-4 h-4 text-white" />
          </div>
          <p className="text-sm font-semibold text-white">
            Post Rejected & Deleted.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-3 w-full max-w-[320px] bg-[#0F1016] border border-white/5 rounded-xl p-5 flex flex-col gap-4 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-pink-500/10 flex items-center justify-center">
            <Share2 className="w-5 h-5 text-pink-500" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white capitalize">
              {data?.platform} Draft
            </h3>
            <p className="text-[10px] text-gray-400">Review before posting</p>
          </div>
        </div>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="p-2 hover:bg-white/5 rounded-lg transition-colors"
        >
          <Edit2
            className={`w-4 h-4 ${isEditing ? "text-blue-400" : "text-gray-400"}`}
          />
        </button>
      </div>

      {/* Media Preview (if any) */}
      {data?.image_url && (
        <div className="relative w-full aspect-video rounded-lg overflow-hidden bg-white/5 border border-white/5">
          {data.image_url === "default" ? (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2 text-gray-500">
              <ImageIcon className="w-8 h-8" />
              <span className="text-[10px]">Using Default Image</span>
            </div>
          ) : (
            <img
              src={data.image_url}
              alt="Social Preview"
              className="w-full h-full object-cover"
            />
          )}
        </div>
      )}

      {/* Content */}
      <div className="flex flex-col gap-2">
        {isEditing ? (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full bg-[#1A1B23] border border-white/10 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-blue-500/50 min-h-[80px]"
            placeholder="Edit post content..."
          />
        ) : (
          <p className="text-xs text-gray-300 leading-relaxed italic border-l-2 border-pink-500/30 pl-3">
            "{content}"
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          disabled={isSubmitting}
          onClick={handleReject}
          className="flex-1 py-2.5 rounded-lg text-xs font-semibold border border-red-500/20 text-red-400 hover:bg-red-500/5 transition-colors disabled:opacity-50"
        >
          Reject
        </button>
        <button
          disabled={isSubmitting}
          onClick={handleApprove}
          className="flex-[2] py-2.5 rounded-lg text-xs font-semibold bg-pink-600 hover:bg-pink-700 text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-pink-600/10 disabled:opacity-50"
        >
          {isSubmitting ? (
            <Loader2 className="w-3 h-3 animate-spin" />
          ) : (
            <Check className="w-3 h-3" />
          )}
          {isEditing ? "Save & Approve" : "Approve & Post"}
        </button>
      </div>
    </div>
  );
}
