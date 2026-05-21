import './styles.css'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import Overview from './pages/Overview'

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Topbar />
        <div className="content">
          <Overview />
        </div>
      </div>
    </div>
  )
}

export default App
