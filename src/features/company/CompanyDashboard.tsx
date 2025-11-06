import { useMemo, useState } from 'react';
import { FilterPanel, FilterState, defaultFilterState } from './components/FilterPanel';
import { StudentsResults } from '@features/students/StudentsResults';
import { allStudents } from '@mock/students';
import { filterStudents } from '@features/students/filtering';

export function CompanyDashboard() {
  const [filters, setFilters] = useState<FilterState>(defaultFilterState);
  const results = useMemo(() => filterStudents(allStudents, filters), [filters]);

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


