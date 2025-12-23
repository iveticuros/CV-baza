## BEST CV Baza

React + TypeScript (Vite) frontend i FastAPI backend za CV bazu u BEST duhu.

### Pokretanje
1. Instalacija:
   ```bash
   npm install
   ```

3. Dev server:
   ```bash
   npm run dev
   ```
4. Build:
   ```bash
   npm run build
   ```
5. Pregled build-a:
   ```bash
   npm run preview
   ```
### Backend
1. Otvoriti zaseban terminal
2. cd backend
3. pip install -r requirements.txt
4. **PostgreSQL setup:**
   - Pokreni PostgreSQL: `brew services start postgresql@15`
   - Kreiraj bazu: `createdb cv_baza`
   - (Ili koristi SQL skriptu: `psql -f create_database.sql`)
5. Pokreni server: `python3 -m uvicorn app.main:app --reload`

#### Baza podataka
- **Lokalno:** PostgreSQL (`postgresql://localhost/cv_baza`)
- **AWS:** Spremno za migraciju na AWS RDS/Aurora - pogledaj `backend/AWS_MIGRATION.md`
- **Nema potrebe za izmenom koda** - samo promeni `DATABASE_URL` u `.env` fajlu
   
### Struktura
- `src/app` - rute, layout
- `src/state` - globalno stanje (auth)
- `src/features` - funkcionalne celine (auth, company, student, admin, students)
- `src/components` - UI i routing pomoćne komponente
- `src/styles` - globalni stilovi i tema
- `src/mock` - mock podaci za razvoj

### Uloge i rute
- `/login` - prijava i izbor uloge (mock)
- `/company` - pretraga studenata sa filterima
- `/student` - kostur studentskog pogleda
- `/admin` - kostur admin pogleda

### Tema i brending
Boje su postavljene na BEST-like plavu/žutu (aproksimacija) u `src/styles/theme.css`.
Ako imate zvanične HEX vrednosti, ažurirajte:
```css
:root {
  --color-brand: #1C57A5;    /* zamenite zvaničnom plavom */
  --color-accent: #FFD24A;   /* zamenite zvaničnom žutom */
}
```
Zamenite `public/logo.svg` zvaničnim logom ako želite.

### AWS deploy (S3 + CloudFront)
1. Kreirajte S3 bucket (npr. `best-cv-baza`) i omogućite static website hosting.
2. (Preporučeno) Napravite CloudFront distribuciju ka S3 origin-u.
3. Podesite CloudFront error responses za SPA (404 -> index.html).
4. Napravite AWS korisnika sa `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`, `cloudfront:CreateInvalidation`.
5. Podesite GitHub tajne:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION` (npr. `eu-central-1`)
   - `S3_BUCKET` (ime vašeg bucket-a)
   - `CLOUDFRONT_DISTRIBUTION_ID` (opciono, za invalidation)
6. Pogledajte `.github/workflows/deploy.yml` za CI/CD.

### Napomene
- Backend koristi PostgreSQL bazu podataka
- Frontend koristi mock podatke za razvoj, ali može da se poveže sa backend API-jem
- Logika je slojevita; pogledi su po ulogama, ali zajednička logika (npr. filtriranje) živi u svojim modulima

# CV-baza
