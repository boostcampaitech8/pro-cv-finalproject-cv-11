import { AlertTriangle, Car, Crosshair, StopCircle, TrendingUp, Users } from 'lucide-react';

interface EventSettingsProps {
  selectedEvents: string[];
  onEventToggle: (event: string) => void;
}

const dangerEvents = [
  { id: 'speeding', name: '과속', icon: TrendingUp },
  { id: 'signal', name: '신호위반', icon: StopCircle },
  { id: 'lane', name: '차선침범', icon: Car },
  { id: 'illegal-parking', name: '불법주정차', icon: AlertTriangle },
  { id: 'illegal-turn', name: '불법유턴', icon: Crosshair },
  { id: 'pedestrian', name: '보행자 위협', icon: Users },
];

export function EventSettings({ selectedEvents, onEventToggle }: EventSettingsProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-sky-100 p-8">
      <h2 className="text-gray-800 mb-6">위험 이벤트 설정</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {dangerEvents.map((event) => {
          const Icon = event.icon;
          const isSelected = selectedEvents.includes(event.id);
          
          return (
            <button
              key={event.id}
              onClick={() => onEventToggle(event.id)}
              className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center gap-2 ${
                isSelected
                  ? 'border-sky-500 bg-sky-50 text-sky-700'
                  : 'border-sky-100 bg-white text-gray-600 hover:border-sky-300 hover:bg-sky-50/50'
              }`}
            >
              <Icon className={`w-6 h-6 ${isSelected ? 'text-sky-500' : 'text-gray-400'}`} />
              <span className="text-sm">{event.name}</span>
              {isSelected && (
                <div className="w-5 h-5 bg-sky-500 rounded-full flex items-center justify-center">
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2.5"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
