import React, { useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

interface RichTextEditorProps {
  content: string;
  onUpdate: (html: string) => void;
  placeholder?: string;
}

const MenuButton: React.FC<{ onClick: () => void; active?: boolean; children: React.ReactNode }> = ({ onClick, active, children }) => (
  <button
    type="button"
    onMouseDown={(e) => { e.preventDefault(); onClick(); }}
    className={`px-2 py-1 text-xs rounded transition-colors ${active ? 'bg-primary text-white' : 'text-neutral-600 hover:bg-neutral-100'}`}
  >
    {children}
  </button>
);

const RichTextEditor: React.FC<RichTextEditorProps> = ({ content, onUpdate, placeholder }) => {
  const editor = useEditor({
    extensions: [StarterKit],
    content: content || '',
    editorProps: {
      attributes: { class: 'prose prose-sm max-w-none focus:outline-none min-h-[80px] px-3 py-2' },
    },
    onBlur: ({ editor }) => onUpdate(editor.getHTML()),
  });

  if (!editor) return null;

  return (
    <div className="border border-neutral-200 rounded-lg overflow-hidden focus-within:border-primary bg-white">
      <div className="flex gap-0.5 px-2 py-1 border-b border-neutral-100 bg-neutral-50">
        <MenuButton onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive('bold')}>B</MenuButton>
        <MenuButton onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive('italic')}>I</MenuButton>
        <MenuButton onClick={() => editor.chain().focus().toggleBulletList().run()} active={editor.isActive('bulletList')}>•</MenuButton>
        <MenuButton onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive('orderedList')}>1.</MenuButton>
      </div>
      <div className="relative bg-white">
        <EditorContent editor={editor} />
        {!content && !editor.isFocused && editor.isEmpty && placeholder && (
          <div className="absolute top-0 left-0 px-3 py-2 text-neutral-400 text-sm pointer-events-none">{placeholder}</div>
        )}
      </div>
    </div>
  );
};

export default RichTextEditor;
