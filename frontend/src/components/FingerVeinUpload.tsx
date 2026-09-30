import React, { useCallback, useState } from 'react';
import { Upload, FileImage, X } from 'lucide-react';

interface FingerVeinUploadProps {
  onUpload: (file: File) => void;
}

export const FingerVeinUpload: React.FC<FingerVeinUploadProps> = ({ onUpload }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      onUpload(file);
    }
  }, [onUpload]);

  const clearFile = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
  };

  return (
    <div className="flex flex-col items-center gap-4 p-4 glass-card">
      <h3 className="text-lg font-semibold text-slate-200">Finger Vein Scan</h3>
      
      {!selectedFile ? (
        <div className="w-full max-w-sm aspect-video border-2 border-dashed border-slate-600 rounded-lg flex flex-col items-center justify-center p-6 text-slate-400 hover:border-brand-500 hover:text-brand-400 transition-colors bg-slate-900/50 cursor-pointer relative">
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <Upload size={48} className="mb-4" />
          <p className="text-center text-sm font-medium">Click or drag image to upload finger vein scan</p>
        </div>
      ) : (
        <div className="w-full max-w-sm aspect-video bg-slate-900 rounded-lg overflow-hidden border border-slate-700 relative group">
          <img 
            src={previewUrl!} 
            alt="Finger vein preview" 
            className="w-full h-full object-cover filter grayscale"
          />
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
            <button 
              type="button"
              onClick={clearFile}
              className="p-3 bg-red-500/80 hover:bg-red-500 text-white rounded-full transition-colors"
            >
              <X size={24} />
            </button>
          </div>
          <div className="absolute bottom-0 inset-x-0 p-2 bg-slate-900/90 flex items-center gap-2">
            <FileImage size={16} className="text-brand-400" />
            <span className="text-xs text-slate-300 truncate">{selectedFile.name}</span>
          </div>
        </div>
      )}
    </div>
  );
};
