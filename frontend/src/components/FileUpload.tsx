import React, { useState, useRef, useCallback } from 'react';
import { CloudArrowUpIcon, DocumentIcon, TrashIcon } from '@heroicons/react/24/outline';

interface Attachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  label?: string;
  uploaded_by: string;
  created_at: string;
}

interface FileUploadProps {
  onUpload: (file: File, label?: string) => Promise<void>;
  attachments: Attachment[];
  onDelete: (id: string) => Promise<void>;
  maxSize: number;
  allowedTypes: string[];
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  attachments,
  onDelete,
  maxSize,
  allowedTypes
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize) {
      return `File size ${formatFileSize(file.size)} exceeds ${formatFileSize(maxSize)} limit`;
    }
    if (!allowedTypes.includes(file.type)) {
      return `File type "${file.type}" is not allowed. Allowed types: ${allowedTypes.join(', ')}`;
    }
    if (file.size === 0) {
      return 'File is empty';
    }
    return null;
  };

  const handleFileUpload = async (file: File, label?: string) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev === null) return 0;
          if (prev >= 90) return prev;
          return prev + 10;
        });
      }, 100);

      await onUpload(file, label);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setTimeout(() => setUploadProgress(null), 1000);
    } catch (err) {
      setUploadProgress(null);
      setError(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  };

  const handleDeleteAttachment = async (id: string) => {
    try {
      await onDelete(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragOver
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <p className="text-sm text-gray-600">
            Drag and drop a file here, or{' '}
            <button
              type="button"
              className="text-blue-600 hover:text-blue-500 font-medium"
              onClick={() => fileInputRef.current?.click()}
            >
              browse
            </button>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Max size: {formatFileSize(maxSize)}
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileSelect}
          accept={allowedTypes.join(',')}
        />
      </div>

      {/* Upload Progress */}
      {uploadProgress !== null && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center justify-between text-sm text-blue-700 mb-2">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-700">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-xs text-red-600 hover:text-red-500 mt-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Attachments List */}
      {attachments.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900">Attachments</h4>
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <DocumentIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {attachment.label || attachment.filename}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(attachment.size_bytes)} • {new Date(attachment.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <a
                  href={`/api/attachments/${attachment.id}`}
                  download={attachment.filename}
                  className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  Download
                </a>
                <button
                  onClick={() => handleDeleteAttachment(attachment.id)}
                  className="text-red-600 hover:text-red-500 p-1"
                  title="Delete attachment"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;