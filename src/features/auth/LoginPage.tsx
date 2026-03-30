import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@state/auth';
import { ApiError, fetchHealth } from '@services/api';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchOnWindowFocus: false,
    retry: false,
  });

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim() || !password) return;
    try {
      const role = await login(email.trim(), password);
      navigate(`/${role}`, { replace: true });
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setError(err.message);
        return;
      }
      setError('Prijava nije uspela.');
    }
  };

  return (
    <div className="hero container">
      <div className="card card-pad" style={{ maxWidth: 560, width: '100%' }}>
        <div className="stack-lg">
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
                background: healthQuery.isLoading
                  ? '#F59E0B'
                  : healthQuery.isError
                    ? '#EF4444'
                    : '#10B981',
              }}
            />
          </div>
          <p style={{ marginTop: -6, color: 'var(--color-muted)' }}>
            Prijavite se emailom i lozinkom. Studenti se najpre{' '}
            <Link to="/register">registruju</Link>.
          </p>
          <form onSubmit={onSubmit} className="stack">
            <label className="label">Email</label>
            <input
              type="email"
              className="input"
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <label className="label">Lozinka</label>
            <input
              type="password"
              className="input"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && <div style={{ color: 'var(--color-danger)' }}>{error}</div>}
            <div className="row space-between" style={{ marginTop: 8 }}>
              <Link to="/privacy-policy">Politika privatnosti</Link>
              <button className="btn btn-primary" type="submit" disabled={healthQuery.isLoading}>
                Prijava
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
