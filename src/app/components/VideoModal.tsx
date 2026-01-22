import { X, Clock, MapPin, AlertCircle, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { AnalysisResult } from './AnalysisDashboard';

interface VideoModalProps {
  result: AnalysisResult;
  onClose: () => void;
}

export function VideoModal({ result, onClose }: VideoModalProps) {
  const [copied, setCopied] = useState(false);

  const reportText = `[교통법규 위반 신고]

발생 일시: ${result.timestamp}
발생 장소: ${result.location}
위반 유형: ${result.eventName}

상세 내용:
${result.description}

위 내용에 대해 신고합니다.`;

  const handleCopyReport = () => {
    // Fallback method for environments where Clipboard API is blocked
    const textArea = document.createElement('textarea');
    textArea.value = reportText;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      document.execCommand('copy');
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    } finally {
      textArea.remove();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-sky-100">
          <h3 className="text-gray-800">분석 상세</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-sky-50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Video Section */}
            <div className="lg:col-span-2">
              <div className="aspect-video bg-gray-900 rounded-xl overflow-hidden mb-4">
                <video
                  src={result.videoUrl}
                  controls
                  className="w-full h-full"
                  autoPlay
                >
                  Your browser does not support the video tag.
                </video>
              </div>
              
              <div className="bg-sky-50 rounded-xl p-4">
                <div className="flex items-start gap-2 mb-3">
                  <AlertCircle className="w-5 h-5 text-sky-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-gray-800 mb-1">위반 내용</h4>
                    <p className="text-sm text-gray-700">{result.description}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Details */}
            <div className="space-y-4">
              <div className="bg-white border border-sky-100 rounded-xl p-4">
                <h4 className="text-gray-800 mb-4">분석 정보</h4>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                      <Clock className="w-4 h-4 text-sky-500" />
                      <span className="text-xs text-gray-500">발생 시간</span>
                    </div>
                    <p className="text-sm text-gray-800 ml-6">{result.timestamp}</p>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                      <MapPin className="w-4 h-4 text-sky-500" />
                      <span className="text-xs text-gray-500">발생 위치</span>
                    </div>
                    <p className="text-sm text-gray-800 ml-6">{result.location}</p>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                      <AlertCircle className="w-4 h-4 text-sky-500" />
                      <span className="text-xs text-gray-500">위반 유형</span>
                    </div>
                    <p className="text-sm ml-6">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs text-white ${
                          result.severity === 'high'
                            ? 'bg-red-500'
                            : result.severity === 'medium'
                            ? 'bg-orange-500'
                            : 'bg-yellow-500'
                        }`}
                      >
                        {result.eventName}
                      </span>
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-sky-500 to-sky-600 rounded-xl p-6 text-white">
                <h4 className="mb-3">신고 내용 복사</h4>
                <p className="text-sm text-sky-100 mb-4">
                  아래 버튼을 클릭하여 안전신문고 신고에 필요한 내용을 클립보드에 복사할 수 있습니다.
                </p>
                <button
                  onClick={handleCopyReport}
                  className="w-full bg-white text-sky-600 px-4 py-3 rounded-lg hover:bg-sky-50 transition-colors flex items-center justify-center gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="w-5 h-5" />
                      <span>복사 완료!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-5 h-5" />
                      <span>신고 내용 복사</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}