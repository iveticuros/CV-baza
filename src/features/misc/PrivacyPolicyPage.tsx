import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE } from '@services/api';

export function PrivacyPolicyPage() {
  const [data, setData] = useState<{ title?: string; summary?: string } | null>(null);
  useEffect(() => {
    void fetch(`${API_BASE}/privacy-policy`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null));
  }, []);
  return (
    <div className="container" style={{ padding: 24 }}>
      <div className="card card-pad stack">
        <h1>{data?.title || 'Politika privatnosti'}</h1>
        <p>{data?.summary}</p>
        <Link to="/login">Nazad</Link>
      </div>
    </div>
  );
}
