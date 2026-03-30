"""Load reference data. Run after table creation."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.fakultet import Fakultet
from app.models.tehnologija import Tehnologija

BEOGRADSKI_FAKULTETI = [
    "Arhitektonski fakultet",
    "Biološki fakultet",
    "Ekonomski fakultet",
    "Elektrotehnički fakultet",
    "Fakultet bezbednosti",
    "Fakultet organizacionih nauka",
    "Fakultet političkih nauka",
    "Fakultet sporta i fizičkog vaspitanja",
    "Fakultet za fizičku hemiju",
    "Fakultet za specijalnu edukaciju i rehabilitaciju",
    "Farmaceutski fakultet",
    "Filološki fakultet",
    "Filozofski fakultet",
    "Fizički fakultet",
    "Geografski fakultet",
    "Građevinski fakultet",
    "Hemijski fakultet",
    "Mašinski fakultet",
    "Matematički fakultet",
    "Medicinski fakultet",
    "Pravni fakultet",
    "Poljoprivredni fakultet",
    "Rudarsko-geološki fakultet",
    "Saobraćajni fakultet",
    "Stomatološki fakultet",
    "Šumarski fakultet",
    "Tehnički fakultet u Boru",
    "Tehnološko-metalurški fakultet",
    "Učiteljski fakultet",
    "Veterinarski fakultet",
    "Računarski fakultet",
]

TEHNOLOGIJE = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C",
    "C++",
    "C#",
    "Go",
    "Rust",
    "PHP",
    "Ruby",
    "Swift",
    "Kotlin",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "React",
    "Angular",
    "Vue.js",
    "Next.js",
    "Node.js",
    "Django",
    "FastAPI",
    "Spring Boot",
    ".NET",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "Git",
    "Linux",
    "HTML/CSS",
    "TensorFlow",
    "PyTorch",
]


def seed() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(Fakultet).first():
            print("Already seeded, skipping.")
            return

        for naziv in sorted(BEOGRADSKI_FAKULTETI):
            db.add(Fakultet(naziv=naziv))

        for tech in TEHNOLOGIJE:
            db.add(Tehnologija(naziv=tech))

        db.commit()
        print(f"Seed OK: {len(BEOGRADSKI_FAKULTETI)} fakulteta, {len(TEHNOLOGIJE)} tehnologija.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
