import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Fingerprint, UploadCloud, Loader2, CheckCircle, Check } from 'lucide-react';
import { CameraCapture } from '../components/CameraCapture';
import { FingerVeinUpload } from '../components/FingerVeinUpload';
import { apiClient } from '../api/client';

const ENROLL_STEPS = [
  "Extracting Face Features (ResNet-18)...",
  "Extracting Vein Features (ResNet-18)...",
  "Fusing Biometric Data (256-d)...",
  "Applying Homomorphic Encryption (TenSEAL)...",
  "Storing Encrypted Template..."
];

export const EnrollPage = () => {
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [veinFile, setVeinFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [stepData, setStepData] = useState<any>(null);
  const navigate = useNavigate();

  const handleEnroll = async () => {
    if (!faceFile || !veinFile) {
      setError("Please provide both face and finger vein biometrics.");
      return;
    }

    setLoading(true);
    setCurrentStep(0);
    setError('');
    
    const formData = new FormData();
    formData.append('face_image', faceFile);
    formData.append('vein_image', veinFile);

    try {
      // Fire API call in background
      const apiPromise = apiClient.post('/biometric/enroll', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Simulate steps for UX visually
      for (let i = 0; i < ENROLL_STEPS.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 600)); // 600ms per step
      }

      const response = await apiPromise; // Ensure API actually finished
      if (response.data?.step_data) {
        setStepData(response.data.step_data);
      }
      setSuccess(true);
      setCurrentStep(ENROLL_STEPS.length); // Keep steps visible
      setTimeout(() => navigate('/'), 4000); 
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Enrollment failed. Ensure images are clear and valid.');
      setCurrentStep(-1);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Shield className="text-brand-500" />
          Biometric Enrollment
        </h1>
        <p className="text-slate-400 mt-2">Capture your face and finger vein for highly secure, privacy-preserving authentication.</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-4 rounded-lg mb-8 text-center max-w-3xl mx-auto">
          {error}
        </div>
      )}

      {(loading || currentStep >= 0) && (
        <div className="mb-8 p-6 glass-card border border-brand-500/30 max-w-3xl mx-auto animate-slide-up">
          <h3 className="text-lg font-bold text-white mb-4">Processing Identity...</h3>
          <div className="space-y-3">
            {ENROLL_STEPS.map((step, index) => (
              <div key={index} className={`flex items-start gap-3 transition-opacity duration-300 ${index > currentStep ? 'opacity-30' : 'opacity-100'}`}>
                <div className="mt-1">
                  {index < currentStep || (success && index === currentStep) ? (
                    <Check className="text-green-400" size={18} />
                  ) : index === currentStep ? (
                    <Loader2 className="text-brand-400 animate-spin" size={18} />
                  ) : (
                    <div className="w-[18px] h-[18px] rounded-full border-2 border-slate-700" />
                  )}
                </div>
                <div>
                  <span className={(index < currentStep || (success && index === currentStep)) ? 'text-slate-300' : index === currentStep ? 'text-white font-medium' : 'text-slate-500'}>
                    {step}
                  </span>
                  {stepData && (index < currentStep || (success && index === currentStep)) && (
                    <div className="text-xs text-brand-400/80 font-mono mt-1">
                      {index === 0 && stepData.face}
                      {index === 1 && stepData.vein}
                      {index === 2 && stepData.fusion}
                      {index === 3 && stepData.encryption}
                      {index === 4 && stepData.storage}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {success ? (
        <div className="flex flex-col items-center justify-center p-4 mt-8">
          <div className="glass-panel p-12 flex flex-col items-center animate-slide-up">
            <div className="h-20 w-20 bg-green-500/20 rounded-full flex items-center justify-center border border-green-500/50 mb-6">
              <CheckCircle className="h-10 w-10 text-green-400" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-2">Enrollment Successful</h2>
            <p className="text-slate-400 text-center max-w-sm">
              Your multibiometric template has been homomorphically encrypted and securely stored. Redirecting...
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className={`grid md:grid-cols-2 gap-8 mb-8 transition-opacity ${loading ? 'opacity-50 pointer-events-none' : ''}`}>
            <CameraCapture onCapture={setFaceFile} />
            <FingerVeinUpload onUpload={setVeinFile} />
          </div>

          <div className="flex justify-center mt-12">
            <button
              onClick={handleEnroll}
              disabled={!faceFile || !veinFile || loading}
              className="px-8 py-4 bg-brand-600 hover:bg-brand-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-xl font-bold text-lg transition-all flex items-center gap-3 shadow-lg shadow-brand-500/20 disabled:shadow-none"
            >
              {loading ? <Loader2 className="animate-spin" /> : <UploadCloud />}
              {loading ? 'Encrypting & Storing...' : 'Enroll Biometrics'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

