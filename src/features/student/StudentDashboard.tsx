import { useAuth } from '@state/auth';

export function StudentDashboard() {
  const { user } = useAuth();
  return (
    <div className="stack-lg">
      <h2 className="section-title" style={{ margin: 0 }}>Moj profil</h2>
      <div className="card card-pad">
        <div className="stack">
          <div className="row" style={{ gap: 12 }}>
            <span className="label">Ime:</span>
            <strong>{user?.name}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
