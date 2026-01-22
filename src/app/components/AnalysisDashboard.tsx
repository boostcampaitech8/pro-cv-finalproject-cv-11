import { Clock, MapPin, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { VideoModal } from './VideoModal';

export interface AnalysisResult {
  id: string;
  thumbnail: string;
  videoUrl: string;
  timestamp: string;
  location: string;
  eventType: string;
  eventName: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
}

interface AnalysisDashboardProps {
  results: AnalysisResult[];
}

export function AnalysisDashboard({ results }: AnalysisDashboardProps) {
  const [selectedVideo, setSelectedVideo] = useState<AnalysisResult | null>(null);

  if (results.length === 0) {
    return null;
  }

  return (
    <>
      <div className="bg-white rounded-2xl shadow-sm border border-sky-100 p-8">
        <h2 className="text-gray-800 mb-6">분석 결과</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((result) => (
            <div
              key={result.id}
              onClick={() => setSelectedVideo(result)}
              className="bg-white border border-sky-100 rounded-xl overflow-hidden cursor-pointer hover:shadow-lg hover:border-sky-300 transition-all group"
            >
              <div className="relative aspect-video bg-gray-100">
                <img
                  src={result.thumbnail}
                  alt={`분석 결과 ${result.id}`}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 right-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs text-white ${
                      result.severity === 'high'
                        ? 'bg-red-500'
                        : result.severity === 'medium'
                        ? 'bg-orange-500'
                        : 'bg-yellow-500'
                    }`}
                  >
                    {result.eventName}
                  </span>
                </div>
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-all flex items-center justify-center">
                  <div className="w-12 h-12 rounded-full bg-white/0 group-hover:bg-white/90 flex items-center justify-center transition-all">
                    <svg
                      className="w-6 h-6 text-sky-500 opacity-0 group-hover:opacity-100 transition-all"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="p-4">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                  <Clock className="w-4 h-4 text-sky-500" />
                  <span>{result.timestamp}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                  <MapPin className="w-4 h-4 text-sky-500" />
                  <span>{result.location}</span>
                </div>
                <p className="text-sm text-gray-700 line-clamp-2">{result.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedVideo && (
        <VideoModal
          result={selectedVideo}
          onClose={() => setSelectedVideo(null)}
        />
      )}
    </>
  );
}
