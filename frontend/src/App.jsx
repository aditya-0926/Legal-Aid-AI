import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from './components/shared/Navbar'
import { ErrorBoundary } from './components/shared/ErrorBoundary'
import Home     from './pages/Home'
import Chat     from './pages/Chat'
import About    from './pages/About'
import Upload   from './pages/Upload'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <div className="min-h-screen bg-surface dark:bg-gray-900 transition-colors">
          <Navbar />
          <Routes>
            <Route path="/"       element={<Home />} />
            <Route path="/chat"   element={<Chat />} />
            <Route path="/about"  element={<About />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="*"       element={<NotFound />} />
          </Routes>
        </div>
      </ErrorBoundary>
    </BrowserRouter>
  )
}
