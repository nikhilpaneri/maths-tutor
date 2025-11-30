'use client';

interface ProgressBarProps {
  total: number;
  correct: number;
  accuracy: number;
}

export default function ProgressBar({ total, correct, accuracy }: ProgressBarProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-600">{total}</div>
          <div className="text-sm text-gray-600 mt-1">Total Questions</div>
        </div>
        <div className="bg-green-50 p-4 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-600">{correct}</div>
          <div className="text-sm text-gray-600 mt-1">Correct</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-600">
            {accuracy.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600 mt-1">Accuracy</div>
        </div>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
        <div
          className="bg-gradient-to-r from-blue-500 to-purple-600 h-6 rounded-full transition-all duration-500 flex items-center justify-center text-white text-sm font-bold"
          style={{ width: `${Math.max(accuracy, 5)}%` }}
        >
          {accuracy > 10 && `${accuracy.toFixed(0)}%`}
        </div>
      </div>
    </div>
  );
}
