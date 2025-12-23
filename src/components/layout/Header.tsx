import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '@state/auth';

export function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="header">
      <div className="container header-inner">
        <Link to={user ? `/${user.role}` : '/login'} className="brand">
          <img src="/logo.svg" alt="BEST" width={32} height={32} />
          <span>BEST CV Baza</span>
        </Link>
        {user ? (
          <nav className="nav">
            {user.role === 'company' && (
              <NavLink to="/company" className="nav-link">
                Kompanije
              </NavLink>
            )}
            {user.role === 'student' && (
              <NavLink to="/student" className="nav-link">
                Student
              </NavLink>
            )}
            {user.role === 'admin' && (
              <NavLink to="/admin" className="nav-link">
                Admin
              </NavLink>
            )}
            <button className="btn btn-ghost" onClick={logout}>
              Odjava
            </button>
          </nav>
        ) : (
          <nav className="nav">
            <NavLink to="/login" className="btn btn-primary">
              Prijava
            </NavLink>
          </nav>
        )}
      </div>
    </header>
  );
}
