import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { searchDocuments } from '../services/api';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [tag, setTag] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await searchDocuments(query, tag);
      setResults(response.data);
    } catch (error) {
      console.error("Search failed:", error);
    }
  };

  return (
    <div>
      <h2>Search Documents</h2>
      <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by title..." />
      <input type="text" value={tag} onChange={(e) => setTag(e.target.value)} placeholder="Search by tag..." />
      <button onClick={handleSearch}>Search</button>
      <hr />
      <div>
        <h3>Results</h3>
        <ul>
          {results.map((doc) => (
            <li key={doc.id}>
              <Link to={`/documents/${doc.id}`}>{doc.title}</Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default SearchPage;