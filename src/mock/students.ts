export type Student = {
  id: string;
  firstName: string;
  lastName: string;
  faculty: string;
  gpa: number;
  skills: string[];
  knowledge: string[];
  yearsOfExperience: number;
  location: string;
};

const faculties = [
  'ETF (Elektrotehnički)',
  'FTN (Tehničke nauke)',
  'PMF (Prirodno-matematički)',
  'RAF (Računarstvo)',
  'FON (Organizacione nauke)'
];

const skillsPool = ['JavaScript', 'TypeScript', 'React', 'Node.js', 'Java', 'Python', 'SQL', 'AWS', 'Docker', 'Kubernetes'];
const knowledgePool = ['Algoritmi', 'Strukture podataka', 'Mreže', 'Baze podataka', 'DevOps', 'Distribuirani sistemi'];
const locations = ['Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica'];

function pick<T>(arr: T[], n: number): T[] {
  const copy = [...arr];
  const out: T[] = [];
  while (out.length < n && copy.length) {
    const i = Math.floor(Math.random() * copy.length);
    out.push(copy.splice(i, 1)[0]);
  }
  return out;
}

function student(i: number): Student {
  const gpa = Math.round((6 + Math.random() * 4) * 10) / 10;
  const years = Math.floor(Math.random() * 6);
  return {
    id: String(i + 1),
    firstName: ['Milan', 'Jovana', 'Nikola', 'Ana', 'Marko', 'Ivana', 'Luka', 'Teodora', 'Vuk', 'Katarina'][i % 10],
    lastName: ['Petrović', 'Janković', 'Marković', 'Ilić', 'Nikolić', 'Kovačević'][i % 6],
    faculty: faculties[i % faculties.length],
    gpa,
    yearsOfExperience: years,
    skills: pick(skillsPool, 4 + (i % 4)),
    knowledge: pick(knowledgePool, 2 + (i % 3)),
    location: locations[i % locations.length]
  };
}

export const allStudents: Student[] = Array.from({ length: 28 }, (_, i) => student(i));


