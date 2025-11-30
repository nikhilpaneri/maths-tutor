'use client';

import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
console.log('API_URL:', API_URL);

interface WelcomeScreenProps {
  onStartSession: (sessionId: string, studentName: string) => void;
}

export default function WelcomeScreen({ onStartSession }: WelcomeScreenProps) {
  const [studentName, setStudentName] = useState('');
  const [maxTimestable, setMaxTimestable] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!studentName.trim()) {
      setError('Please enter your name!');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const url = `${API_URL}/api/session/start`;
      console.log('Fetching:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_name: studentName.trim(),
          max_timestable: maxTimestable,
        }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error('Failed to start session');
      }

      const data = await response.json();
      console.log('Response data:', data);
      onStartSession(data.session_id, studentName.trim());
    } catch (err) {
      console.error('Full error:', err);
      setError('Oops! Could not start the session. Make sure the backend is running!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-3">
            Timestable Tutor
          </h1>
          <p className="text-gray-600 text-lg">
            Learn your timestables with fun facts!
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              What's your name?
            </label>
            <input
              id="name"
              type="text"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors text-gray-900"
              placeholder="Enter your name"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="level" className="block text-sm font-medium text-gray-700 mb-2">
              Which timestable do you want to learn up to?
            </label>
            <select
              id="level"
              value={maxTimestable}
              onChange={(e) => setMaxTimestable(Number(e.target.value))}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors text-gray-900"
              disabled={loading}
            >
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  {i + 1} times table
                </option>
              ))}
            </select>
          </div>

          {error && (
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-3 text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
          >
            {loading ? 'Starting...' : "Let's Start Learning!"}
          </button>
        </form>

        <div className="mt-8 text-center">
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center">
              <span className="text-2xl mr-2">🎯</span>
              <span>Math Questions</span>
            </div>
            <div className="flex items-center">
              <span className="text-2xl mr-2">🌟</span>
              <span>Fun Facts</span>
            </div>
            <div className="flex items-center">
              <span className="text-2xl mr-2">🎮</span>
              <span>Quizzes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
