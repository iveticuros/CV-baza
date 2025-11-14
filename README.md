## BEST CV Baza (Frontend)

React + TypeScript (Vite) frontend za CV bazu u BEST duhu. Backend nije uključen (mock podaci i login).

### Pokretanje
1. Instalacija:
   ```bash
   npm install
   ```

2. Query za react fetchovanje:
```npm install @tanstack/react-query
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
4. uvicorn app.main:app --reload

#### Bonus
   Instalirati sqlitebrowser za lep pregled podataka(dev)
   
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
- Autentikacija i podaci su mock (nema backend-a). Kada backend bude spreman, zameniti `src/mock` i logiku fetch-a realnim API pozivima i tokenima.
- Logika je slojevita; pogledi su po ulogama, ali zajednička logika (npr. filtriranje) živi u svojim modulima.

# CV-baza
