import { useState, useEffect } from 'react';
import { MainPage } from '@/app/components/MainPage';
import { UploadPage } from '@/app/components/UploadPage';
import { ResultsPage } from '@/app/components/ResultsPage';
import { MyPage } from '@/app/components/MyPage';
import { AnalysisResult } from '@/app/components/AnalysisDashboard';
import axios from 'axios';

// Mock data for demonstration
const mockResults: AnalysisResult[] = [
  {
    id: '1',
    thumbnail: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=800&q=80',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    timestamp: '2026-01-22 14:32:15',
    location: '서울시 강남구 테헤란로 123',
    eventType: 'speeding',
    eventName: '과속',
    description: '제한속도 60km/h 구간에서 약 85km/h로 주행하여 과속이 감지되었습니다.',
    severity: 'high',
  },
  {
    id: '2',
    thumbnail: 'https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&q=80',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    timestamp: '2026-01-22 15:45:30',
    location: '서울시 서초구 강남대로 456',
    eventType: 'signal',
    eventName: '신호위반',
    description: '적색 신호에서 교차로를 통과하여 신호위반이 감지되었습니다.',
    severity: 'high',
  },
  {
    id: '3',
    thumbnail: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&q=80',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    timestamp: '2026-01-22 16:12:45',
    location: '서울시 송파구 올림픽대로 789',
    eventType: 'lane',
    eventName: '차선침범',
    description: '차선을 침범하여 주행하는 차량이 감지되었습니다.',
    severity: 'medium',
  },
  {
    id: '4',
    thumbnail: 'https://images.unsplash.com/photo-1485463611174-f302f6a5c1c9?w=800&q=80',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    timestamp: '2026-01-22 17:20:10',
    location: '서울시 마포구 월드컵로 321',
    eventType: 'illegal-parking',
    eventName: '불법주정차',
    description: '주정차 금지 구역에 차량이 정차되어 있는 것이 감지되었습니다.',
    severity: 'medium',
  },
  {
    id: '5',
    thumbnail: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    timestamp: '2026-01-22 18:05:22',
    location: '서울시 용산구 이태원로 654',
    eventType: 'pedestrian',
    eventName: '보행자 위협',
    description: '횡단보도를 건너는 보행자에게 위협적으로 접근한 차량이 감지되었습니다.',
    severity: 'high',
  },
  {
    id: '6',
    thumbnail: 'https://images.unsplash.com/photo-1464219789935-c2d9d9aba644?w=800&q=80',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    timestamp: '2026-01-22 19:15:33',
    location: '서울시 중구 세종대로 987',
    eventType: 'illegal-turn',
    eventName: '불법유턴',
    description: '유턴 금지 구역에서 유턴을 시도한 차량이 감지되었습니다.',
    severity: 'medium',
  },
];

type Page = 'main' | 'upload' | 'results' | 'mypage';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('main');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  useEffect(() => {
  const checkBackend = async () => {
    try {
      const res = await axios.get('http://localhost:8000/health');
      console.log('FastAPI 연결 성공:', res.data);
    } catch (err) {
      console.error('FastAPI 연결 실패:', err);
    }
  };

  checkBackend();
}, []);

  const handleNavigate = (page: Page) => {
    setCurrentPage(page);
  };

  const handleStart = () => {
    setCurrentPage('upload');
  };

  const handleFilesUpload = (files: File[]) => {
    setUploadedFiles(files);
  };

  const handleEventToggle = (event: string) => {
    setSelectedEvents((prev) =>
      prev.includes(event)
        ? prev.filter((e) => e !== event)
        : [...prev, event]
    );
  };

  const handleAnalyze = async () => {
    if (uploadedFiles.length === 0 || selectedEvents.length === 0) {
      return;
    }

    setIsAnalyzing(true);

    try {
      const formData = new FormData();

      // 파일들 추가
      uploadedFiles.forEach((file) => {
        formData.append("files", file);
      });

      // 선택 이벤트도 같이 전송
      formData.append("events", JSON.stringify(selectedEvents));

      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("업로드 결과:", data);

      // 일단 성공하면 바로 결과 페이지로 이동 (임시)
      setResults([]);
      setCurrentPage("results");
    } catch (err) {
      console.error("분석 요청 실패:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <>
      {currentPage === 'main' && <MainPage onStart={handleStart} />}
      
      {currentPage === 'upload' && (
        <UploadPage
          uploadedFiles={uploadedFiles}
          onFilesUpload={handleFilesUpload}
          selectedEvents={selectedEvents}
          onEventToggle={handleEventToggle}
          onAnalyze={handleAnalyze}
          onNavigate={handleNavigate}
          isAnalyzing={isAnalyzing}
        />
      )}
      
      {currentPage === 'results' && (
        <ResultsPage
          results={results}
          onNavigate={handleNavigate}
        />
      )}
      
      {currentPage === 'mypage' && (
        <MyPage
          onNavigate={handleNavigate}
        />
      )}
    </>
  );
}