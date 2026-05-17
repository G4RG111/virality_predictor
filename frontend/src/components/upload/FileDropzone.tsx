"use client";

import { useRef, useState, DragEvent, ChangeEvent } from "react";
import { Upload, File, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  accept: string;
  label: string;
  onFile: (file: File) => void;
  disabled?: boolean;
}

export function FileDropzone({ accept, label, onFile, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleFile = (file: File) => {
    setSelectedFile(file);
    onFile(file);
  };

  const clear = () => {
    setSelectedFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div>
      <input ref={inputRef} type="file" accept={accept} className="hidden" onChange={handleChange} disabled={disabled} />
      {selectedFile ? (
        <div className="flex items-center gap-3 rounded border border-emerald-200 bg-emerald-50 p-3.5">
          <File className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span className="text-[13px] text-[#333333] flex-1 truncate">{selectedFile.name}</span>
          <span className="text-[11px] text-[#999999]">{(selectedFile.size / 1024 / 1024).toFixed(1)} MB</span>
          <button onClick={clear} className="text-[#BBBBBB] hover:text-red-500 transition-colors">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ) : (
        <div
          onClick={() => !disabled && inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={cn(
            "rounded border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200",
            dragging
              ? "border-[#E41E26]/40 bg-[#FFF8F8]"
              : "border-[#E5E5E5] hover:border-[#CCCCCC] hover:bg-[#FAFAFA]",
            disabled && "opacity-40 cursor-not-allowed",
          )}
        >
          <Upload className="w-6 h-6 text-[#CCCCCC] mx-auto mb-3" />
          <p className="text-[13px] font-medium text-[#555555]">{label}</p>
          <p className="text-[11px] text-[#BBBBBB] mt-1">Drag & drop or click to browse</p>
          <p className="text-[10px] text-[#CCCCCC] mt-1 font-mono">{accept}</p>
        </div>
      )}
    </div>
  );
}
