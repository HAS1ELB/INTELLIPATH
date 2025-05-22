import { Routes, Route, Navigate } from 'react-router-dom'
import { useSession } from './contexts/SessionContext'

// Pages
import HomePage from './pages/HomePage'
import SyllabusPage from './pages/SyllabusPage'
import ChatPage from './pages/ChatPage'
import QuizPage from './pages/QuizPage'
import NotFoundPage from './pages/NotFoundPage'

// Components
import Navbar from './components/Navbar'
import Footer from './components/Footer'

const App = () => {
  const { sessionId } = useSession()

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route 
            path="/syllabus" 
            element={sessionId ? <SyllabusPage /> : <Navigate to="/" replace />} 
          />
          <Route 
            path="/chat" 
            element={sessionId ? <ChatPage /> : <Navigate to="/" replace />} 
          />
          <Route 
            path="/quiz" 
            element={sessionId ? <QuizPage /> : <Navigate to="/" replace />} 
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App