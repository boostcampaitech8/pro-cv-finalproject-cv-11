import { Upload, Video, X } from 'lucide-react';
import { useState } from 'react';

interface UploadSectionProps {
  onFilesUpload: (files: File[]) => void;
  uploadedFiles: File[];
}

export function UploadSection({ onFilesUpload, uploadedFiles }: UploadSectionProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('video/'));
    if (files.length > 0) {
      onFilesUpload([...uploadedFiles, ...files]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const videoFiles = Array.from(files).filter(file => file.type.startsWith('video/'));
      onFilesUpload([...uploadedFiles, ...videoFiles]);
    }
  };

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    onFilesUpload(newFiles);
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-sky-100 p-8">
      <h2 className="text-gray-800 mb-4">블랙박스 영상 업로드</h2>
      
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
          isDragging 
            ? 'border-sky-400 bg-sky-50' 
            : 'border-sky-200 bg-sky-50/30 hover:border-sky-300 hover:bg-sky-50'
        }`}
      >
        <div className="flex flex-col items-center gap-3">
          <Upload className="w-12 h-12 text-sky-400" />
          <p className="text-gray-700">영상 파일을 드래그하거나 클릭하여 업로드하세요</p>
          <p className="text-sm text-gray-500">MP4, AVI, MOV 형식 지원 | 여러 파일 선택 가능</p>
        </div>
        
        <input
          type="file"
          accept="video/*"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-block mt-4 px-6 py-2 bg-sky-500 text-white rounded-lg cursor-pointer hover:bg-sky-600 transition-colors"
        >
          파일 선택
        </label>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-gray-700 mb-3">업로드된 파일 ({uploadedFiles.length}개)</h3>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-sky-50 rounded-lg p-4 border border-sky-100"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <Video className="w-5 h-5 text-sky-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700 truncate">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-4 p-2 hover:bg-sky-100 rounded-lg transition-colors flex-shrink-0"
                >
                  <X className="w-4 h-4 text-gray-500 hover:text-red-500" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}