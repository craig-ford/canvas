import React, { useState, useEffect, useRef, useCallback } from 'react';

interface InlineEditProps {
  value: string;
  onSave: (value: string) => Promise<void>;
  multiline?: boolean;
  placeholder?: string;
  readonly?: boolean;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

const InlineEdit: React.FC<InlineEditProps> = ({ 
  value, 
  onSave, 
  multiline = false, 
  placeholder = 'Click to edit...', 
  readonly = false 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [currentValue, setCurrentValue] = useState(value);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
  const saveTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    setCurrentValue(value);
  }, [value]);

  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  const handleSave = useCallback(async () => {
    if (currentValue === value) return;
    
    setSaveStatus('saving');
    setError(null);
    
    try {
      await onSave(currentValue);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (err) {
      setSaveStatus('error');
      setError(err instanceof Error ? err.message : 'Save failed');
    }
  }, [currentValue, value, onSave]);

  const debouncedSave = useCallback(() => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    saveTimeoutRef.current = setTimeout(handleSave, 2000);
  }, [handleSave]);

  const handleClick = () => {
    if (readonly) return;
    setIsEditing(true);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setCurrentValue(e.target.value);
    debouncedSave();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setCurrentValue(value);
      setIsEditing(false);
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    } else if (e.key === 'Enter' && !multiline) {
      e.preventDefault();
      handleSave();
      setIsEditing(false);
    }
  };

  const handleBlur = () => {
    setIsEditing(false);
  };

  const retry = () => {
    handleSave();
  };

  const getSaveIcon = () => {
    switch (saveStatus) {
      case 'saving':
        return <span className="text-blue-500">⏳</span>;
      case 'saved':
        return <span className="text-green-500">✓</span>;
      case 'error':
        return <span className="text-red-500">⚠</span>;
      default:
        return null;
    }
  };

  if (isEditing && !readonly) {
    const InputComponent = multiline ? 'textarea' : 'input';
    return (
      <div className="relative">
        <InputComponent
          ref={inputRef as any}
          value={currentValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={placeholder}
          className={`w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            multiline ? 'min-h-[80px] resize-vertical' : ''
          }`}
          rows={multiline ? 3 : undefined}
        />
        <div className="absolute -right-6 top-1 flex items-center space-x-1">
          {getSaveIcon()}
          {saveStatus === 'error' && (
            <button
              onClick={retry}
              className="text-xs text-blue-600 hover:underline"
              title="Retry save"
            >
              Retry
            </button>
          )}
        </div>
        {error && (
          <div className="text-xs text-red-600 mt-1">{error}</div>
        )}
      </div>
    );
  }

  return (
    <div
      onClick={handleClick}
      className={`px-2 py-1 rounded ${
        readonly 
          ? 'cursor-default' 
          : 'cursor-pointer hover:bg-gray-50 border border-transparent hover:border-gray-200'
      } ${currentValue ? '' : 'text-gray-500'}`}
    >
      {currentValue || placeholder}
      {!readonly && (
        <span className="ml-2 text-gray-400 opacity-0 group-hover:opacity-100">📝</span>
      )}
    </div>
  );
};

export default InlineEdit;