'use client';

import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface MathQuestionProps {
  question: string;
  questionData: any;
  sessionId: string;
  onNext: () => void;
}

export default function MathQuestion({
  question,
  questionData,
  sessionId,
  onNext,
}: MathQuestionProps) {
  const [answer, setAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!answer.trim()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/answer/math`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          answer: answer.trim(),
          question_data: questionData,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit answer');
      }

      const data = await response.json();
      setResult(data);
      setSubmitted(true);
    } catch (err) {
      console.error('Error submitting answer:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setAnswer('');
    setSubmitted(false);
    setResult(null);
    onNext();
  };

  if (submitted && result) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="text-8xl mb-4">
            {result.correct ? '🎉' : '💪'}
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            {result.correct ? 'Correct!' : 'Not quite!'}
          </h3>
          <div className={`p-6 rounded-xl mb-4 ${
            result.correct ? 'bg-green-50' : 'bg-blue-50'
          }`}>
            <p className="text-lg text-gray-800 leading-relaxed">
              {result.feedback}
            </p>
            {!result.correct && (
              <p className="mt-2 text-gray-700 font-semibold">
                The correct answer is {result.expected_answer}
              </p>
            )}
          </div>

          {result.bonus_fact && (
            <div className="bg-purple-50 p-6 rounded-xl mb-4">
              <div className="flex items-center justify-center mb-2">
                <span className="text-3xl mr-2">💡</span>
                <h4 className="font-bold text-purple-800">Bonus Fact!</h4>
              </div>
              <p className="text-gray-800">{result.bonus_fact}</p>
            </div>
          )}

          <div className="flex items-center justify-center space-x-4 text-sm text-gray-600 mb-6">
            <div className="bg-gray-100 px-4 py-2 rounded-lg">
              <span className="font-semibold">Total Questions:</span> {result.total_questions}
            </div>
            <div className="bg-gray-100 px-4 py-2 rounded-lg">
              <span className="font-semibold">Accuracy:</span> {result.accuracy.toFixed(1)}%
            </div>
          </div>
        </div>

        <button
          onClick={handleNext}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg"
        >
          Next Activity
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <div className="text-5xl mb-4">🎯</div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">Math Question</h3>
      </div>

      <div className="bg-blue-50 p-6 rounded-xl">
        <p className="text-xl text-gray-800 leading-relaxed text-center">
          {question}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="answer" className="block text-sm font-medium text-gray-700 mb-2">
            Your answer:
          </label>
          <input
            id="answer"
            type="number"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors text-gray-900 text-center text-2xl font-bold"
            placeholder="?"
            disabled={loading}
            autoFocus
          />
        </div>

        <button
          type="submit"
          disabled={loading || !answer.trim()}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
        >
          {loading ? 'Checking...' : 'Submit Answer'}
        </button>
      </form>
    </div>
  );
}
