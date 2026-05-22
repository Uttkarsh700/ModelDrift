import './styles.css'
import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import Overview from './pages/Overview'
import Retraining from './pages/Retraining'
import Experiments from './pages/Experiments'

function App() {
  const [activePage, setActivePage] = useState('overview')

  const renderPage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview />
      case 'retraining':
        return <Retraining />
      case 'experiments':
        return <Experiments />
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
