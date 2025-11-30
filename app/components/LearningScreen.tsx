'use client';

import { useState, useEffect } from 'react';
import MathQuestion from './MathQuestion';
import FunFact from './FunFact';
import FactQuiz from './FactQuiz';
import ProgressBar from './ProgressBar';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LearningScreenProps {
  sessionId: string;
  studentName: string;
  onEndSession: () => void;
}

interface Activity {
  type?: string;
  question?: string;
  timestable?: number;
  multiplier?: number;
  expected_answer?: number;
  content?: string;
  category?: string;
  options?: Record<string, string>;
  correct_answer?: string;
  explanation?: string;
  number?: number;
}

export default function LearningScreen({
  sessionId,
  studentName,
  onEndSession,
}: LearningScreenProps) {
  const [activity, setActivity] = useState<Activity | null>(null);
  const [loading, setLoading] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState<any>(null);
  const [showProgress, setShowProgress] = useState(false);

  useEffect(() => {
    loadNextActivity();
  }, []);

  const loadNextActivity = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/activity/next`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to load activity');
      }

      const data = await response.json();
      setActivity(data);
    } catch (err) {
      console.error('Error loading activity:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseResume = async () => {
    try {
      const endpoint = isPaused ? 'resume' : 'pause';
      const response = await fetch(`${API_URL}/api/session/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to ${endpoint} session`);
      }

      setIsPaused(!isPaused);
    } catch (err) {
      console.error('Error pausing/resuming:', err);
    }
  };

  const loadProgress = async () => {
    try {
      const response = await fetch(`${API_URL}/api/session/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to load progress');
      }

      const data = await response.json();
      setProgress(data);
      setShowProgress(true);
    } catch (err) {
      console.error('Error loading progress:', err);
    }
  };

  const handleEndSession = async () => {
    try {
      const response = await fetch(`${API_URL}/api/session/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to end session');
      }

      const data = await response.json();
      alert(data.message);
      onEndSession();
    } catch (err) {
      console.error('Error ending session:', err);
      onEndSession();
    }
  };

  if (loading && !activity) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading your next activity...</p>
        </div>
      </div>
    );
  }

  if (isPaused) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 max-w-md w-full text-center">
          <div className="text-6xl mb-4">⏸️</div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Session Paused</h2>
          <p className="text-gray-600 mb-6">Take a break, {studentName}!</p>
          <button
            onClick={handlePauseResume}
            className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-4 rounded-xl hover:from-green-600 hover:to-teal-700 transition-all transform hover:scale-105 shadow-lg"
          >
            Resume Learning
          </button>
        </div>
      </div>
    );
  }

  if (showProgress && progress) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Your Progress
          </h2>

          <div className="space-y-6">
            <ProgressBar
              total={progress.total_questions}
              correct={progress.correct_answers}
              accuracy={progress.accuracy}
            />

            <div className="bg-blue-50 rounded-xl p-6">
              <p className="text-gray-800 text-lg leading-relaxed">
                {progress.summary}
              </p>
            </div>

            {progress.weak_areas && progress.weak_areas.length > 0 && (
              <div className="bg-yellow-50 rounded-xl p-6">
                <h3 className="font-semibold text-gray-800 mb-2">
                  Areas to practice:
                </h3>
                <div className="flex gap-2 flex-wrap">
                  {progress.weak_areas.map((table: number) => (
                    <span
                      key={table}
                      className="bg-yellow-200 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {table}x table
                    </span>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => setShowProgress(false)}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-4 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg"
            >
              Continue Learning
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-t-3xl shadow-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-bold text-gray-800">
              Hi, {studentName}!
            </h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadProgress}
              className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
            >
              View Progress
            </button>
            <button
              onClick={handlePauseResume}
              className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-sm font-medium"
            >
              Pause
            </button>
            <button
              onClick={handleEndSession}
              className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium"
            >
              End Session
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
        {activity && (
          <>
            {activity.type === 'fact' && (
              <FunFact
                fact={activity.content || ''}
                category={activity.category || ''}
                onNext={loadNextActivity}
              />
            )}

            {activity.type === 'number_fact' && (
              <FunFact
                fact={activity.content || ''}
                category={`Number ${activity.number}`}
                onNext={loadNextActivity}
              />
            )}

            {activity.type === 'quiz' && (
              <FactQuiz
                question={activity.question || ''}
                options={activity.options || {}}
                correctAnswer={activity.correct_answer || ''}
                explanation={activity.explanation || ''}
                category={activity.category || ''}
                quizData={activity}
                sessionId={sessionId}
                onNext={loadNextActivity}
              />
            )}

            {!activity.type && activity.question && (
              <MathQuestion
                question={activity.question}
                questionData={activity}
                sessionId={sessionId}
                onNext={loadNextActivity}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
