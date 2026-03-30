import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { apiFetch, apiJson } from '@services/api';

type StudentRow = {
  id: number;
  ime: string;
  prezime: string;
  prosek: number | null;
  faculty_name: string | null;
  tehnologije: string[];
};

type Page = {
  items: StudentRow[];
  total: number;
  page: number;
  page_size: number;
};

type Grant = {
  id: number;
  max_cv_count: number;
  used_cv_count: number;
  valid_from: string;
  valid_until: string;
  active: boolean;
};

type Fakultet = { id: number; naziv: string };
type TehRef = { id: number; naziv: string };

export function CompanyDashboard() {
  const [search, setSearch] = useState('');
  const [fakultetId, setFakultetId] = useState<number | ''>('');
  const [minProsek, setMinProsek] = useState('');
  const [tehId, setTehId] = useState<number | ''>('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const accessQ = useQuery({
    queryKey: ['company-access'],
    queryFn: () => apiJson<Grant[]>('/company/access'),
  });

  const facQ = useQuery({ queryKey: ['fakulteti'], queryFn: () => apiJson<Fakultet[]>('/fakulteti/') });
  const techQ = useQuery({ queryKey: ['tehnologije'], queryFn: () => apiJson<TehRef[]>('/tehnologije/') });

  const params = new URLSearchParams();
  params.set('page', String(page));
  params.set('page_size', String(pageSize));
  if (search) params.set('q', search);
  if (fakultetId) params.set('fakultet_id', String(fakultetId));
  if (minProsek) params.set('min_prosek', minProsek);
  if (tehId) params.set('tehnologija_id', String(tehId));

  const studentsQ = useQuery({
    queryKey: ['company-students', search, fakultetId, minProsek, tehId, page],
    queryFn: () => apiJson<Page>(`/company/students?${params.toString()}`),
  });

  const totalPages = studentsQ.data ? Math.ceil(studentsQ.data.total / pageSize) : 0;

  return (
    <div className="stack-lg" style={{ padding: '24px 0' }}>
      <h2 className="section-title">Pristup CV-ovima</h2>
      {accessQ.data && accessQ.data.length === 0 && (
        <p className="muted">Nemate aktivnih ugovora o pristupu. Kontaktirajte administratora.</p>
      )}
      {accessQ.data?.map((g: Grant) => (
        <div key={g.id} className="card card-pad" style={{ marginBottom: 12 }}>
          <p>
            Iskorišćeno: <strong>{g.used_cv_count}</strong> / {g.max_cv_count} dodela — važi do{' '}
            {g.valid_until} {g.active ? '(aktivno)' : '(van opsega datuma)'}
          </p>
        </div>
      ))}
      <h3>Studenti</h3>
      <div className="card card-pad" style={{ marginBottom: 12 }}>
        <div className="row" style={{ gap: 8, flexWrap: 'wrap', alignItems: 'end' }}>
          <div className="stack" style={{ flex: 2, minWidth: 150 }}>
            <label className="label">Pretraga</label>
            <input className="input" placeholder="Ime ili prezime…" value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }} />
          </div>
          <div className="stack" style={{ flex: 1, minWidth: 120 }}>
            <label className="label">Fakultet</label>
            <select className="input" value={fakultetId}
              onChange={e => { setFakultetId(e.target.value ? Number(e.target.value) : ''); setPage(1); }}>
              <option value="">Svi</option>
              {facQ.data?.map(f => <option key={f.id} value={f.id}>{f.naziv}</option>)}
            </select>
          </div>
          <div className="stack" style={{ flex: 1, minWidth: 100 }}>
            <label className="label">Min prosek</label>
            <input className="input" type="number" step="0.1" min="6" max="10" value={minProsek}
              onChange={e => { setMinProsek(e.target.value); setPage(1); }} />
          </div>
          <div className="stack" style={{ flex: 1, minWidth: 120 }}>
            <label className="label">Tehnologija</label>
            <select className="input" value={tehId}
              onChange={e => { setTehId(e.target.value ? Number(e.target.value) : ''); setPage(1); }}>
              <option value="">Sve</option>
              {techQ.data?.map(t => <option key={t.id} value={t.id}>{t.naziv}</option>)}
            </select>
          </div>
        </div>
      </div>
      {studentsQ.isLoading && <p>Učitavanje…</p>}
      {studentsQ.data?.items.length === 0 && <p>Nema dostupnih studenata.</p>}
      <div className="stack" style={{ gap: 8 }}>
        {studentsQ.data?.items.map((s: StudentRow) => (
          <div key={s.id} className="card card-pad">
            <div className="row space-between">
              <div>
                <strong>{s.ime} {s.prezime}</strong>
                <div className="muted">{s.faculty_name} · prosek {s.prosek ?? '—'}</div>
                <div className="muted" style={{ fontSize: 12 }}>{s.tehnologije.join(', ')}</div>
              </div>
              <button type="button" className="btn btn-primary"
                onClick={async () => {
                  const res = await apiFetch(`/company/students/${s.id}/cv`);
                  if (res.ok) { const blob = await res.blob(); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `cv-${s.id}.pdf`; a.click(); }
                }}>Preuzmi CV</button>
            </div>
          </div>
        ))}
      </div>
      {totalPages > 1 && (
        <div className="row" style={{ gap: 8, justifyContent: 'center' }}>
          <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prethodna</button>
          <span className="muted">{page} / {totalPages}</span>
          <button className="btn btn-ghost" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Sledeća →</button>
        </div>
      )}
    </div>
  );
}
