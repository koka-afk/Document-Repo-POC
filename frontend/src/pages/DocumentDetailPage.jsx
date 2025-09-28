import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getDocumentVersions, downloadDocument } from '../services/api';

function DocumentDetailPage() {
  const [versions, setVersions] = useState([]);
  const { id } = useParams(); 
  useEffect(() => {
    const fetchVersions = async () => {
      try {
        const response = await getDocumentVersions(id);
        setVersions(response.data);
      } catch (error) {
        console.error("Failed to fetch versions:", error);
      }
    };
    fetchVersions();
  }, [id]);

  const createFilename = (version) => {
    const originalFilename = version.storage_path.split('/').pop() || `document_${id}.bin`;
    const [name, ext] = originalFilename.split('.');
    return `${name}_v${version.version_number}.${ext || 'bin'}`;
  }

  return (
    <div>
      <h2>Document Version History (ID: {id})</h2>
      {versions.length > 0 ? (
        <ul>
          {versions.map((version, index) => (
            <li key={version.id}>
              Version {version.version_number}
              
              {index === 0 && <strong> (Latest)</strong>}
              
              <span> (Uploaded by: {version.uploader.name} on {new Date(version.created_at).toLocaleString()})</span>
              
              {index === 0 && (
                <button onClick={() => downloadDocument(id, createFilename(version))}>
                  Download Latest Version
                </button>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading version history or no versions found...</p>
      )}
    </div>
  );
}

export default DocumentDetailPage;