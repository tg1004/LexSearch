import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, FolderPlus, Trash2 } from 'lucide-react';
import { useBookmarks } from '../../hooks/useBookmarks';
import { formatDate } from '../../utils/formatDate';
import BookmarkFolder from './BookmarkFolder';
import ErrorMessage from '../shared/ErrorMessage';
import LoadingSpinner from '../shared/LoadingSpinner';

export default function Bookmarks() {
  const { items, folders, isLoading, error, removeBookmark, editBookmark, isSaving } = useBookmarks();
  const [selectedFolder, setSelectedFolder] = useState('General');
  const [newFolderName, setNewFolderName] = useState('');
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [customFolders, setCustomFolders] = useState<string[]>([]);

  const allFolders = useMemo(() => {
    const merged = new Set([...folders, ...customFolders, 'General']);
    return Array.from(merged).sort((a, b) => {
      if (a === 'General') return -1;
      if (b === 'General') return 1;
      return a.localeCompare(b);
    });
  }, [folders, customFolders]);

  const folderCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const folder of allFolders) {
      counts[folder] = items.filter((item) => item.folder_name === folder).length;
    }
    return counts;
  }, [allFolders, items]);

  const filteredItems = items.filter((item) => item.folder_name === selectedFolder);

  const handleCreateFolder = () => {
    const trimmed = newFolderName.trim();
    if (!trimmed) return;
    setCustomFolders((prev) => [...prev, trimmed]);
    setSelectedFolder(trimmed);
    setNewFolderName('');
    setShowNewFolder(false);
  };

  const handleMoveToFolder = async (bookmarkId: string, folderName: string) => {
    await editBookmark({ id: bookmarkId, payload: { folder_name: folderName } });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorMessage
        message={error instanceof Error ? error.message : 'Failed to load bookmarks'}
      />
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-primary">Bookmarks</h2>
        <button
          type="button"
          onClick={() => setShowNewFolder(true)}
          className="inline-flex items-center gap-1.5 text-sm text-accent hover:underline"
        >
          <FolderPlus className="w-4 h-4" />
          Create folder
        </button>
      </div>

      {showNewFolder && (
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            placeholder="Folder name"
            className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30"
          />
          <button
            type="button"
            onClick={handleCreateFolder}
            className="px-4 py-2 text-sm bg-accent text-white rounded-lg hover:bg-accent/90"
          >
            Add
          </button>
          <button
            type="button"
            onClick={() => setShowNewFolder(false)}
            className="px-3 py-2 text-sm text-subtext"
          >
            Cancel
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <aside className="md:col-span-3 space-y-1">
          {allFolders.map((folder) => (
            <BookmarkFolder
              key={folder}
              name={folder}
              count={folderCounts[folder] ?? 0}
              isActive={selectedFolder === folder}
              onSelect={() => setSelectedFolder(folder)}
            />
          ))}
        </aside>

        <div className="md:col-span-9 space-y-3">
          {filteredItems.length === 0 ? (
            <div className="text-center py-12 bg-white border border-gray-200 rounded-xl">
              <Bookmark className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-primary font-medium mb-1">No bookmarks in this folder</p>
              <p className="text-sm text-subtext">
                Save documents from the document viewer to see them here.
              </p>
            </div>
          ) : (
            filteredItems.map((item) => (
              <article
                key={item.id}
                className="p-4 bg-white border border-gray-200 rounded-xl"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    {item.document_id ? (
                      <Link
                        to={`/document/${item.document_id}`}
                        className="font-medium text-primary hover:text-accent transition-colors line-clamp-2"
                      >
                        {item.title || item.document_id}
                      </Link>
                    ) : (
                      <p className="font-medium text-primary">{item.title || 'Untitled'}</p>
                    )}
                    <p className="text-sm text-subtext mt-1">
                      {[item.court, item.date ? formatDate(item.date) : null]
                        .filter(Boolean)
                        .join(' · ')}
                    </p>
                    {item.notes && (
                      <p className="text-sm text-subtext mt-2 italic">{item.notes}</p>
                    )}
                    <p className="text-xs text-subtext mt-2">
                      Saved {formatDate(item.created_at)}
                    </p>
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    <select
                      value={item.folder_name}
                      onChange={(e) => handleMoveToFolder(item.id, e.target.value)}
                      disabled={isSaving}
                      className="text-xs border border-gray-200 rounded-lg px-2 py-1"
                    >
                      {allFolders.map((folder) => (
                        <option key={folder} value={folder}>
                          {folder}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => removeBookmark(item.id)}
                      className="p-2 text-subtext hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors self-end"
                      aria-label="Remove bookmark"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
