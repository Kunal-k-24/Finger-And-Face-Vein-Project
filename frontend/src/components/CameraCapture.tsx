import React, { useRef, useState, useCallback } from 'react';
import { Camera, RefreshCw, Image as ImageIcon } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
}

export const CameraCapture: React.FC<CameraCaptureProps> = ({ onCapture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isStreamActive, setIsStreamActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsStreamActive(true);
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Could not access camera. Please ensure you have given permission.");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsStreamActive(false);
    }
  };

  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], "face_capture.jpg", { type: "image/jpeg" });
            const imageUrl = URL.createObjectURL(blob);
            setCapturedImage(imageUrl);
            onCapture(file);
            stopCamera();
          }
        }, 'image/jpeg', 0.9);
      }
    }
  }, [onCapture]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const imageUrl = URL.createObjectURL(file);
      setCapturedImage(imageUrl);
      onCapture(file);
      stopCamera();
    }
  };

  const retake = () => {
    setCapturedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-4 glass-card">
      <h3 className="text-lg font-semibold text-slate-200">Face Scan</h3>
      
      <div className="relative w-full max-w-sm aspect-video bg-slate-900 rounded-lg overflow-hidden flex flex-col items-center justify-center border border-slate-700">
        {!capturedImage ? (
          <>
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              className={`absolute inset-0 w-full h-full object-cover ${isStreamActive ? 'block' : 'hidden'}`}
            />
            {!isStreamActive && (
              <div className="flex items-center justify-center gap-8 h-full w-full bg-slate-900/50">
                <button 
                  type="button"
                  onClick={startCamera}
                  className="flex flex-col items-center gap-2 text-slate-400 hover:text-brand-400 transition-colors"
                >
                  <Camera size={36} />
                  <span className="text-sm font-medium">Camera</span>
                </button>
                <div className="w-px h-12 bg-slate-700" />
                <button 
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex flex-col items-center gap-2 text-slate-400 hover:text-brand-400 transition-colors"
                >
                  <ImageIcon size={36} />
                  <span className="text-sm font-medium">Upload</span>
                </button>
                <input 
                  type="file" 
                  ref={fileInputRef}
                  accept="image/*" 
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>
            )}
          </>
        ) : (
          <img src={capturedImage} alt="Captured face" className="w-full h-full object-cover" />
        )}
        <canvas ref={canvasRef} className="hidden" />
      </div>

      <div className="flex gap-4">
        {isStreamActive && !capturedImage && (
          <button 
            type="button"
            onClick={capturePhoto}
            className="px-6 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg font-medium transition-colors"
          >
            Capture Photo
          </button>
        )}
        
        {capturedImage && (
          <button 
            type="button"
            onClick={retake}
            className="flex items-center gap-2 px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
          >
            <RefreshCw size={18} />
            Reset
          </button>
        )}
      </div>
    </div>
  );
};
