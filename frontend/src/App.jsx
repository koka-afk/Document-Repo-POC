import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import SearchPage from './pages/SearchPage';
import UploadPage from './pages/UploadPage';
import DocumentDetailPage from './pages/DocumentDetailPage';
import './App.css'; // Basic styling

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/search">Search</Link></li>
            <li><Link to="/upload">Upload</Link></li>
            <li><Link to="/login">Login</Link></li>
          </ul>
        </nav>
        <main>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents/:id" element={<DocumentDetailPage />} />
            <Route path="/" element={<SearchPage />} /> {/* Default page */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;