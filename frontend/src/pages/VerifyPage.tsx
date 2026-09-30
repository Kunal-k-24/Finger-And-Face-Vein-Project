import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, ScanFace, Loader2, Check } from 'lucide-react';
import { CameraCapture } from '../components/CameraCapture';
import { FingerVeinUpload } from '../components/FingerVeinUpload';
import { apiClient } from '../api/client';

const VERIFY_STEPS = [
  "Extracting Live Face Features...",
  "Extracting Live Vein Features...",
  "Fusing Live Biometric Data...",
  "Retrieving Encrypted Template from DB...",
  "Computing Homomorphic Cosine Similarity...",
  "Decoupling Score & Evaluating Threshold..."
];

export const VerifyPage = () => {
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [veinFile, setVeinFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any>(null);

  const handleVerify = async () => {
    if (!faceFile || !veinFile) {
      setError("Please provide both face and finger vein biometrics.");
      return;
    }

    setLoading(true);
    setCurrentStep(0);
    setError('');
    setResult(null);
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    const formData = new FormData();
    formData.append('username', user.username);
    formData.append('face_image', faceFile);
    formData.append('vein_image', veinFile);

    try {
      const apiPromise = apiClient.post('/biometric/verify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Simulate steps visually for UX
      for (let i = 0; i < VERIFY_STEPS.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 500)); // 500ms per step
      }

      const response = await apiPromise;
      setResult(response.data);
      setCurrentStep(VERIFY_STEPS.length); // Keep steps completed
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed due to an error.');
      setCurrentStep(-1); // Reset on error
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setFaceFile(null);
    setVeinFile(null);
    setError('');
    setCurrentStep(-1);
  };

  return (
    <div className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <ScanFace className="text-brand-500" />
          Verify Identity
        </h1>
        <p className="text-slate-400 mt-2">Authenticate using your face and finger vein. Verification happens homomorphically on encrypted templates.</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-4 rounded-lg mb-8 text-center max-w-3xl mx-auto">
          {error}
        </div>
      )}

      {(loading || currentStep >= 0) && (
        <div className="mb-8 p-6 glass-card border border-brand-500/30 max-w-3xl mx-auto animate-slide-up">
          <h3 className="text-lg font-bold text-white mb-4">Verifying Secure Identity...</h3>
          <div className="space-y-3">
            {VERIFY_STEPS.map((step, index) => {
              const stepData = result?.step_data;
              return (
                <div key={index} className={`flex items-start gap-3 transition-opacity duration-300 ${index > currentStep ? 'opacity-30' : 'opacity-100'}`}>
                  <div className="mt-1">
                    {index < currentStep || (result && index === currentStep) ? (
                      <Check className="text-green-400" size={18} />
                    ) : index === currentStep ? (
                      <Loader2 className="text-brand-400 animate-spin" size={18} />
                    ) : (
                      <div className="w-[18px] h-[18px] rounded-full border-2 border-slate-700" />
                    )}
                  </div>
                  <div>
                    <span className={(index < currentStep || (result && index === currentStep)) ? 'text-slate-300' : index === currentStep ? 'text-white font-medium' : 'text-slate-500'}>
                      {step}
                    </span>
                    {stepData && (index < currentStep || (result && index === currentStep)) && (
                      <div className="text-xs text-brand-400/80 font-mono mt-1">
                        {index === 0 && stepData.face}
                        {index === 1 && stepData.vein}
                        {index === 2 && stepData.fusion}
                        {index === 3 && stepData.db_fetch}
                        {index === 4 && stepData.homomorphic}
                        {index === 5 && stepData.decision}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {result ? (
        <div className="flex flex-col items-center justify-center p-4">
          <div className={`glass-panel p-10 flex flex-col items-center animate-slide-up max-w-lg w-full ${result.authenticated ? 'border-green-500/30' : 'border-red-500/30'}`}>
            <div className={`h-24 w-24 rounded-full flex items-center justify-center border-4 mb-6 ${result.authenticated ? 'bg-green-500/20 border-green-500/50 text-green-400' : 'bg-red-500/20 border-red-500/50 text-red-400'}`}>
              {result.authenticated ? <ShieldCheck className="h-12 w-12" /> : <ShieldAlert className="h-12 w-12" />}
            </div>
            
            <h2 className="text-3xl font-bold text-white mb-2 text-center">
              {result.authenticated ? 'Authentication Granted' : 'Authentication Denied'}
            </h2>
            
            <p className={`text-center mb-8 font-medium ${result.authenticated ? 'text-green-400' : 'text-red-400'}`}>
              {result.message}
            </p>

            <div className="w-full bg-slate-950/50 rounded-lg p-4 space-y-3 mb-8 border border-slate-800">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Similarity Score</span>
                <span className="text-white font-mono font-bold">{(result.similarity_score * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Threshold Required</span>
                <span className="text-white font-mono">{(result.threshold * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Latency</span>
                <span className="text-white font-mono">{result.latency_ms.toFixed(1)} ms</span>
              </div>
            </div>
            
            <button
              onClick={reset}
              className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
            >
              Authenticate Again
            </button>
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
              onClick={handleVerify}
              disabled={!faceFile || !veinFile || loading}
              className="px-8 py-4 bg-brand-600 hover:bg-brand-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-xl font-bold text-lg transition-all flex items-center gap-3 shadow-lg shadow-brand-500/20 disabled:shadow-none"
            >
              {loading ? <Loader2 className="animate-spin" /> : <ShieldCheck />}
              {loading ? 'Processing Cryptography...' : 'Verify Identity'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

