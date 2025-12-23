import { useEffect, useMemo, useState } from 'react';
import { FilterPanel, FilterState, defaultFilterState } from './components/FilterPanel';
import { StudentsResults } from '@features/students/StudentsResults';
import { filterStudents } from '@features/students/filtering';
import type { Student } from '@mock/students';

export function CompanyDashboard() {
  const [filters, setFilters] = useState<FilterState>(defaultFilterState);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/students/')
      .then(res => res.json())
      .then(data => {
        const transformed: Student[] = data.map((s: any) => ({
          id: String(s.id),
          firstName: s.ime,
          lastName: s.prezime,
          faculty: '',
          gpa: 0,
          skills: [],
          knowledge: [],
          yearsOfExperience: 0,
          location: ''
        }));
        setStudents(transformed);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const results = useMemo(() => filterStudents(students, filters), [students, filters]);

  if (loading) {
    return (
      <div className="stack-lg" style={{ textAlign: 'center', padding: '40px' }}>
        <div>Učitavanje studenata...</div>
      </div>
    );
  }

  return (
    <div className="stack-lg">
      <div className="row space-between section-sticky">
        <h2 className="section-title" style={{ margin: 0 }}>Pretraga studenata</h2>
        <div className="row" style={{ gap: 8 }}>
          <span className="pill">{results.length} rezultata</span>
          <button className="btn btn-ghost" onClick={() => setFilters(defaultFilterState)}>
            Resetuj filtere
          </button>
        </div>
      </div>
      <div className="grid layout-3-cols">
        <div className="card card-pad sticky">
          <FilterPanel value={filters} onChange={setFilters} />
        </div>
        <div className="grid cards-wide section-below" style={{ gridColumn: 'span 2' }}>
          <StudentsResults students={results} />
        </div>
      </div>
    </div>
  );
}