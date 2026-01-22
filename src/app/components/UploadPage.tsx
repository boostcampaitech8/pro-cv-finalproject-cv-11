import { Sparkles } from 'lucide-react';
import { UploadSection } from './UploadSection';
import { EventSettings } from './EventSettings';
import { Header } from './Header';

interface UploadPageProps {
  uploadedFiles: File[];
  onFilesUpload: (files: File[]) => void;
  selectedEvents: string[];
  onEventToggle: (event: string) => void;
  onAnalyze: () => void;
  onNavigate: (page: 'main' | 'upload' | 'results' | 'mypage') => void;
  isAnalyzing: boolean;
}

export function UploadPage({
  uploadedFiles,
  onFilesUpload,
  selectedEvents,
  onEventToggle,
  onAnalyze,
  onNavigate,
  isAnalyzing,
}: UploadPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-50">
      {/* Header */}
      <Header currentPage="upload" onNavigate={onNavigate} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        <div className="mb-4">
          <h2 className="text-gray-800 mb-2">영상 분석하기</h2>
          <p className="text-gray-600">분석할 영상과 위험 이벤트를 선택하세요</p>
        </div>

        {/* Upload Section */}
        <UploadSection
          onFilesUpload={onFilesUpload}
          uploadedFiles={uploadedFiles}
        />

        {/* Event Settings */}
        <EventSettings
          selectedEvents={selectedEvents}
          onEventToggle={onEventToggle}
        />

        {/* Analyze Button */}
        <div className="flex justify-center pt-4">
          <button
            onClick={onAnalyze}
            disabled={uploadedFiles.length === 0 || selectedEvents.length === 0 || isAnalyzing}
            className={`px-10 py-5 rounded-2xl transition-all flex items-center gap-3 text-lg ${
              uploadedFiles.length === 0 || selectedEvents.length === 0 || isAnalyzing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-sky-500 to-sky-600 text-white hover:from-sky-600 hover:to-sky-700 shadow-xl hover:shadow-2xl transform hover:scale-105'
            }`}
          >
            <Sparkles className={`w-6 h-6 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>
              {isAnalyzing ? '영상 분석 중...' : '영상 분석 시작'}
            </span>
          </button>
        </div>

        {uploadedFiles.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-8">
            분석을 시작하려면 영상 파일을 업로드하고 위험 이벤트를 선택해주세요
          </div>
        )}
      </main>
    </div>
  );
}