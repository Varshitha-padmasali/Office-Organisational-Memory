"use client";

import { useRef, useState } from "react";

/**
 * STATUS: NOT FUNCTIONAL YET. There is no backend upload endpoint (planned
 * Day 2-3). Selecting a file shows an honest "not implemented" notice
 * instead of silently doing nothing or pretending to upload.
 */
export default function DocumentUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [notice, setNotice] = useState<string | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setNotice(
      `Upload isn't implemented yet — "${file.name}" was not sent anywhere. Planned for Day 2-3.`
    );
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center bg-white">
      <p className="text-sm text-gray-600 mb-3">
        Drag and drop files here, or click to select.
      </p>
      <input
        ref={inputRef}
        type="file"
        onChange={handleFileChange}
        className="block mx-auto text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-brand-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100"
      />
      {notice && (
        <div className="mt-4 rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800 inline-block">
          {notice}
        </div>
      )}
    </div>
  );
}
