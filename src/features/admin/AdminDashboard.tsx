import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { apiFetch, apiJson } from '@services/api';

type UserRow = {
  id: number;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  admin_approved: boolean;
};

type DeletionReq = {
  id: number;
  user_id: number;
  email: string | null;
  requested_at: string | null;
};

type AuditEntry = {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string | null;
  resource_id: number | null;
  ip_address: string | null;
  request_id: string | null;
  details: Record<string, unknown> | null;
  created_at: string | null;
};

type AuditPage = {
  items: AuditEntry[];
  total: number;
  page: number;
  page_size: number;
};

type Analytics = {
  student_users: number;
  pending_student_approvals: number;
  company_users: number;
  students_by_faculty: { faculty: string; count: number }[];
};

const TAB_LABELS: Record<string, string> = {
  users: 'Korisnici',
  pending: 'Na čekanju',
  grants: 'Pristup',
  import: 'Uvoz',
  audit: 'Revizija',
  stats: 'Statistika',
  deletions: 'Brisanja',
};

export function AdminDashboard() {
  const [tab, setTab] = useState<'users' | 'pending' | 'grants' | 'import' | 'audit' | 'stats' | 'deletions'>('users');
  const qc = useQueryClient();

  const usersQ = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => apiJson<UserRow[]>('/admin/users'),
    enabled: tab === 'users',
  });

  const pendingQ = useQuery({
    queryKey: ['admin-pending'],
    queryFn: () => apiJson<UserRow[]>('/admin/users?pending_approval=true'),
    enabled: tab === 'pending',
  });

  const analyticsQ = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => apiJson<Analytics>('/admin/analytics'),
    enabled: tab === 'stats',
  });

  const [auditPage, setAuditPage] = useState(1);
  const auditQ = useQuery({
    queryKey: ['admin-audit', auditPage],
    queryFn: () => apiJson<AuditPage>(`/admin/audit-log?page=${auditPage}&page_size=50`),
    enabled: tab === 'audit',
  });

  const deletionsQ = useQuery({
    queryKey: ['admin-deletions'],
    queryFn: () => apiJson<DeletionReq[]>('/admin/deletion-requests'),
    enabled: tab === 'deletions',
  });

  const approveMut = useMutation({
    mutationFn: (id: number) => apiJson(`/admin/users/${id}/approve-student`, { method: 'POST' }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['admin-users'] });
      void qc.invalidateQueries({ queryKey: ['admin-pending'] });
    },
  });

  const toggleActiveMut = useMutation({
    mutationFn: (u: UserRow) =>
      apiJson(`/admin/users/${u.id}`, {
        method: 'PUT',
        body: JSON.stringify({ is_active: !u.is_active }),
      }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['admin-users'] }),
  });

  const [resetPwUserId, setResetPwUserId] = useState<number | null>(null);
  const [resetPwValue, setResetPwValue] = useState('');
  const resetPwMut = useMutation({
    mutationFn: (args: { userId: number; pw: string }) =>
      apiJson(`/admin/users/${args.userId}`, { method: 'PUT', body: JSON.stringify({ password: args.pw }) }),
    onSuccess: () => { setResetPwUserId(null); setResetPwValue(''); },
  });

  const processDeletionMut = useMutation({
    mutationFn: (args: { id: number; approve: boolean }) =>
      apiJson(`/admin/deletion-requests/${args.id}/process`, {
        method: 'POST',
        body: JSON.stringify({ approve: args.approve }),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['admin-deletions'] });
      void qc.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });

  const [grantCompanyId, setGrantCompanyId] = useState('');
  const [grantMax, setGrantMax] = useState('50');
  const [grantFrom, setGrantFrom] = useState('');
  const [grantTo, setGrantTo] = useState('');
  const grantMut = useMutation({
    mutationFn: async () => {
      return apiJson('/admin/access-grants', {
        method: 'POST',
        body: JSON.stringify({
          company_user_id: Number(grantCompanyId),
          max_cv_count: Number(grantMax),
          valid_from: grantFrom,
          valid_until: grantTo,
        }),
      });
    },
  });

  const importMut = useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData();
      fd.append('file', file);
      const res = await apiFetch('/admin/students/import', { method: 'POST', body: fd });
      if (!res.ok) throw new Error('Import failed');
      return res.json() as Promise<{ created: number }>;
    },
  });

  return (
    <div className="stack-lg" style={{ padding: '24px 0' }}>
      <h1 className="section-title">Administracija</h1>
      <div className="row" style={{ gap: 8, flexWrap: 'wrap' }}>
        {(['users', 'pending', 'grants', 'deletions', 'import', 'audit', 'stats'] as const).map((t) => (
          <button key={t} type="button" className={tab === t ? 'btn btn-primary' : 'btn btn-ghost'} onClick={() => setTab(t)}>
            {TAB_LABELS[t]}
          </button>
        ))}
      </div>

      {tab === 'users' && (
        <div className="card card-pad stack">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border, #ddd)', textAlign: 'left' }}>
                <th style={{ padding: '6px 8px' }}>Email</th>
                <th style={{ padding: '6px 8px' }}>Ime</th>
                <th style={{ padding: '6px 8px' }}>Uloga</th>
                <th style={{ padding: '6px 8px' }}>Status</th>
                <th style={{ padding: '6px 8px' }}>Akcije</th>
              </tr>
            </thead>
            <tbody>
              {usersQ.data?.map((u: UserRow) => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--color-border, #eee)' }}>
                  <td style={{ padding: '6px 8px' }}>{u.email}</td>
                  <td style={{ padding: '6px 8px' }}>{u.name}</td>
                  <td style={{ padding: '6px 8px' }}>{u.role}</td>
                  <td style={{ padding: '6px 8px' }}>
                    {u.is_active ? 'Aktivan' : 'Neaktivan'} · {u.admin_approved ? 'Odobren' : 'Čeka'}
                  </td>
                  <td style={{ padding: '6px 8px' }}>
                    <div className="row" style={{ gap: 4, flexWrap: 'wrap' }}>
                      <button type="button" className="btn btn-ghost" style={{ fontSize: 12, padding: '2px 8px' }}
                        onClick={() => toggleActiveMut.mutate(u)}>
                        {u.is_active ? 'Deaktiviraj' : 'Aktiviraj'}
                      </button>
                      <button type="button" className="btn btn-ghost" style={{ fontSize: 12, padding: '2px 8px' }}
                        onClick={() => { setResetPwUserId(u.id); setResetPwValue(''); }}>
                        Reset lozinke
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {resetPwUserId && (
            <div className="card card-pad stack" style={{ marginTop: 8 }}>
              <p className="muted">Nova lozinka za korisnika #{resetPwUserId}:</p>
              <input className="input" type="password" placeholder="Min 12 karaktera…" value={resetPwValue}
                onChange={e => setResetPwValue(e.target.value)} />
              <div className="row" style={{ gap: 8 }}>
                <button type="button" className="btn btn-primary" disabled={resetPwValue.length < 12}
                  onClick={() => resetPwMut.mutate({ userId: resetPwUserId, pw: resetPwValue })}>
                  Postavi
                </button>
                <button type="button" className="btn btn-ghost" onClick={() => setResetPwUserId(null)}>Otkaži</button>
              </div>
              {resetPwMut.isError && <p style={{ color: 'var(--color-danger)' }}>{(resetPwMut.error as Error).message}</p>}
            </div>
          )}
        </div>
      )}

      {tab === 'pending' && (
        <div className="card card-pad stack">
          {pendingQ.data?.length === 0 && <p className="muted">Nema zahteva na čekanju.</p>}
          {pendingQ.data?.map((u: UserRow) => (
            <div key={u.id} className="row space-between">
              <span>{u.email} ({u.name})</span>
              <button type="button" className="btn btn-primary" onClick={() => approveMut.mutate(u.id)}>Odobri</button>
            </div>
          ))}
        </div>
      )}

      {tab === 'grants' && (
        <div className="card card-pad stack">
          <input className="input" placeholder="Company user ID" value={grantCompanyId} onChange={(e) => setGrantCompanyId(e.target.value)} />
          <input className="input" placeholder="Max CV pristupa" value={grantMax} onChange={(e) => setGrantMax(e.target.value)} />
          <div className="row" style={{ gap: 8 }}>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Od</label>
              <input className="input" type="date" value={grantFrom} onChange={(e) => setGrantFrom(e.target.value)} />
            </div>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Do</label>
              <input className="input" type="date" value={grantTo} onChange={(e) => setGrantTo(e.target.value)} />
            </div>
          </div>
          <button type="button" className="btn btn-primary" onClick={() => grantMut.mutate()}>Kreiraj grant</button>
          {grantMut.isSuccess && <p className="muted">Grant kreiran.</p>}
          {grantMut.isError && <p style={{ color: 'var(--color-danger)' }}>{(grantMut.error as Error).message}</p>}
        </div>
      )}

      {tab === 'deletions' && (
        <div className="card card-pad stack">
          {deletionsQ.data?.length === 0 && <p className="muted">Nema zahteva za brisanje.</p>}
          {deletionsQ.data?.map((d: DeletionReq) => (
            <div key={d.id} className="row space-between" style={{ alignItems: 'center' }}>
              <div>
                <span>{d.email ?? `User #${d.user_id}`}</span>
                {d.requested_at && <span className="muted" style={{ marginLeft: 8 }}>{new Date(d.requested_at).toLocaleString()}</span>}
              </div>
              <div className="row" style={{ gap: 4 }}>
                <button type="button" className="btn btn-primary" style={{ fontSize: 12, padding: '2px 8px' }}
                  onClick={() => processDeletionMut.mutate({ id: d.id, approve: true })}>Obriši</button>
                <button type="button" className="btn btn-ghost" style={{ fontSize: 12, padding: '2px 8px' }}
                  onClick={() => processDeletionMut.mutate({ id: d.id, approve: false })}>Odbij</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'import' && (
        <div className="card card-pad stack">
          <p className="muted">CSV kolone: email, name, password, ime, prezime, fakultet_id</p>
          <input type="file" accept=".csv" onChange={(e) => { const f = e.target.files?.[0]; if (f) importMut.mutate(f); }} />
          {importMut.data && <p>Uvezeno: {importMut.data.created}</p>}
        </div>
      )}

      {tab === 'audit' && (
        <div className="card card-pad stack" style={{ fontSize: 13 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border, #ddd)', textAlign: 'left' }}>
                <th style={{ padding: '4px 6px' }}>Datum</th>
                <th style={{ padding: '4px 6px' }}>Akcija</th>
                <th style={{ padding: '4px 6px' }}>Korisnik</th>
                <th style={{ padding: '4px 6px' }}>Resurs</th>
                <th style={{ padding: '4px 6px' }}>IP</th>
              </tr>
            </thead>
            <tbody>
              {auditQ.data?.items.map((r: AuditEntry) => (
                <tr key={r.id} style={{ borderBottom: '1px solid var(--color-border, #eee)' }}>
                  <td style={{ padding: '4px 6px' }}>{r.created_at ? new Date(r.created_at).toLocaleString() : '—'}</td>
                  <td style={{ padding: '4px 6px' }}>{r.action}</td>
                  <td style={{ padding: '4px 6px' }}>{r.user_id ?? '—'}</td>
                  <td style={{ padding: '4px 6px' }}>{r.resource_type}{r.resource_id != null ? `#${r.resource_id}` : ''}</td>
                  <td style={{ padding: '4px 6px' }}>{r.ip_address ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {auditQ.data && auditQ.data.total > 50 && (
            <div className="row" style={{ gap: 8, justifyContent: 'center', marginTop: 8 }}>
              <button className="btn btn-ghost" disabled={auditPage <= 1} onClick={() => setAuditPage(p => p - 1)}>← Prethodna</button>
              <span className="muted">{auditPage} / {Math.ceil(auditQ.data.total / 50)}</span>
              <button className="btn btn-ghost" disabled={auditPage >= Math.ceil(auditQ.data.total / 50)} onClick={() => setAuditPage(p => p + 1)}>Sledeća →</button>
            </div>
          )}
        </div>
      )}

      {tab === 'stats' && analyticsQ.data && (
        <div className="card card-pad stack">
          <div className="row" style={{ gap: 24, flexWrap: 'wrap' }}>
            <div className="stack" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 700 }}>{analyticsQ.data.student_users}</div>
              <div className="muted">Studenata</div>
            </div>
            <div className="stack" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 700 }}>{analyticsQ.data.pending_student_approvals}</div>
              <div className="muted">Na čekanju</div>
            </div>
            <div className="stack" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 700 }}>{analyticsQ.data.company_users}</div>
              <div className="muted">Kompanija</div>
            </div>
          </div>
          {analyticsQ.data.students_by_faculty.length > 0 && (
            <div className="stack" style={{ marginTop: 16 }}>
              <h4>Po fakultetu</h4>
              {analyticsQ.data.students_by_faculty.map((f) => (
                <div key={f.faculty} className="row space-between">
                  <span>{f.faculty}</span>
                  <strong>{f.count}</strong>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
