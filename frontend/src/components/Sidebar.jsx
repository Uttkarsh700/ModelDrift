import React from 'react'

const Sidebar = ({ activePage = 'overview', onPageChange = () => { } }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'retraining', label: 'Retraining', icon: '🔄' },
    { id: 'experiments', label: 'Experiments', icon: '🧪' },
    { id: 'models', label: 'Models', icon: '🤖', disabled: true },
    { id: 'drift', label: 'Drift Analysis', icon: '📈', disabled: true },
    { id: 'alerts', label: 'Alerts', icon: '🔔', disabled: true },
    { id: 'settings', label: 'Settings', icon: '⚙️', disabled: true },
  ]

  const handleNavClick = (e, itemId, disabled) => {
    e.preventDefault()
    if (!disabled) {
      onPageChange(itemId)
    }
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">🔬</div>
        <h2>ModelDrift</h2>
      </div>

      <nav className="sidebar-nav">
        <ul>
          {navItems.map((item) => (
            <li
              key={item.id}
              className={`${activePage === item.id ? 'active' : ''} ${item.disabled ? 'disabled' : ''}`}
            >
              <a
                href="#"
                onClick={(e) => handleNavClick(e, item.id, item.disabled)}
                style={{ cursor: item.disabled ? 'not-allowed' : 'pointer' }}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="footer-item">Version 0.1.0</div>
      </div>
    </div>
  )
}

export default Sidebar
