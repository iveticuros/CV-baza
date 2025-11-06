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

export const defaultFaculties = [
  'ETF (Elektrotehnički)',
  'FTN (Tehničke nauke)',
  'PMF (Prirodno-matematički)',
  'RAF (Računarstvo)',
  'FON (Organizacione nauke)'
];

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
        <CheckboxSelect
          options={defaultFaculties}
          values={v.faculties}
          onChange={(values) => set({ faculties: values })}
        />
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

function MultiSelect(props: { options: string[]; values: string[]; onChange: (values: string[]) => void }) {
  const toggle = (opt: string) => {
    const exists = props.values.includes(opt);
    if (exists) props.onChange(props.values.filter((v) => v !== opt));
    else props.onChange([...props.values, opt]);
  };
  return (
    <div className="chips row" style={{ flexWrap: 'wrap', gap: 8, padding: 8 }}>
      {props.options.map((opt) => {
        const active = props.values.includes(opt);
        return (
          <button
            key={opt}
            type="button"
            onClick={() => toggle(opt)}
            className={`pill${active ? ' is-active' : ''}`}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

function RadioSelect(props: { options: string[]; value: string; onChange: (value: string) => void }) {
  return (
    <div className="stack">
      {props.options.map((opt) => {
        const id = `opt-${opt}`;
        return (
          <label key={opt} className="row" style={{ gap: 8 }}>
            <input
              type="radio"
              name="faculty"
              id={id}
              checked={props.value === opt}
              onChange={() => props.onChange(props.value === opt ? '' : opt)}
            />
            <span>{opt}</span>
          </label>
        );
      })}
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


