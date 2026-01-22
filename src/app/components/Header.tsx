import { Shield, User, Upload, BarChart3 } from 'lucide-react';

interface HeaderProps {
  currentPage: string;
  onNavigate: (page: 'main' | 'upload' | 'results' | 'mypage') => void;
  showNavigation?: boolean;
}

export function Header({ currentPage, onNavigate, showNavigation = true }: HeaderProps) {
  return (
    <header className="bg-white border-b border-sky-100 shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <button
            onClick={() => onNavigate('main')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-sky-500 to-sky-600 rounded-xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-lg text-gray-800">교통법규 위반 탐지</h1>
            </div>
          </button>

          {/* Navigation */}
          {showNavigation && (
            <nav className="flex items-center gap-2">
              <button
                onClick={() => onNavigate('upload')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'upload'
                    ? 'bg-sky-500 text-white shadow-md'
                    : 'text-gray-600 hover:bg-sky-50 hover:text-sky-600'
                }`}
              >
                <Upload className="w-4 h-4" />
                <span className="text-sm">분석하기</span>
              </button>

              <button
                onClick={() => onNavigate('results')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'results'
                    ? 'bg-sky-500 text-white shadow-md'
                    : 'text-gray-600 hover:bg-sky-50 hover:text-sky-600'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span className="text-sm">결과 보기</span>
              </button>

              <button
                onClick={() => onNavigate('mypage')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  currentPage === 'mypage'
                    ? 'bg-sky-500 text-white shadow-md'
                    : 'text-gray-600 hover:bg-sky-50 hover:text-sky-600'
                }`}
              >
                <User className="w-4 h-4" />
                <span className="text-sm">마이페이지</span>
              </button>
            </nav>
          )}
        </div>
      </div>
    </header>
  );
}
