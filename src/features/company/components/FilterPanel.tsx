import { useState, useEffect } from 'react';

export type FilterState = {
  query?: string;
  faculties: string[];
  minGpa?: number;
  maxGpa?: number;
  skills: string[];
  knowledge: string[];
  minYears?: number;
  maxYears?: number;
};

export const defaultSkills = [
  'JavaScript',
  'TypeScript',
  'React',
  'Node.js',
  'Java',
  'Python',
  'SQL',
  'AWS'
];
export const defaultKnowledge = ['Algoritmi', 'Strukture podataka', 'Mreže', 'Baze podataka', 'DevOps'];

export const defaultFilterState: FilterState = {
  query: '',
  faculties: [],
  minGpa: undefined,
  maxGpa: undefined,
  skills: [],
  knowledge: [],
  minYears: undefined,
  maxYears: undefined
};

export function FilterPanel(props: { value: FilterState; onChange: (v: FilterState) => void }) {
  const v = props.value;
  const set = (patch: Partial<FilterState>) => props.onChange({ ...v, ...patch });
  const [faculties, setFaculties] = useState<string[]>([]);
  const [loadingFaculties, setLoadingFaculties] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/fakulteti/')
      .then(res => res.json())
      .then(data => {
        const facultyNames = data.map((f: any) => f.naziv);
        setFaculties(facultyNames);
        setLoadingFaculties(false);
      })
      .catch(() => {
        setLoadingFaculties(false);
      });
  }, []);

  return (
    <div className="stack">
      <div className="stack">
        <label className="label">Pretraga</label>
        <input
          className="input"
          placeholder="Ime ili veština..."
          value={v.query ?? ''}
          onChange={(e) => set({ query: e.target.value })}
        />
      </div>
      <div className="stack">
        <label className="label">Fakultet</label>
        {loadingFaculties ? (
          <div className="muted" style={{ padding: '8px' }}>Učitavanje fakulteta...</div>
        ) : (
          <CheckboxSelect
            options={faculties}
            values={v.faculties}
            onChange={(values) => set({ faculties: values })}
          />
        )}
      </div>
      <div className="stack">
        <label className="label">Minimalan prosek: {v.minGpa ?? '—'}</label>
        <input
          type="range"
          min={6}
          max={10}
          step={0.1}
          value={v.minGpa ?? 6}
          onChange={(e) => set({ minGpa: Number(e.target.value) })}
        />
      </div>
      <div className="stack">
        <label className="label">Iskustvo</label>
        <select
          className="select"
          value={v.minYears ?? -1}
          onChange={(e) => {
            const val = Number(e.target.value);
            set({ minYears: val < 0 ? undefined : val });
          }}
        >
          <option value={-1}>Sve</option>
          <option value={0}>0+ godina</option>
          <option value={1}>1+ godina</option>
          <option value={2}>2+ godine</option>
          <option value={3}>3+ godine</option>
          <option value={5}>5+ godina</option>
        </select>
      </div>
    </div>
  );
}

function CheckboxSelect(props: { options: string[]; values: string[]; onChange: (values: string[]) => void }) {
  const toggle = (opt: string) => {
    const exists = props.values.includes(opt);
    if (exists) props.onChange(props.values.filter((v) => v !== opt));
    else props.onChange([...props.values, opt]);
  };
  return (
    <div className="stack">
      {props.options.map((opt) => {
        const id = `chk-${opt}`;
        const checked = props.values.includes(opt);
        return (
          <label key={opt} className="row" style={{ gap: 8 }}>
            <input
              type="checkbox"
              name="faculties"
              id={id}
              checked={checked}
              onChange={() => toggle(opt)}
            />
            <span>{opt}</span>
          </label>
        );
      })}
    </div>
  );
}