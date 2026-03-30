import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { API_BASE, ApiError } from '@services/api';

interface Fakultet {
  id: number;
  naziv: string;
}

interface Tehnologija {
  id: number;
  naziv: string;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

interface Props {
  onBack?: () => void;
}

export function StudentRegistrationForm({ onBack }: Props) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [consent, setConsent] = useState(false);
  const [ime, setIme] = useState('');
  const [prezime, setPrezime] = useState('');
  const [phone, setPhone] = useState('');
  const [datumRodjenja, setDatumRodjenja] = useState('');
  const [adresa, setAdresa] = useState('');
  const [prosek, setProsek] = useState('');
  const [fakultetId, setFakultetId] = useState<number | ''>('');
  const [selectedTech, setSelectedTech] = useState<number[]>([]);
  const [projOpis, setProjOpis] = useState('');
  const [done, setDone] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fakultetiQ = useQuery({
    queryKey: ['fakulteti'],
    queryFn: () => getJson<Fakultet[]>('/fakulteti/'),
  });
  const techQ = useQuery({
    queryKey: ['tehnologije'],
    queryFn: () => getJson<Tehnologija[]>('/tehnologije/'),
  });

  const payload = useMemo(() => {
    const prosekNum = prosek.trim() === '' ? null : parseFloat(prosek);
    return {
      name: name.trim(),
      email: email.trim(),
      password,
      consent_data_processing: consent,
      ime: ime.trim(),
      prezime: prezime.trim(),
      kontakt_telefon: phone.trim() || null,
      datum_rodjenja: datumRodjenja || null,
      adresa: adresa.trim() || null,
      prosek: prosekNum !== null && !Number.isNaN(prosekNum) ? prosekNum : null,
      fakultet_id: fakultetId === '' ? 0 : fakultetId,
      projekti:
        projOpis.trim() === ''
          ? []
          : [
              {
                datum_pocetka_izrade: new Date().toISOString().slice(0, 10),
                datum_kraja_izrade_projekta: null,
                opis: projOpis.trim().slice(0, 1000),
              },
            ],
      tehnologija_ids: selectedTech,
    };
  }, [
    name,
    email,
    password,
    consent,
    ime,
    prezime,
    phone,
    datumRodjenja,
    adresa,
    prosek,
    projOpis,
    selectedTech,
  ]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (!consent) {
      setErr('Morate prihvatiti obradu podataka.');
      return;
    }
    if (fakultetId === '') {
      setErr('Izaberite fakultet.');
      return;
    }
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        let msg = 'Greška pri registraciji';
        try {
          const j = await res.json();
          msg = j.detail || j.error?.message || msg;
        } catch {
          /* ignore */
        }
        throw new ApiError(msg, res.status);
      }
      const j = await res.json();
      setDone(j.message || 'Registracija primljena.');
      setPassword('');
    } catch (ex: unknown) {
      setErr(ex instanceof ApiError ? ex.message : 'Greška');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleTech = (id: number) => {
    setSelectedTech((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  if (done) {
    return (
      <div className="card card-pad stack">
        <p>{done}</p>
        {onBack && (
          <button type="button" className="btn btn-ghost" onClick={onBack}>
            Nazad
          </button>
        )}
      </div>
    );
  }

  return (
    <form className="card card-pad stack-lg" onSubmit={submit}>
      <p className="muted" style={{ margin: 0 }}>
        Lozinka: min. 12 karaktera, veliko/malo slovo, cifra i specijalni karakter.
      </p>
      <div className="grid grid-cols-2" style={{ gap: 12 }}>
        <input className="input" placeholder="Ime i prezime (za nalog) *" value={name} onChange={(e) => setName(e.target.value)} required />
        <input className="input" type="email" placeholder="Email *" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <input className="input" type="password" placeholder="Lozinka *" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <div className="grid grid-cols-2" style={{ gap: 12 }}>
        <input className="input" placeholder="Ime *" value={ime} onChange={(e) => setIme(e.target.value)} required />
        <input className="input" placeholder="Prezime *" value={prezime} onChange={(e) => setPrezime(e.target.value)} required />
      </div>
      <input className="input" placeholder="Telefon" value={phone} onChange={(e) => setPhone(e.target.value)} />
      <input className="input" type="date" placeholder="Datum rođenja" value={datumRodjenja} onChange={(e) => setDatumRodjenja(e.target.value)} />
      <input className="input" placeholder="Adresa" value={adresa} onChange={(e) => setAdresa(e.target.value)} />
      <input className="input" placeholder="Prosek (opciono)" value={prosek} onChange={(e) => setProsek(e.target.value)} />
      <select
        className="select"
        value={fakultetId === '' ? '' : String(fakultetId)}
        onChange={(e) => {
          const v = e.target.value;
          setFakultetId(v === '' ? '' : Number(v));
        }}
        required
      >
        <option value="">Fakultet *</option>
        {fakultetiQ.data?.map((f) => (
          <option key={f.id} value={f.id}>
            {f.naziv}
          </option>
        ))}
      </select>
      <div className="stack" style={{ gap: 8 }}>
        <span className="label">Tehnologije</span>
        <div className="row" style={{ flexWrap: 'wrap', gap: 8 }}>
          {techQ.data?.map((t) => (
            <label key={t.id} className="row" style={{ gap: 6 }}>
              <input type="checkbox" checked={selectedTech.includes(t.id)} onChange={() => toggleTech(t.id)} />
              {t.naziv}
            </label>
          ))}
        </div>
      </div>
      <textarea
        className="input"
        style={{ minHeight: 80 }}
        placeholder="Kratak opis jednog projekta (opciono)"
        value={projOpis}
        onChange={(e) => setProjOpis(e.target.value)}
      />
      <label className="row" style={{ gap: 8 }}>
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
        Slažem se sa obradom ličnih podataka (ZZPL).
      </label>
      {err && <div style={{ color: 'var(--color-danger)' }}>{err}</div>}
      <div className="row space-between">
        {onBack && (
          <button type="button" className="btn btn-ghost" onClick={onBack}>
            Nazad
          </button>
        )}
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Šaljem...' : 'Registruj se'}
        </button>
      </div>
    </form>
  );
}
