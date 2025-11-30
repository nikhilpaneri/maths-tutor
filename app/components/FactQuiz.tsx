'use client';

import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FactQuizProps {
  question: string;
  options: Record<string, string>;
  correctAnswer: string;
  explanation: string;
  category: string;
  quizData: any;
  sessionId: string;
  onNext: () => void;
}

export default function FactQuiz({
  question,
  options,
  correctAnswer,
  explanation,
  category,
  quizData,
  sessionId,
  onNext,
}: FactQuizProps) {
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedAnswer) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/answer/quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          answer: selectedAnswer,
          quiz_data: quizData,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit quiz answer');
      }

      const data = await response.json();
      setResult(data);
      setSubmitted(true);
    } catch (err) {
      console.error('Error submitting quiz answer:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setSelectedAnswer('');
    setSubmitted(false);
    setResult(null);
    onNext();
  };

  if (submitted && result) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="text-8xl mb-4">
            {result.correct ? '🎊' : '🤔'}
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            {result.correct ? 'Amazing!' : 'Good try!'}
          </h3>
          <div className={`p-6 rounded-xl mb-4 ${
            result.correct ? 'bg-green-50' : 'bg-blue-50'
          }`}>
            <p className="text-lg text-gray-800 leading-relaxed mb-2">
              {result.feedback}
            </p>
            {!result.correct && (
              <p className="text-gray-700 font-semibold">
                The correct answer was: {result.correct_answer}
              </p>
            )}
          </div>

          {result.explanation && (
            <div className="bg-purple-50 p-6 rounded-xl">
              <h4 className="font-bold text-purple-800 mb-2">Did you know?</h4>
              <p className="text-gray-800">{result.explanation}</p>
            </div>
          )}
        </div>

        <button
          onClick={handleNext}
          className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-4 rounded-xl hover:from-green-600 hover:to-teal-700 transition-all transform hover:scale-105 shadow-lg"
        >
          Next Activity
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <div className="text-5xl mb-4">🎮</div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">Fun Quiz!</h3>
        <div className="inline-block bg-green-100 text-green-700 px-4 py-1 rounded-full text-sm font-medium">
          {category}
        </div>
      </div>

      <div className="bg-green-50 p-6 rounded-xl">
        <p className="text-xl text-gray-800 leading-relaxed text-center">
          {question}
        </p>
      </div>

      <div className="space-y-3">
        {Object.entries(options).map(([key, value]) => (
          <button
            key={key}
            onClick={() => setSelectedAnswer(key)}
            className={`w-full p-4 rounded-xl text-left transition-all transform hover:scale-102 ${
              selectedAnswer === key
                ? 'bg-green-500 text-white shadow-lg'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
            disabled={loading}
          >
            <span className="font-bold mr-2">{key})</span>
            {value}
          </button>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !selectedAnswer}
        className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-4 rounded-xl hover:from-green-600 hover:to-teal-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
      >
        {loading ? 'Checking...' : 'Submit Answer'}
      </button>
    </div>
  );
}
