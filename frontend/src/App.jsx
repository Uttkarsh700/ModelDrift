import './styles.css'
import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import Overview from './pages/Overview'
import DriftAnalysis from './pages/DriftAnalysis'
import Retraining from './pages/Retraining'
import Experiments from './pages/Experiments'
import Alerts from './pages/Alerts'

function App() {
  const [activePage, setActivePage] = useState('overview')

  const renderPage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview />
      case 'drift':
        return <DriftAnalysis />
      case 'retraining':
        return <Retraining />
      case 'experiments':
        return <Experiments />
      case 'alerts':
        return <Alerts />
      default:
        return <Overview />
    }
  }

  return (
    <div className="app-container">
      <Sidebar activePage={activePage} onPageChange={setActivePage} />
      <div className="main-content">
        <Topbar />
        <div className="content">
          {renderPage()}
        </div>
      </div>
    </div>
  )
}

export default App
