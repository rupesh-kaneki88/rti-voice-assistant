'use client';

import { useState, useEffect } from 'react';
import { updateForm, getForm, generateDocument, getRTIGuidance } from '@/lib/api';

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

  const handleFieldChange = async (field: string, value: string) => {
    try {
      setError(null);
      await updateForm(sessionId, field, value);
      setFormData(prev => ({ ...prev, [field]: value }));
    } catch (err) {
      setError('Failed to update form. Please try again.');
      console.error('Update error:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await generateDocument(sessionId);
      
      alert('RTI Application generated successfully! Check the console for details.');
      console.log('Generated document:', result);
    } catch (err) {
      setError('Failed to generate document. Please try again.');
      console.error('Generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* RTI Guidance */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <button
          onClick={() => setShowGuidance(!showGuidance)}
          className="w-full text-left font-semibold text-blue-900 flex justify-between items-center"
          aria-expanded={showGuidance}
        >
          <span>ℹ️ What is RTI?</span>
          <span>{showGuidance ? '▼' : '▶'}</span>
        </button>
        
        {showGuidance && guidance && (
          <div className="mt-3 text-gray-700 whitespace-pre-wrap">
            {guidance}
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div role="alert" className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Applicant Name */}
        <div>
          <label htmlFor="applicant_name" className="block text-sm font-medium text-gray-700 mb-1">
            Your Name *
          </label>
          <input
            type="text"
            id="applicant_name"
            value={formData.applicant_name || ''}
            onChange={(e) => handleFieldChange('applicant_name', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
            aria-required="true"
          />
        </div>

        {/* Address */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
            Address *
          </label>
          <textarea
            id="address"
            value={formData.address || ''}
            onChange={(e) => handleFieldChange('address', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
            aria-required="true"
          />
        </div>

        {/* Department */}
        <div>
          <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
            Government Department *
          </label>
          <input
            type="text"
            id="department"
            value={formData.department || ''}
            onChange={(e) => handleFieldChange('department', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Ministry of Education"
            required
            aria-required="true"
          />
        </div>

        {/* Information Sought */}
        <div>
          <label htmlFor="information_sought" className="block text-sm font-medium text-gray-700 mb-1">
            Information You Want *
          </label>
          <textarea
            id="information_sought"
            value={formData.information_sought || ''}
            onChange={(e) => handleFieldChange('information_sought', e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Describe what information you are seeking..."
            required
            aria-required="true"
          />
        </div>

        {/* Reason */}
        <div>
          <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-1">
            Reason (Optional)
          </label>
          <textarea
            id="reason"
            value={formData.reason || ''}
            onChange={(e) => handleFieldChange('reason', e.target.value)}
            rows={2}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Why do you need this information?"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-4 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Generating...' : 'Generate RTI Application'}
        </button>
      </form>
    </div>
  );
}
