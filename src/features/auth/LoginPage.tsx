import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Role, useAuth } from '@state/auth';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '../../services/api';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [role, setRole] = useState<Role>('company');

  const [error, setError] = useState<string | null>(null);

  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchOnWindowFocus: false,
    retry: false,
  });

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    if (healthQuery.isSuccess) {
      login({ name: name.trim(), role });
      navigate(`/${role}`, { replace: true });
      return;
    }

    try {
      await healthQuery.refetch();
      if (healthQuery.isSuccess || healthQuery.data) {
        login({ name: name.trim(), role });
        navigate(`/${role}`, { replace: true });
      } else {
        throw new Error('health failed');
      }
    } catch {
      setError('Ne mogu da se povežem sa backend-om jer sam dziber(proverite da li je server pokrenut).');
    }
  };

  return (
    <div className="hero container">
      <div className="card card-pad" style={{ maxWidth: 560, width: '100%' }}>
        <div className="stack-lg">
          <div className="stack">
            <div className="row" style={{ gap: 10 }}>
              <img src="/logo.svg" alt="BEST" width={40} height={40} />
              <h1 style={{ margin: 0 }}>BEST CV Baza</h1>
              <span
                title={
                  healthQuery.isLoading
                    ? 'Povezivanje...'
                    : healthQuery.isError
                    ? 'Nije povezan'
                    : 'Povezano'
                }
                style={{
                  display: 'inline-block',
                  width: 12,
                  height: 12,
                  borderRadius: 12,
                  marginLeft: 8,
                  marginTop: 6,
                  background:
                    healthQuery.isLoading ? '#F59E0B' : healthQuery.isError ? '#EF4444' : '#10B981',
                }}
              />
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

            {error && <div style={{ color: 'var(--color-danger)' }}>{error}</div>}

            <div className="row space-between" style={{ marginTop: 8 }}>
              <div className="row" style={{ gap: 8 }}>
                <span className="pill">Frontend samo</span>
                <span className="pill">Mock autentikacija</span>
              </div>
              <button
                className="btn btn-primary"
                type="submit"
                disabled={healthQuery.isLoading}
              >
                {healthQuery.isLoading ? 'Povezivanje...' : 'Prijava'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
