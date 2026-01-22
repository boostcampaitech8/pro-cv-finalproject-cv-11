import { AnalysisDashboard, AnalysisResult } from './AnalysisDashboard';
import { Header } from './Header';

interface ResultsPageProps {
  results: AnalysisResult[];
  onNavigate: (page: 'main' | 'upload' | 'results' | 'mypage') => void;
}

export function ResultsPage({ results, onNavigate }: ResultsPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-50">
      {/* Header */}
      <Header currentPage="results" onNavigate={onNavigate} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h2 className="text-gray-800 mb-2">분석 결과</h2>
          <p className="text-gray-600">
            총 {results.length}건의 위반 행위가 탐지되었습니다
          </p>
        </div>

        {results.length > 0 ? (
          <AnalysisDashboard results={results} />
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-sky-100 p-12 text-center">
            <div className="w-16 h-16 bg-sky-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-sky-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h2 className="text-gray-800 mb-2">위반 행위가 탐지되지 않았습니다</h2>
            <p className="text-gray-600 mb-6">
              선택한 이벤트 유형에 해당하는 위반 행위가 발견되지 않았습니다.
            </p>
            <button
              onClick={() => onNavigate('upload')}
              className="px-6 py-3 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors"
            >
              새로운 분석 시작하기
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-sky-100 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-sm text-gray-500">
          <p>© 2026 교통법규 위반 자동 탐지 시스템. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}