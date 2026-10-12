import React, { useState } from 'react';
import { INDIAN_STATES } from '../data/borewellData';

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  prefilledDepth?: number;
  contractorName?: string;
  onSuccess: (bookingId: string) => void;
}

export const BookingModal: React.FC<BookingModalProps> = ({
  isOpen,
  onClose,
  prefilledDepth = 450,
  contractorName,
  onSuccess
}) => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [state, setState] = useState('Karnataka');
  const [city, setCity] = useState('');
  const [depth, setDepth] = useState(prefilledDepth);
  const [purpose, setPurpose] = useState('Agricultural Farm');
  const [diameter, setDiameter] = useState('6.5" (Heavy Yield)');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};

    if (!name.trim()) errs.name = 'Full name is required';
    if (!phone.trim()) {
      errs.phone = 'Mobile number is required';
    } else if (!/^[6-9]\d{9}$/.test(phone.replace(/\D/g, ''))) {
      errs.phone = 'Enter valid 10-digit Indian mobile number';
    }
    if (!city.trim()) errs.city = 'Taluk or City is required';

    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }

    setErrors({});
    setIsSubmitting(true);

    setTimeout(() => {
      setIsSubmitting(false);
      const bookingRef = 'GB-' + Math.floor(100000 + Math.random() * 900000);
      onSuccess(bookingRef);
      onClose();
    }, 600);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-title">
              {contractorName ? `Request Direct Quote from ${contractorName}` : 'Book Borewell Rig & Groundwater Survey'}
            </div>
            <div style={{ fontSize: '12px', color: '#93c5fd', marginTop: '2px' }}>
              Free site feasibility inspection & guaranteed transparent per-foot pricing
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        <form className="modal-body" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input
              type="text"
              placeholder="e.g. Ramesh Patel"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            {errors.name && <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '4px' }}>{errors.name}</div>}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">WhatsApp / Phone *</label>
              <input
                type="tel"
                placeholder="10-digit mobile"
                className="form-input"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              {errors.phone && <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '4px' }}>{errors.phone}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Land Purpose</label>
              <select
                className="form-input"
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
              >
                <option value="Agricultural Farm">Agricultural Farm / Orchards</option>
                <option value="Residential Independent House">Residential Villa / House</option>
                <option value="Apartment / Gated Community">Apartment Complex</option>
                <option value="Industrial Factory">Industrial / Commercial Plant</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">State</label>
              <select
                className="form-input"
                value={state}
                onChange={(e) => setState(e.target.value)}
              >
                {INDIAN_STATES.filter(s => s !== 'All States').map(st => (
                  <option key={st} value={st}>{st}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Taluk / Village / City *</label>
              <input
                type="text"
                placeholder="e.g. Hosur, Devanahalli"
                className="form-input"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              />
              {errors.city && <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '4px' }}>{errors.city}</div>}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Estimated Depth (Feet)</label>
              <input
                type="number"
                min="100"
                max="1500"
                step="50"
                className="form-input"
                value={depth}
                onChange={(e) => setDepth(Number(e.target.value))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Bore Diameter</label>
              <select
                className="form-input"
                value={diameter}
                onChange={(e) => setDiameter(e.target.value)}
              >
                <option value="4.5 inches">4.5" (Domestic Compact)</option>
                <option value="6.5 inches (Heavy Yield)">6.5" (Standard Farm & High Yield)</option>
                <option value="8.0 inches (Commercial)">8.0" (Industrial / High Flow)</option>
              </select>
            </div>
          </div>

          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', fontSize: '12px', color: '#64748b', marginBottom: '18px', border: '1px solid #e2e8f0' }}>
            🔒 <strong>GoogleBore Guarantee:</strong> No unsolicited spam. Verified local contractors respond within 15 minutes with exact machine schedules and government-standard rate quotes.
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Routing to Rig Dispatcher...' : 'Confirm & Dispatch Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
