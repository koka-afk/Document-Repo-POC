import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import SearchPage from './pages/SearchPage';
import UploadPage from './pages/UploadPage';
import DocumentDetailPage from './pages/DocumentDetailPage';
import './App.css';

function LogoutButton() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login'); 
  };

  return <button onClick={handleLogout}>Sign Out</button>;
}


function App() {
  const { user } = useAuth();

  return (
    <Router>
      <div>
        <nav>
          <ul>
            {user && (
              <>
                <li><Link to="/search">Search</Link></li>
                <li><Link to="/upload">Upload</Link></li>
              </>
            )}
            
            {user ? (
              <>
                <li>
                  <span>Welcome, {user.email}</span>
                </li>
                <li>
                  <LogoutButton />
                </li>
              </>
            ) : (
              <>
              <li>
                <Link to="/login">Login</Link>
              </li>
              <li>
                <Link to="/signup">Register</Link>
              </li>
              </>
              
            )}
          </ul>
        </nav>
        <main>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents/:id" element={<DocumentDetailPage />} />
            
            <Route path="/" element={user ? <SearchPage /> : <LoginPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;