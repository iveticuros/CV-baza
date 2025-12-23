import { useState } from 'react';
import { Student } from '@mock/students';

export function StudentsResults(props: { students: Student[] }) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const toggleExpand = (id: string) => setExpanded((m) => ({ ...m, [id]: !m[id] }));

  return (
    <div className="grid cards-wide">
      {props.students.map((s) => (
        <article key={s.id} className="card card-pad">
          <div className="stack">
            <div className="row" style={{ alignItems: 'flex-start', gap: 14 }}>
              <div className="avatar">{initials(s.firstName, s.lastName)}</div>
              <div className="stack" style={{ width: '100%' }}>
                <h3 style={{ margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {s.firstName} {s.lastName}
                </h3>
                {s.faculty && (
                  <div className="muted" style={{ marginTop: -2 }}>{s.faculty}</div>
                )}
                {(s.gpa > 0 || s.yearsOfExperience > 0) && (
                  <div className="meta" style={{ marginTop: 4 }}>
                    {s.gpa > 0 && <span>Prosek {s.gpa.toFixed(1)}</span>}
                    {s.yearsOfExperience > 0 && <span>Iskustvo {experienceLabel(s.yearsOfExperience)}</span>}
                  </div>
                )}
              </div>
            </div>
            {(() => {
              const { languages, technologies } = splitSkills(s.skills);
              return (
                <>
                  {languages.length > 0 && (
                    <div className="tag-group" style={{ marginTop: 6 }}>
                      <div className="group-title">Jezici</div>
                      <div className={`skills-row${expanded[s.id] ? ' expanded' : ''}`}>
                        {languages.map((sk) => (
                          <span key={`lang-${sk}`} className="pill">{sk}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {technologies.length > 0 && (
                    <div className="tag-group" style={{ marginTop: 6 }}>
                      <div className="group-title">Tehnologije</div>
                      <div className={`skills-row${expanded[s.id] ? ' expanded' : ''}`}>
                        {technologies.map((sk) => (
                          <span key={`tech-${sk}`} className="pill">{sk}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              );
            })()}
            {(s.skills.length > 8) && (
              <div className="row" style={{ justifyContent: 'flex-end' }}>
                <button className="btn btn-ghost" onClick={() => toggleExpand(s.id)}>
                  {expanded[s.id] ? 'Sakrij veštine' : 'Prikaži više'}
                </button>
              </div>
            )}
            <div className="row space-between" style={{ alignItems: 'center', marginTop: 6 }}>
              {s.location && <div className="muted">{s.location}</div>}
              <button className="btn btn-outline">Kontakt</button>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function initials(first: string, last: string) {
  const a = (first?.[0] ?? '').toUpperCase();
  const b = (last?.[0] ?? '').toUpperCase();
  return `${a}${b}` || 'ST';
}

function experienceLabel(years: number) {
  if (years < 1) return '0-1 god.';
  if (years === 1) return '1 god.';
  return `${years} god.`;
}

const LANGUAGE_SET: Set<string> = new Set([
  'JavaScript', 'TypeScript', 'Java', 'Python', 'C', 'C++', 'C#', 'Go', 'Rust',
  'PHP', 'Ruby', 'Kotlin', 'Swift', 'Scala', 'R', 'Matlab', 'SQL'
]);

function splitSkills(skills: string[]): { languages: string[]; technologies: string[] } {
  const languages: string[] = [];
  const technologies: string[] = [];
  for (const s of skills) {
    if (LANGUAGE_SET.has(s)) languages.push(s);
    else technologies.push(s);
  }
  return { languages, technologies };
}