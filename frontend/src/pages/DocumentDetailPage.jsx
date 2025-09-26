import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getDocumentVersions, downloadDocument } from '../services/api';

function DocumentDetailPage() {
  const [versions, setVersions] = useState([]);
  const { id } = useParams(); // Gets the ':id' from the URL

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

  return (
    <div>
      <h2>Document Version History (ID: {id})</h2>
      {versions.length > 0 ? (
        <ul>
          {versions.map((version) => (
            <li key={version.id}>
              Version {version.version_number} (Uploaded: {new Date(version.created_at).toLocaleString()})
              <button onClick={() => downloadDocument(id, `doc_${id}_v${version.version_number}.pdf`)}>
                Download
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p>No versions found for this document.</p>
      )}
    </div>
  );
}

export default DocumentDetailPage;