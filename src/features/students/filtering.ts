import { Student } from '@mock/students';
import { FilterState } from '@features/company/components/FilterPanel';

export function filterStudents(students: Student[], f: FilterState): Student[] {
  return students.filter((s) => {
    if (f.faculties.length && !f.faculties.includes(s.faculty)) return false;
    if (f.minGpa !== undefined && s.gpa < f.minGpa) return false;
    if (f.minYears !== undefined && s.yearsOfExperience < f.minYears) return false;
    if (f.skills.length && !f.skills.every((sk) => s.skills.includes(sk))) return false;
    if (f.knowledge.length && !f.knowledge.every((kn) => s.knowledge.includes(kn))) return false;
    if (f.query) {
      const q = f.query.toLowerCase();
      const name = `${s.firstName} ${s.lastName}`.toLowerCase();
      const skills = s.skills.join(' ').toLowerCase();
      const knowledge = s.knowledge.join(' ').toLowerCase();
      if (!name.includes(q) && !skills.includes(q) && !knowledge.includes(q)) return false;
    }
    return true;
  });
}


