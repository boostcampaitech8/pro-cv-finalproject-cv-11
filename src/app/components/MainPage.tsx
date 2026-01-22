import { Shield, ArrowRight, Video, Search, ClipboardCheck } from 'lucide-react';

interface MainPageProps {
  onStart: () => void;
}

export function MainPage({ onStart }: MainPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-50 flex items-center justify-center px-6">
      <div className="max-w-5xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-24 h-24 bg-gradient-to-br from-sky-500 to-sky-600 rounded-3xl flex items-center justify-center shadow-xl">
              <Shield className="w-14 h-14 text-white" />
            </div>
          </div>
          
          <h1 className="text-5xl mb-4 text-gray-800">
            교통법규 위반 자동 탐지 시스템
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            블랙박스 영상을 AI가 분석하여 교통법규 위반 행위를 자동으로 탐지합니다
          </p>

          <button
            onClick={onStart}
            className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-sky-500 to-sky-600 text-white text-xl rounded-2xl hover:from-sky-600 hover:to-sky-700 shadow-xl hover:shadow-2xl transition-all transform hover:scale-105"
          >
            <span>시작하기</span>
            <ArrowRight className="w-6 h-6" />
          </button>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
          <div className="bg-white rounded-2xl p-8 border border-sky-100 shadow-sm hover:shadow-lg transition-all">
            <div className="w-14 h-14 bg-sky-100 rounded-xl flex items-center justify-center mb-4">
              <Video className="w-8 h-8 text-sky-600" />
            </div>
            <h3 className="text-gray-800 mb-2">영상 업로드</h3>
            <p className="text-sm text-gray-600">
              블랙박스 영상을 간편하게 업로드하고 여러 파일을 한 번에 분석할 수 있습니다
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 border border-sky-100 shadow-sm hover:shadow-lg transition-all">
            <div className="w-14 h-14 bg-sky-100 rounded-xl flex items-center justify-center mb-4">
              <Search className="w-8 h-8 text-sky-600" />
            </div>
            <h3 className="text-gray-800 mb-2">AI 분석</h3>
            <p className="text-sm text-gray-600">
              과속, 신호위반, 차선침범 등 다양한 교통법규 위반 행위를 자동으로 탐지합니다
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 border border-sky-100 shadow-sm hover:shadow-lg transition-all">
            <div className="w-14 h-14 bg-sky-100 rounded-xl flex items-center justify-center mb-4">
              <ClipboardCheck className="w-8 h-8 text-sky-600" />
            </div>
            <h3 className="text-gray-800 mb-2">신고 지원</h3>
            <p className="text-sm text-gray-600">
              분석 결과를 안전신문고 신고에 바로 사용할 수 있도록 복사해드립니다
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
