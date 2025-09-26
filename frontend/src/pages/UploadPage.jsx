import React, { useState } from 'react';
import { uploadDocument } from '../services/api';

function UploadPage() {
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState('');
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('tags', tags); // e.g., "Finance,Report"
    formData.append('file', file);

    try {
      await uploadDocument(formData);
      alert('Document uploaded successfully!');
    } catch (error) {
      alert('Failed to upload document.');
      console.error(error);
    }
  };

  return (
    <div>
      <h2>Upload New Document</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Document Title" required />
        <input type="text" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="Tags (comma-separated)" required />
        <input type="file" onChange={(e) => setFile(e.target.files[0])} required />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default UploadPage;