import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { API_BASE } from '../../../services/api';

interface Fakultet {
  id: number;
  naziv: string;
}

interface StudentRegistrationFormData {
  fakultet: string;
  datumPocetkaStudija: string;
  datumKrajaStudija: string;
  tipStudija: 'Osnovne studije' | 'Master studije' | 'Doktorske studije' | '';
  ime: string;
  prezime: string;
  email: string;
  kontaktTelefon: string;
  studijskiProgram: string;
}

type FormErrors = Partial<Record<keyof StudentRegistrationFormData, string>>;

interface DateValidationErrors {
  startDateError?: string;
  endDateError?: string;
}

async function fetchFakulteti(signal?: AbortSignal): Promise<Fakultet[]> {
  const res = await fetch(`${API_BASE}/fakulteti/`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    signal,
  });
  if (!res.ok) throw new Error(`Failed to fetch fakulteti: ${res.status}`);
  return res.json();
}

interface StudentRegistrationFormProps {
  onBack?: () => void;
}

export function StudentRegistrationForm({ onBack }: StudentRegistrationFormProps) {
  const [formData, setFormData] = useState<StudentRegistrationFormData>({
    fakultet: '',
    datumPocetkaStudija: '',
    datumKrajaStudija: '',
    tipStudija: '',
    ime: '',
    prezime: '',
    email: '',
    kontaktTelefon: '',
    studijskiProgram: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [focusedDateField, setFocusedDateField] = useState<'start' | 'end' | null>(null);

  const fakultetiQuery = useQuery({
    queryKey: ['fakulteti'],
    queryFn: ({ signal }) => fetchFakulteti(signal),
    refetchOnWindowFocus: false,
  });

  // Validation helper functions
  const validateEmail = (email: string): string | undefined => {
    if (!email.trim()) {
      return 'Email je obavezan';
    }
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email.trim())) {
      return 'Format email-a nije validan';
    }
    return undefined;
  };

  const validatePhone = (phone: string): string | undefined => {
    if (!phone.trim()) {
      return 'Kontakt telefon je obavezan';
    }
    const cleanedPhone = phone.replace(/[\s\-/()]/g, '');
    const phoneRegex = /^(\+3816[0-9]{8}|06[0-9]{8})$/;
    if (!phoneRegex.test(cleanedPhone)) {
      return 'Telefon nije validan. Format: +381 60 123 4567 ili 060 123 4567';
    }
    return undefined;
  };

  const validateDateRange = (
    startDate: string,
    endDate: string
  ): DateValidationErrors => {
    const errors: DateValidationErrors = {};
    
    if (!startDate) {
      errors.startDateError = 'Datum početka studija je obavezan';
      return errors;
    }

    if (endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (end <= start) {
        errors.endDateError = 'Datum kraja studija mora biti posle datuma početka studija';
      }
    }

    return errors;
  };

  const updateField = (field: keyof StudentRegistrationFormData, value: string) => {
    setFormData((prev) => {
      const updated = { ...prev, [field]: value };
      
      // Real-time date validation
      if (field === 'datumPocetkaStudija' || field === 'datumKrajaStudija') {
        const startDate = field === 'datumPocetkaStudija' ? value : updated.datumPocetkaStudija;
        const endDate = field === 'datumKrajaStudija' ? value : updated.datumKrajaStudija;
        const dateErrors = validateDateRange(startDate, endDate);
        setErrors((prevErrors) => ({
          ...prevErrors,
          datumPocetkaStudija: dateErrors.startDateError,
          datumKrajaStudija: dateErrors.endDateError,
        }));
      }
      
      return updated;
    });
    
    // Clear error for this field when user starts typing (except for date fields which are handled above)
    if (errors[field] && field !== 'datumPocetkaStudija' && field !== 'datumKrajaStudija') {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Required field validations
    if (!formData.fakultet.trim()) {
      newErrors.fakultet = 'Fakultet je obavezan';
    }
    if (!formData.tipStudija) {
      newErrors.tipStudija = 'Tip studija je obavezan';
    }
    if (!formData.ime.trim()) {
      newErrors.ime = 'Ime je obavezno';
    }
    if (!formData.prezime.trim()) {
      newErrors.prezime = 'Prezime je obavezno';
    }
    if (!formData.studijskiProgram.trim()) {
      newErrors.studijskiProgram = 'Studijski program je obavezan';
    }

    // Email validation
    const emailError = validateEmail(formData.email);
    if (emailError) {
      newErrors.email = emailError;
    }

    // Phone validation
    const phoneError = validatePhone(formData.kontaktTelefon);
    if (phoneError) {
      newErrors.kontaktTelefon = phoneError;
    }

    // Date validation
    const dateErrors = validateDateRange(
      formData.datumPocetkaStudija,
      formData.datumKrajaStudija
    );
    if (dateErrors.startDateError) {
      newErrors.datumPocetkaStudija = dateErrors.startDateError;
    }
    if (dateErrors.endDateError) {
      newErrors.datumKrajaStudija = dateErrors.endDateError;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      // TODO: Implement API call to submit student registration
      // await submitStudentRegistration(formData);
      
      // Reset form after successful submission
      setFormData({
        fakultet: '',
        datumPocetkaStudija: '',
        datumKrajaStudija: '',
        tipStudija: '',
        ime: '',
        prezime: '',
        email: '',
        kontaktTelefon: '',
        studijskiProgram: '',
      });
      
      alert('Registracija uspešna!');
    } catch (error) {
      alert('Došlo je do greške pri registraciji. Pokušajte ponovo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card card-pad">
      <div className="stack-lg">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="grid grid-cols-2" style={{ gap: '20px', alignItems: 'start' }}>
            {/* Ime */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              <input
                type="text"
                className="input"
                placeholder="Ime *"
                value={formData.ime}
                onChange={(e) => updateField('ime', e.target.value)}
              />
              {errors.ime && (
                <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.ime}</span>
              )}
            </div>

            {/* Prezime */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              <input
                type="text"
                className="input"
                placeholder="Prezime *"
                value={formData.prezime}
                onChange={(e) => updateField('prezime', e.target.value)}
              />
              {errors.prezime && (
                <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.prezime}</span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2" style={{ gap: '20px', alignItems: 'start' }}>
            {/* Email */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              <input
                type="email"
                className="input"
                placeholder="Email *"
                value={formData.email}
                onChange={(e) => updateField('email', e.target.value)}
                onBlur={() => {
                  const emailError = validateEmail(formData.email);
                  setErrors((prev) => ({ ...prev, email: emailError }));
                }}
              />
              {errors.email && (
                <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.email}</span>
              )}
            </div>

            {/* Kontakt telefon */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              <input
                type="tel"
                className="input"
                placeholder="Kontakt telefon *"
                value={formData.kontaktTelefon}
                onChange={(e) => updateField('kontaktTelefon', e.target.value)}
                onBlur={() => {
                  const phoneError = validatePhone(formData.kontaktTelefon);
                  setErrors((prev) => ({ ...prev, kontaktTelefon: phoneError }));
                }}
              />
              {errors.kontaktTelefon && (
                <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.kontaktTelefon}</span>
              )}
            </div>
          </div>

          {/* Fakultet */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {fakultetiQuery.isLoading ? (
              <div className="muted" style={{ padding: '10px 12px', border: '1px solid var(--color-border)', borderRadius: '10px' }}>Učitavanje fakulteta...</div>
            ) : fakultetiQuery.isError ? (
              <div style={{ color: '#EF4444', fontSize: '12px', padding: '10px 12px' }}>
                Greška pri učitavanju fakulteta
              </div>
            ) : (
              <select
                className="select"
                value={formData.fakultet}
                onChange={(e) => updateField('fakultet', e.target.value)}
                style={formData.fakultet === '' ? { color: '#6b7a90' } : {}}
              >
                <option value="" disabled>Fakultet *</option>
                {fakultetiQuery.data?.map((fakultet) => (
                  <option key={fakultet.id} value={fakultet.naziv}>
                    {fakultet.naziv}
                  </option>
                ))}
              </select>
            )}
            {errors.fakultet && (
              <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.fakultet}</span>
            )}
          </div>

          {/* Studijski program */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            <input
              type="text"
              className="input"
              placeholder="Studijski program *"
              value={formData.studijskiProgram}
              onChange={(e) => updateField('studijskiProgram', e.target.value)}
            />
            {errors.studijskiProgram && (
              <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.studijskiProgram}</span>
            )}
          </div>

          {/* Tip studija */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            <select
              className="select"
              value={formData.tipStudija}
              onChange={(e) => updateField('tipStudija', e.target.value)}
              style={formData.tipStudija === '' ? { color: '#6b7a90' } : {}}
            >
              <option value="" disabled>Tip studija *</option>
              <option value="Osnovne studije">Osnovne studije</option>
              <option value="Master studije">Master studije</option>
              <option value="Doktorske studije">Doktorske studije</option>
            </select>
            {errors.tipStudija && (
              <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.tipStudija}</span>
            )}
          </div>

          <div className="grid grid-cols-2" style={{ gap: '20px', alignItems: 'start' }}>
            {/* Datum početka studija */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0, position: 'relative' }}>
              <input
                type="date"
                className="input"
                value={formData.datumPocetkaStudija}
                onChange={(e) => updateField('datumPocetkaStudija', e.target.value)}
                onFocus={() => setFocusedDateField('start')}
                onBlur={() => setFocusedDateField(null)}
                style={{ 
                  color: formData.datumPocetkaStudija ? 'var(--color-ink)' : (focusedDateField === 'start' ? 'var(--color-ink)' : 'transparent')
                }}
              />
              {!formData.datumPocetkaStudija && focusedDateField !== 'start' && (
                <span style={{ 
                  position: 'absolute', 
                  left: '12px', 
                  top: '10px', 
                  pointerEvents: 'none',
                  color: '#6b7a90',
                  fontSize: '14px',
                  userSelect: 'none'
                }}>Datum početka studija *</span>
              )}
              {errors.datumPocetkaStudija && (
                <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.datumPocetkaStudija}</span>
              )}
            </div>

            {/* Datum kraja studija */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0, position: 'relative' }}>
              <input
                type="date"
                className="input"
                value={formData.datumKrajaStudija}
                onChange={(e) => updateField('datumKrajaStudija', e.target.value)}
                onFocus={() => setFocusedDateField('end')}
                onBlur={() => setFocusedDateField(null)}
                style={{ 
                  color: formData.datumKrajaStudija ? 'var(--color-ink)' : (focusedDateField === 'end' ? 'var(--color-ink)' : 'transparent')
                }}
              />
              {!formData.datumKrajaStudija && focusedDateField !== 'end' && (
                <span style={{ 
                  position: 'absolute', 
                  left: '12px', 
                  top: '10px', 
                  pointerEvents: 'none',
                  color: '#6b7a90',
                  fontSize: '14px',
                  userSelect: 'none'
                }}>Datum kraja studija (opciono)</span>
              )}
              {errors.datumKrajaStudija && (
                <span style={{ color: '#EF4444', fontSize: '12px', marginTop: '2px', lineHeight: '1.2' }}>{errors.datumKrajaStudija}</span>
              )}
            </div>
          </div>

          {/* Submit button */}
          <div className="row" style={{ justifyContent: 'space-between', marginTop: '8px', gap: '12px' }}>
            {onBack && (
              <button
                type="button"
                className="btn"
                onClick={onBack}
              >
                ← Nazad
              </button>
            )}
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting || fakultetiQuery.isLoading}
              style={{ flex: onBack ? '0 1 auto' : '0 0 auto', marginLeft: onBack ? '0' : 'auto' }}
            >
              {isSubmitting ? 'Registracija...' : 'Registruj se'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
