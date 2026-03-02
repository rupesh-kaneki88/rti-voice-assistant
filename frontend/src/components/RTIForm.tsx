'use client';

import { useState, useEffect } from 'react';
import { updateForm, getForm, generateDocument, getRTIGuidance } from '@/lib/api';

// SVG Icon Components
const InfoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
  </svg>
);

const ChevronIcon = ({ open }: { open: boolean }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={`h-6 w-6 transform transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
);

interface RTIFormProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
}

interface FormData {
  applicant_name?: string;
  address?: string;
  information_sought?: string;
  department?: string;
  reason?: string;
}

export default function RTIForm({ sessionId, language }: RTIFormProps) {
  const [formData, setFormData] = useState<FormData>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [guidance, setGuidance] = useState<string>('');
  const [showGuidance, setShowGuidance] = useState(false);

  useEffect(() => {
    loadFormData();
    loadGuidance();
    
    // Listen for form refresh events
    const handleRefresh = () => {
      loadFormData();
    };
    
    window.addEventListener('refreshForm', handleRefresh);
    
    return () => {
      window.removeEventListener('refreshForm', handleRefresh);
    };
  }, [sessionId]);

  const loadFormData = async () => {
    try {
      const data = await getForm(sessionId);
      setFormData(data.form_data || {});
    } catch (err) {
      console.error('Failed to load form data:', err);
    }
  };

  const loadGuidance = async () => {
    try {
      const result = await getRTIGuidance(language);
      setGuidance(result.explanation);
    } catch (err) {
      console.error('Failed to load guidance:', err);
    }
  };

  const handleFieldChange = async (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    try {
      setError(null);
      await updateForm(sessionId, field, value);
    } catch (err) {
      setError('Failed to save progress. Please check your connection.');
      console.error('Update error:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError(null);
      const result = await generateDocument(sessionId);
      alert('RTI Application generated successfully! Check your downloads or the console.');
      console.log('Generated document:', result);
    } catch (err) {
      setError('Failed to generate document. Please ensure all fields are filled correctly.');
      console.error('Generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formFields: { id: keyof FormData; label: string; type: 'text' | 'textarea'; required: boolean; placeholder: string }[] = [
    { id: 'applicant_name', label: 'Your Full Name', type: 'text', required: true, placeholder: 'e.g., John Doe' },
    { id: 'address', label: 'Your Full Address', type: 'textarea', required: true, placeholder: 'e.g., 123 Main St, Anytown, India' },
    { id: 'department', label: 'Target Government Department', type: 'text', required: true, placeholder: 'e.g., Ministry of Health and Family Welfare' },
    { id: 'information_sought', label: 'Information You Are Seeking', type: 'textarea', required: true, placeholder: 'Clearly describe the information you need...' },
    { id: 'reason', label: 'Reason for Seeking Information (Optional)', type: 'textarea', required: false, placeholder: 'e.g., For public interest, personal matter, etc.' },
  ];

  return (
    <div className="space-y-6">
      {/* RTI Guidance */}
      <div className="bg-neutral-100 border border-neutral-200 rounded-lg">
        <button
          onClick={() => setShowGuidance(!showGuidance)}
          className="w-full p-4 text-left font-semibold text-brand-blue flex justify-between items-center"
          aria-expanded={showGuidance}
        >
          <span className="flex items-center gap-2">
            <InfoIcon />
            What is the RTI Act?
          </span>
          <ChevronIcon open={showGuidance} />
        </button>
        {showGuidance && guidance && (
          <div className="p-4 border-t border-neutral-200 text-neutral-700 whitespace-pre-wrap">
            {guidance}
          </div>
        )}
      </div>

      {error && (
        <div role="alert" className="bg-red-100 border-l-4 border-red-500 text-red-800 p-4 rounded-md font-semibold">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {formFields.map(field => (
          <div key={field.id}>
            <label htmlFor={field.id} className="block text-sm font-bold text-neutral-700 mb-1">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            {field.type === 'textarea' ? (
              <textarea
                id={field.id}
                value={formData[field.id] || ''}
                onChange={(e) => handleFieldChange(field.id, e.target.value)}
                rows={field.id === 'information_sought' ? 4 : 2}
                className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange"
                required={field.required}
                placeholder={field.placeholder}
              />
            ) : (
              <input
                type="text"
                id={field.id}
                value={formData[field.id] || ''}
                onChange={(e) => handleFieldChange(field.id, e.target.value)}
                className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange"
                required={field.required}
                placeholder={field.placeholder}
              />
            )}
          </div>
        ))}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-brand-green hover:bg-brand-green-light text-white font-bold py-3 px-4 rounded-md transition-colors duration-300 focus:outline-none focus:ring-4 focus:ring-brand-green focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-wait"
        >
          {isLoading ? 'Generating Document...' : 'Generate RTI Application'}
        </button>
      </form>
    </div>
  );
}
