import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { API_BASE } from '@services/api';

export function VerifyEmailPage() {
  const [params] = useSearchParams();
  const token = params.get('token') || '';
  const [msg, setMsg] = useState<string>('Potvrda…');
  useEffect(() => {
    if (!token) {
      setMsg('Nedostaje token.');
      return;
    }
    void (async () => {
      const res = await fetch(`${API_BASE}/auth/verify-email?token=${encodeURIComponent(token)}`);
      const j = await res.json().catch(() => ({}));
      setMsg(j.message || (res.ok ? 'Email potvrđen.' : 'Link nije validan.'));
    })();
  }, [token]);
  return (
    <div className="container" style={{ padding: 24 }}>
      <div className="card card-pad stack">
        <p>{msg}</p>
        <Link to="/login">Na prijavu</Link>
      </div>
    </div>
  );
}
