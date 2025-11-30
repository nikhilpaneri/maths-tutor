'use client';

import { useState } from 'react';
import WelcomeScreen from './components/WelcomeScreen';
import LearningScreen from './components/LearningScreen';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [studentName, setStudentName] = useState<string>('');

  const handleStartSession = (id: string, name: string) => {
    setSessionId(id);
    setStudentName(name);
  };

  const handleEndSession = () => {
    setSessionId(null);
    setStudentName('');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="container mx-auto px-4 py-8">
        {!sessionId ? (
          <WelcomeScreen onStartSession={handleStartSession} />
        ) : (
          <LearningScreen
            sessionId={sessionId}
            studentName={studentName}
            onEndSession={handleEndSession}
          />
        )}
      </div>
    </main>
  );
}
