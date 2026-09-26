import { useState, useEffect } from 'react';

function App() {
  const [reports, setReports] = useState([]);
  const [location, setLocation] = useState('');
  const [fieldNotes, setFieldNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const API_URL = 'http://localhost:8000/api/reports';

  const fetchReports = async () => {
    try {
      const response = await fetch(API_URL);
      if (response.ok) {
        const data = await response.json();
        setReports(data);
      }
    } catch (error) {
      console.error('Failed to fetch field reports:', error);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setFieldNotes((prev) => (prev ? `${prev} ${transcript}` : transcript));
    };

    recognition.start();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!location || !fieldNotes) return;

    setLoading(true);
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, field_notes: fieldNotes }),
      });

      if (response.ok) {
        setLocation('');
        setFieldNotes('');
        await fetchReports();
      }
    } catch (error) {
      console.error('Failed to submit report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">Field Reporting Terminal</h1>
      </header>

      <section className="form-panel">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="location">Sector / Location ID</label>
            <input
              id="location"
              type="text"
              placeholder="e.g. Substation Alpha"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label htmlFor="notes" style={{ margin: 0 }}>Field Log Notes (Voice or Text)</label>
              <button
                type="button"
                onClick={startListening}
                style={{
                  background: isListening ? '#ff0055' : '#00ff66',
                  color: '#000',
                  border: 'none',
                  padding: '6px 12px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  borderRadius: '4px',
                  fontSize: '0.8rem'
                }}
              >
                {isListening ? '🔴 Listening...' : '🎙️ Record Voice Note'}
              </button>
            </div>
            <textarea
              id="notes"
              rows="4"
              placeholder="Speak or enter operational observations..."
              value={fieldNotes}
              onChange={(e) => setFieldNotes(e.target.value)}
              required
            ></textarea>
          </div>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? 'PROCESSING ENTRY...' : 'SUBMIT FIELD REPORT'}
          </button>
        </form>
      </section>

      <section className="log-panel">
        <h2 style={{ color: '#ffffff', marginTop: 0 }}>System Logs</h2>
        {reports.length === 0 ? (
          <p style={{ color: '#888' }}>No logs recorded.</p>
        ) : (
          reports.map((item) => (
            <div key={item.id} className="report-card">
              <div className="report-meta">
                ID #{item.id} | <span className="report-location">{item.location}</span> | {item.timestamp}
              </div>
              <p style={{ margin: '8px 0', fontSize: '1.05rem', color: '#ccc' }}>
                <strong>Raw:</strong> {item.field_notes}
              </p>
              {item.ai_summary && (
                <div className="ai-box">
                  {item.ai_summary}
                </div>
               )}
            </div>
          ))
        )}
      </section>
    </div>
  );
}

export default App;