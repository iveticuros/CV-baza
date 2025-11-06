import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Role, useAuth } from '@state/auth';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [role, setRole] = useState<Role>('company');

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    login({ name: name.trim(), role });
    navigate(`/${role}`, { replace: true });
  };

  return (
    <div className="hero container">
      <div className="card card-pad" style={{ maxWidth: 560, width: '100%' }}>
        <div className="stack-lg">
          <div className="stack">
            <div className="row" style={{ gap: 10 }}>
              <img src="/logo.svg" alt="BEST" width={40} height={40} />
              <h1 style={{ margin: 0 }}>BEST CV Baza</h1>
            </div>
            <p style={{ marginTop: -6, color: 'var(--color-muted)' }}>
              Pristupite bazi studenata — odaberite ulogu za nastavak.
            </p>
          </div>
          <form onSubmit={onSubmit} className="stack">
            <div className="stack">
              <label className="label">Ime i prezime</label>
              <input
                className="input"
                placeholder="Unesite ime (mock login)"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="stack">
              <label className="label">Uloga</label>
              <select
                className="select"
                value={role}
                onChange={(e) => setRole(e.target.value as Role)}
              >
                <option value="company">Kompanija</option>
                <option value="student">Student</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
            <div className="row space-between" style={{ marginTop: 8 }}>
              <div className="row" style={{ gap: 8 }}>
                <span className="pill">Frontend samo</span>
                <span className="pill">Mock autentikacija</span>
              </div>
              <button className="btn btn-primary" type="submit">
                Prijava
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}


