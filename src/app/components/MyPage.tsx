import { User, Mail, Calendar, ChevronDown, ChevronUp, AlertCircle, MapPin, Clock } from 'lucide-react';
import { Header } from './Header';
import { useState } from 'react';

interface MyPageProps {
  onNavigate: (page: 'main' | 'upload' | 'results' | 'mypage') => void;
}

// Mock user data
const userData = {
  name: '홍길동',
  email: 'user@example.com',
  joinDate: '2025-12-01',
};

// Mock recent reports
const recentReports = [
  {
    id: 1,
    date: '2026-01-22 14:32:15',
    location: '서울시 강남구 테헤란로 123',
    violationType: '과속',
    description: '제한속도 60km/h 구간에서 약 85km/h로 주행하여 과속이 감지되었습니다.',
    status: '접수 완료',
  },
  {
    id: 2,
    date: '2026-01-21 15:45:30',
    location: '서울시 서초구 강남대로 456',
    violationType: '신호위반',
    description: '적색 신호에서 교차로를 통과하여 신호위반이 감지되었습니다.',
    status: '처리 중',
  },
  {
    id: 3,
    date: '2026-01-20 16:12:45',
    location: '서울시 송파구 올림픽대로 789',
    violationType: '차선침범',
    description: '차선을 침범하여 주행하는 차량이 감지되었습니다.',
    status: '접수 완료',
  },
  {
    id: 4,
    date: '2026-01-19 17:20:10',
    location: '서울시 마포구 월드컵로 321',
    violationType: '불법주정차',
    description: '주정차 금지 구역에 차량이 정차되어 있는 것이 감지되었습니다.',
    status: '완료',
  },
  {
    id: 5,
    date: '2026-01-18 18:05:22',
    location: '서울시 용산구 이태원로 654',
    violationType: '보행자 위협',
    description: '횡단보도를 건너는 보행자에게 위협적으로 접근한 차량이 감지되었습니다.',
    status: '접수 완료',
  },
];

export function MyPage({ onNavigate }: MyPageProps) {
  const [expandedReports, setExpandedReports] = useState<number[]>([]);

  const toggleReport = (id: number) => {
    setExpandedReports((prev) =>
      prev.includes(id) ? prev.filter((reportId) => reportId !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-50">
      <Header currentPage="mypage" onNavigate={onNavigate} />

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-gray-800 mb-2">마이페이지</h2>
          <p className="text-gray-600">내 정보와 신고 내역을 확인하세요</p>
        </div>

        <div className="space-y-6">
          {/* Profile Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-sky-100 p-8">
            <h3 className="text-gray-800 mb-6">프로필 정보</h3>
            
            <div className="flex items-start gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-sky-400 to-sky-600 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-10 h-10 text-white" />
              </div>
              
              <div className="flex-1 space-y-4">
                <div>
                  <label className="text-sm text-gray-500 mb-1 block">이름</label>
                  <p className="text-gray-800">{userData.name}</p>
                </div>
                
                <div>
                  <label className="text-sm text-gray-500 mb-1 block">이메일</label>
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-sky-500" />
                    <p className="text-gray-800">{userData.email}</p>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm text-gray-500 mb-1 block">가입일</label>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-sky-500" />
                    <p className="text-gray-800">{userData.joinDate}</p>
                  </div>
                </div>

                <button className="mt-4 px-6 py-2 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors">
                  프로필 수정
                </button>
              </div>
            </div>
          </div>

          {/* Recent Reports */}
          <div className="bg-white rounded-2xl shadow-sm border border-sky-100 p-8">
            <h3 className="text-gray-800 mb-6">최근 신고 내역</h3>
            
            <div className="space-y-3">
              {recentReports.map((report) => {
                const isExpanded = expandedReports.includes(report.id);
                
                return (
                  <div
                    key={report.id}
                    className="border border-sky-100 rounded-xl overflow-hidden hover:border-sky-300 transition-colors"
                  >
                    <button
                      onClick={() => toggleReport(report.id)}
                      className="w-full p-4 flex items-center justify-between hover:bg-sky-50 transition-colors"
                    >
                      <div className="flex items-center gap-4 flex-1 text-left">
                        <div className="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <AlertCircle className="w-5 h-5 text-sky-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-gray-800">{report.violationType}</span>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              report.status === '완료' 
                                ? 'bg-green-100 text-green-700'
                                : report.status === '처리 중'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-sky-100 text-sky-700'
                            }`}>
                              {report.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500">{report.date}</p>
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      )}
                    </button>

                    {isExpanded && (
                      <div className="px-4 pb-4 pt-2 bg-sky-50/50 border-t border-sky-100">
                        <div className="space-y-3">
                          <div className="flex items-start gap-2">
                            <MapPin className="w-4 h-4 text-sky-500 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-xs text-gray-500 mb-1">발생 위치</p>
                              <p className="text-sm text-gray-700">{report.location}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-start gap-2">
                            <Clock className="w-4 h-4 text-sky-500 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-xs text-gray-500 mb-1">발생 시간</p>
                              <p className="text-sm text-gray-700">{report.date}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-start gap-2">
                            <AlertCircle className="w-4 h-4 text-sky-500 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-xs text-gray-500 mb-1">상세 내용</p>
                              <p className="text-sm text-gray-700">{report.description}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {recentReports.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>아직 신고 내역이 없습니다</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}