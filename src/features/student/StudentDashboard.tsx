import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { useAuth } from '@state/auth';
import { apiFetch, apiJson } from '@services/api';

type Projekat = {
  id: number;
  datum_pocetka_izrade: string;
  datum_kraja_izrade_projekta: string | null;
  opis: string;
};

type Tehnologija = {
  id: number;
  naziv: string;
};

type Fakultet = {
  id: number;
  naziv: string;
};

type Profile = {
  id: number;
  ime: string;
  prezime: string;
  kontakt_telefon: string | null;
  datum_rodjenja: string | null;
  adresa: string | null;
  prosek: number | null;
  fakultet_id: number;
  faculty_name: string | null;
  has_cv: boolean;
  last_edit_at: string | null;
  can_edit_until: string | null;
  projekti: Projekat[];
  tehnologije: Tehnologija[];
};

type TehRef = { id: number; naziv: string };

export function StudentDashboard() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<{
    ime: string; prezime: string; kontakt_telefon: string; datum_rodjenja: string;
    adresa: string; prosek: string; fakultet_id: number; tehnologija_ids: number[];
    projekti: { datum_pocetka_izrade: string; datum_kraja_izrade_projekta: string; opis: string }[];
  }>({ ime: '', prezime: '', kontakt_telefon: '', datum_rodjenja: '', adresa: '', prosek: '', fakultet_id: 0, tehnologija_ids: [], projekti: [] });

  const profileQ = useQuery({
    queryKey: ['student-profile'],
    queryFn: () => apiJson<Profile>('/students/profile'),
  });

  const fakultetiQ = useQuery({
    queryKey: ['fakulteti'],
    queryFn: () => apiJson<Fakultet[]>('/fakulteti/'),
    enabled: editing,
  });

  const techQ = useQuery({
    queryKey: ['tehnologije'],
    queryFn: () => apiJson<TehRef[]>('/tehnologije/'),
    enabled: editing,
  });

  useEffect(() => {
    if (profileQ.data && editing) {
      const p = profileQ.data;
      setForm({
        ime: p.ime, prezime: p.prezime, kontakt_telefon: p.kontakt_telefon ?? '',
        datum_rodjenja: p.datum_rodjenja ?? '', adresa: p.adresa ?? '',
        prosek: p.prosek?.toString() ?? '', fakultet_id: p.fakultet_id,
        tehnologija_ids: p.tehnologije.map(t => t.id),
        projekti: p.projekti.map(pr => ({
          datum_pocetka_izrade: pr.datum_pocetka_izrade,
          datum_kraja_izrade_projekta: pr.datum_kraja_izrade_projekta ?? '',
          opis: pr.opis,
        })),
      });
    }
  }, [editing, profileQ.data]);

  const updateMut = useMutation({
    mutationFn: async () => {
      const body: Record<string, unknown> = {
        ime: form.ime, prezime: form.prezime,
        kontakt_telefon: form.kontakt_telefon || null,
        datum_rodjenja: form.datum_rodjenja || null,
        adresa: form.adresa || null,
        prosek: form.prosek ? parseFloat(form.prosek) : null,
        fakultet_id: form.fakultet_id,
        tehnologija_ids: form.tehnologija_ids,
        projekti: form.projekti.map(p => ({
          datum_pocetka_izrade: p.datum_pocetka_izrade,
          datum_kraja_izrade_projekta: p.datum_kraja_izrade_projekta || null,
          opis: p.opis,
        })),
      };
      return apiJson<Profile>('/students/profile', { method: 'PUT', body: JSON.stringify(body) });
    },
    onSuccess: () => {
      setEditing(false);
      void qc.invalidateQueries({ queryKey: ['student-profile'] });
    },
  });

  const exportMut = useMutation({
    mutationFn: async () => {
      const res = await apiFetch('/students/profile/export');
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'my-data-export.json';
      a.click();
    },
  });

  const delReqMut = useMutation({
    mutationFn: () => apiJson<{ message: string }>('/students/me/deletion-request', { method: 'POST' }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['student-profile'] }),
  });

  const canEdit = profileQ.data && !profileQ.data.can_edit_until;

  return (
    <div className="container stack-lg" style={{ padding: '24px 0' }}>
      <h1 className="section-title">Student — {user?.name}</h1>
      {profileQ.isLoading && <p>Učitavanje…</p>}
      {profileQ.error && <p style={{ color: 'var(--color-danger)' }}>Ne mogu učitati profil.</p>}
      {profileQ.data && !editing && (
        <div className="card card-pad stack">
          <p><strong>{profileQ.data.ime}</strong> {profileQ.data.prezime}</p>
          {profileQ.data.faculty_name && <p className="muted">{profileQ.data.faculty_name}</p>}
          {profileQ.data.kontakt_telefon && <p>Telefon: {profileQ.data.kontakt_telefon}</p>}
          {profileQ.data.datum_rodjenja && <p>Datum rođenja: {profileQ.data.datum_rodjenja}</p>}
          {profileQ.data.adresa && <p>Adresa: {profileQ.data.adresa}</p>}
          {profileQ.data.prosek != null && <p>Prosek: {profileQ.data.prosek}</p>}
          {profileQ.data.tehnologije.length > 0 && (
            <p>Tehnologije: {profileQ.data.tehnologije.map(t => t.naziv).join(', ')}</p>
          )}
          {profileQ.data.projekti.length > 0 && (
            <div className="stack" style={{ gap: 4 }}>
              <strong>Projekti:</strong>
              {profileQ.data.projekti.map(pr => (
                <div key={pr.id} className="muted">• {pr.opis} ({pr.datum_pocetka_izrade}{pr.datum_kraja_izrade_projekta ? ` – ${pr.datum_kraja_izrade_projekta}` : ''})</div>
              ))}
            </div>
          )}
          {profileQ.data.can_edit_until && (
            <p className="muted">Izmena profila dostupna od: {new Date(profileQ.data.can_edit_until).toLocaleString()}</p>
          )}
          <p>CV: {profileQ.data.has_cv ? 'Otpremljen' : 'Nije otpremljen'}</p>
          <div className="row" style={{ gap: 8, flexWrap: 'wrap' }}>
            {canEdit && (
              <button type="button" className="btn btn-primary" onClick={() => setEditing(true)}>Izmeni profil</button>
            )}
            <label className="btn btn-ghost">
              Otpremi PDF
              <input type="file" accept="application/pdf" hidden onChange={async (e) => {
                const f = e.target.files?.[0];
                if (!f) return;
                const fd = new FormData();
                fd.append('file', f);
                const res = await apiFetch('/students/profile/cv', { method: 'POST', body: fd });
                if (res.ok) void qc.invalidateQueries({ queryKey: ['student-profile'] });
              }} />
            </label>
            <button type="button" className="btn btn-ghost" disabled={!profileQ.data.has_cv}
              onClick={async () => {
                const res = await apiFetch('/students/profile/cv');
                if (res.ok) { const blob = await res.blob(); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'cv.pdf'; a.click(); }
              }}>Preuzmi CV</button>
            <button type="button" className="btn btn-ghost" onClick={() => exportMut.mutate()}>Izvoz podataka (JSON)</button>
            <button type="button" className="btn btn-ghost" onClick={() => delReqMut.mutate()}>Zatraži brisanje naloga</button>
          </div>
          {delReqMut.isSuccess && delReqMut.data && <p className="muted">{delReqMut.data.message}</p>}
        </div>
      )}
      {profileQ.data && editing && (
        <div className="card card-pad stack">
          <h3>Izmena profila</h3>
          <div className="row" style={{ gap: 8 }}>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Ime</label>
              <input className="input" value={form.ime} onChange={e => setForm(f => ({ ...f, ime: e.target.value }))} />
            </div>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Prezime</label>
              <input className="input" value={form.prezime} onChange={e => setForm(f => ({ ...f, prezime: e.target.value }))} />
            </div>
          </div>
          <div className="row" style={{ gap: 8 }}>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Telefon</label>
              <input className="input" value={form.kontakt_telefon} onChange={e => setForm(f => ({ ...f, kontakt_telefon: e.target.value }))} />
            </div>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Datum rođenja</label>
              <input className="input" type="date" value={form.datum_rodjenja} onChange={e => setForm(f => ({ ...f, datum_rodjenja: e.target.value }))} />
            </div>
          </div>
          <div className="stack">
            <label className="label">Adresa</label>
            <input className="input" value={form.adresa} onChange={e => setForm(f => ({ ...f, adresa: e.target.value }))} />
          </div>
          <div className="row" style={{ gap: 8 }}>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Prosek</label>
              <input className="input" type="number" step="0.01" min="0" max="10" value={form.prosek} onChange={e => setForm(f => ({ ...f, prosek: e.target.value }))} />
            </div>
            <div className="stack" style={{ flex: 1 }}>
              <label className="label">Fakultet</label>
              <select className="input" value={form.fakultet_id} onChange={e => setForm(f => ({ ...f, fakultet_id: Number(e.target.value) }))}>
                <option value={0}>Izaberite fakultet</option>
                {fakultetiQ.data?.map(fak => (
                  <option key={fak.id} value={fak.id}>{fak.naziv}</option>
                ))}
              </select>
            </div>
          </div>
          {techQ.data && (
            <div className="stack">
              <label className="label">Tehnologije</label>
              <div className="row" style={{ gap: 8, flexWrap: 'wrap' }}>
                {techQ.data.map(t => (
                  <label key={t.id} className="row" style={{ gap: 4 }}>
                    <input type="checkbox" checked={form.tehnologija_ids.includes(t.id)}
                      onChange={() => setForm(f => ({
                        ...f, tehnologija_ids: f.tehnologija_ids.includes(t.id)
                          ? f.tehnologija_ids.filter(x => x !== t.id) : [...f.tehnologija_ids, t.id],
                      }))} />
                    <span>{t.naziv}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
          <div className="stack">
            <label className="label">Projekti</label>
            {form.projekti.map((pr, i) => (
              <div key={i} className="card card-pad stack" style={{ background: 'var(--color-bg-subtle, #f5f5f5)' }}>
                <input className="input" placeholder="Opis projekta" value={pr.opis}
                  onChange={e => { const upd = [...form.projekti]; upd[i] = { ...upd[i], opis: e.target.value }; setForm(f => ({ ...f, projekti: upd })); }} />
                <div className="row" style={{ gap: 8 }}>
                  <input className="input" type="date" value={pr.datum_pocetka_izrade}
                    onChange={e => { const upd = [...form.projekti]; upd[i] = { ...upd[i], datum_pocetka_izrade: e.target.value }; setForm(f => ({ ...f, projekti: upd })); }} />
                  <input className="input" type="date" value={pr.datum_kraja_izrade_projekta}
                    onChange={e => { const upd = [...form.projekti]; upd[i] = { ...upd[i], datum_kraja_izrade_projekta: e.target.value }; setForm(f => ({ ...f, projekti: upd })); }} />
                  <button type="button" className="btn btn-ghost" onClick={() => setForm(f => ({ ...f, projekti: f.projekti.filter((_, j) => j !== i) }))}>Ukloni</button>
                </div>
              </div>
            ))}
            <button type="button" className="btn btn-ghost"
              onClick={() => setForm(f => ({ ...f, projekti: [...f.projekti, { datum_pocetka_izrade: '', datum_kraja_izrade_projekta: '', opis: '' }] }))}>
              + Dodaj projekat
            </button>
          </div>
          <div className="row" style={{ gap: 8 }}>
            <button type="button" className="btn btn-primary" disabled={updateMut.isPending} onClick={() => updateMut.mutate()}>
              {updateMut.isPending ? 'Čuvanje…' : 'Sačuvaj'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => setEditing(false)}>Otkaži</button>
          </div>
          {updateMut.isError && <p style={{ color: 'var(--color-danger)' }}>{(updateMut.error as Error).message}</p>}
        </div>
      )}
    </div>
  );
}
