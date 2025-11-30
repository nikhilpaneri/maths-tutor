'use client';

interface FunFactProps {
  fact: string;
  category: string;
  onNext: () => void;
}

export default function FunFact({ fact, category, onNext }: FunFactProps) {
  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <div className="text-5xl mb-4">🌟</div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">Fun Fact!</h3>
        <div className="inline-block bg-purple-100 text-purple-700 px-4 py-1 rounded-full text-sm font-medium">
          {category}
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-8 rounded-xl border-2 border-purple-200">
        <p className="text-xl text-gray-800 leading-relaxed text-center">
          {fact}
        </p>
      </div>

      <div className="text-center text-sm text-gray-500">
        Take a moment to enjoy this interesting fact!
      </div>

      <button
        onClick={onNext}
        className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white font-semibold py-4 rounded-xl hover:from-purple-600 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg"
      >
        Continue Learning
      </button>
    </div>
  );
}
