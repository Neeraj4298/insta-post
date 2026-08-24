import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Video, Play, Download, Clock, Zap, CheckCircle2, 
  AlertCircle, RefreshCw, BarChart2, Layers, Scissors, Film
} from 'lucide-react';

export default function App() {
  const [urlOrPath, setUrlOrPath] = useState('');
  const [title, setTitle] = useState('');
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [activeProject, setActiveProject] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [rankedClips, setRankedClips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewVideoUrl, setPreviewVideoUrl] = useState(null);

  // Fetch project list
  const fetchProjects = async () => {
    try {
      const res = await fetch('/api/projects');
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0 && !activeProjectId) {
          setActiveProjectId(data[0].project_id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Poll active project details and candidate clips
  useEffect(() => {
    if (!activeProjectId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/projects/${activeProjectId}`);
        if (res.ok) {
          const projData = await res.json();
          setActiveProject(projData);

          // Auto-trigger missing pipeline steps sequentially
          if (projData.status === 'AUDIO_EXTRACTED') {
            fetch(`/api/projects/${activeProjectId}/transcribe`, { method: 'POST' });
          } else if (projData.status === 'TRANSCRIBED') {
            fetch(`/api/projects/${activeProjectId}/analyze`, { method: 'POST' });
          } else if (projData.status === 'ANALYZED') {
            fetch(`/api/projects/${activeProjectId}/rank`, { method: 'POST' });
          }

          // Fetch candidates / ranked clips when ready
          if (['ANALYZED', 'RANKING', 'READY_FOR_REVIEW', 'RENDERING', 'COMPLETED'].includes(projData.status)) {
            const rankedRes = await fetch(`/api/projects/${activeProjectId}/ranked`);
            if (rankedRes.ok) {
              const rClips = await rankedRes.json();
              setRankedClips(rClips);
            }
          }
        }
      } catch (err) {
        console.error("Error polling project:", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeProjectId]);

  // Create new project pipeline
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!urlOrPath.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url_or_path: urlOrPath, title: title.trim() || undefined })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to create project");
      }

      const newProj = await res.json();
      setActiveProjectId(newProj.project_id);
      setUrlOrPath('');
      setTitle('');
      fetchProjects();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Trigger FFmpeg rendering
  const handleRenderClip = async (candidateId) => {
    if (!activeProjectId) return;
    try {
      await fetch(`/api/projects/${activeProjectId}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clip_ids: [candidateId], aspect_ratio: "9:16" })
      });
    } catch (err) {
      console.error("Render trigger failed:", err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '2rem 1.5rem', maxWidth: '1280px', margin: '0 auto' }}>
      
      {/* Header Bar */}
      <header className="glass-panel" style={{ padding: '1.25rem 2rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)', padding: '0.6rem', borderRadius: '12px', display: 'flex' }}>
            <Scissors size={24} color="#090d16" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
              ClipForge <span className="gold-text">Local</span>
            </h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Offline AI Video Reel Generator (CPU INT8)</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', padding: '0.35rem 0.8rem', borderRadius: '20px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Zap size={14} /> Local Hardware Mode (8GB RAM)
          </span>
        </div>
      </header>

      {/* Main Content Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '2rem' }}>
        
        {/* Left Sidebar: Form & Workspace Projects */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Input Form */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Video size={18} color="var(--gold-primary)" /> Ingest Video
            </h2>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                  YouTube URL or File Path
                </label>
                <input 
                  type="text" 
                  placeholder="https://youtu.be/... or /path/video.mp4"
                  value={urlOrPath}
                  onChange={(e) => setUrlOrPath(e.target.value)}
                  style={{
                    width: '100%', padding: '0.75rem', borderRadius: '8px',
                    background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-color)',
                    color: '#fff', fontSize: '0.875rem'
                  }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                  Project Title (Optional)
                </label>
                <input 
                  type="text" 
                  placeholder="e.g. Sunday Sermon Highlights"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  style={{
                    width: '100%', padding: '0.75rem', borderRadius: '8px',
                    background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-color)',
                    color: '#fff', fontSize: '0.875rem'
                  }}
                />
              </div>

              {error && (
                <div style={{ color: '#f87171', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <AlertCircle size={14} /> {error}
                </div>
              )}

              <button 
                type="submit" 
                disabled={loading}
                style={{
                  width: '100%', padding: '0.85rem', borderRadius: '8px', border: 'none',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  color: '#000', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer',
                  display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem',
                  boxShadow: '0 4px 14px rgba(245, 158, 11, 0.3)'
                }}
              >
                {loading ? <RefreshCw className="spin" size={18} /> : <Sparkles size={18} />} 
                {loading ? 'Starting Pipeline...' : 'Generate AI Reels'}
              </button>
            </form>
          </div>

          {/* Project List History */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>
              Projects Workspace ({projects.length})
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
              {projects.map((proj) => (
                <div 
                  key={proj.project_id}
                  onClick={() => setActiveProjectId(proj.project_id)}
                  className="glass-card"
                  style={{
                    padding: '0.85rem', cursor: 'pointer',
                    borderColor: activeProjectId === proj.project_id ? 'var(--gold-primary)' : 'var(--border-color)',
                    background: activeProjectId === proj.project_id ? 'rgba(245, 158, 11, 0.08)' : 'transparent'
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {proj.title}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <span>{proj.project_id}</span>
                    <span style={{ color: proj.status === 'COMPLETED' || proj.status === 'READY_FOR_REVIEW' ? '#34d399' : '#fbbf24' }}>
                      {proj.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </aside>

        {/* Right Main Dashboard Panel */}
        <main style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {activeProject ? (
            <>
              {/* Project Status Pipeline Bar */}
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{activeProject.title}</h2>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>ID: {activeProject.project_id}</p>
                  </div>
                  <span style={{ padding: '0.4rem 1rem', borderRadius: '20px', background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', fontWeight: 700, fontSize: '0.85rem' }}>
                    Status: {activeProject.status}
                  </span>
                </div>

                {/* Pipeline Step Badges */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginTop: '1.25rem' }}>
                  {[
                    { label: '1. Ingestion & Audio', done: ['AUDIO_EXTRACTED', 'TRANSCRIBING', 'TRANSCRIBED', 'ANALYZING', 'ANALYZED', 'RANKING', 'READY_FOR_REVIEW', 'RENDERING', 'COMPLETED'].includes(activeProject.status) },
                    { label: '2. Whisper Speech-to-Text', done: ['TRANSCRIBED', 'ANALYZING', 'ANALYZED', 'RANKING', 'READY_FOR_REVIEW', 'RENDERING', 'COMPLETED'].includes(activeProject.status) },
                    { label: '3. LLM Intelligence & Scoring', done: ['ANALYZED', 'RANKING', 'READY_FOR_REVIEW', 'RENDERING', 'COMPLETED'].includes(activeProject.status) },
                    { label: '4. Candidate Ranking & Reels', done: ['READY_FOR_REVIEW', 'RENDERING', 'COMPLETED'].includes(activeProject.status) }
                  ].map((step, i) => (
                    <div key={i} style={{
                      padding: '0.6rem 0.8rem', borderRadius: '8px', fontSize: '0.75rem',
                      background: step.done ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255,255,255,0.03)',
                      border: `1px solid ${step.done ? 'rgba(16, 185, 129, 0.3)' : 'var(--border-color)'}`,
                      color: step.done ? '#34d399' : 'var(--text-muted)',
                      display: 'flex', alignItems: 'center', gap: '0.4rem'
                    }}>
                      <CheckCircle2 size={14} color={step.done ? '#34d399' : '#64748b'} />
                      {step.label}
                    </div>
                  ))}
                </div>
              </div>

              {/* Ranked Reels Candidates Grid */}
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Film size={20} color="var(--gold-primary)" />
                  Top Ranked Reels ({rankedClips.length})
                </h3>

                {rankedClips.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                    <RefreshCw className="spin" size={28} style={{ marginBottom: '0.75rem' }} />
                    <p>Processing pipeline... Analyzing viral clip moments.</p>
                  </div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
                    {rankedClips.map((clip, index) => (
                      <div key={clip.candidate_id || index} className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        
                        <div>
                          {/* Card Header: Rank & Score */}
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                            <span style={{ background: 'var(--gold-primary)', color: '#000', fontWeight: 800, padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem' }}>
                              RANK #{index + 1}
                            </span>
                            <div style={{ textAlign: 'right' }}>
                              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fbbf24' }}>
                                {clip.final_score}
                              </span>
                              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 100</span>
                            </div>
                          </div>

                          {/* Reel Title & Hook */}
                          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem' }}>{clip.title}</h4>
                          <blockquote style={{
                            fontSize: '0.825rem', fontStyle: 'italic', color: '#cbd5e1',
                            paddingLeft: '0.75rem', borderLeft: '3px solid var(--gold-primary)',
                            marginBottom: '1rem', background: 'rgba(255,255,255,0.02)', padding: '0.5rem 0.75rem', borderRadius: '0 6px 6px 0'
                          }}>
                            "{clip.hook}"
                          </blockquote>

                          {/* Timestamps & Duration */}
                          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            <span style={{ background: 'rgba(255,255,255,0.05)', padding: '0.25rem 0.5rem', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                              <Clock size={12} /> {clip.start}s - {clip.end}s
                            </span>
                            <span style={{ background: 'rgba(255,255,255,0.05)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                              Duration: {clip.duration}s
                            </span>
                          </div>

                          {/* Scores Breakdown */}
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem', fontSize: '0.725rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                            <div>Hook: <strong style={{ color: '#fff' }}>{clip.scores?.hook}</strong></div>
                            <div>Context: <strong style={{ color: '#fff' }}>{clip.scores?.standalone_context}</strong></div>
                            <div>Emotion: <strong style={{ color: '#fff' }}>{clip.scores?.emotional_impact}</strong></div>
                            <div>Shareable: <strong style={{ color: '#fff' }}>{clip.scores?.shareability}</strong></div>
                          </div>
                        </div>

                        {/* Card Footer Actions */}
                        <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
                          <button 
                            onClick={() => handleRenderClip(clip.candidate_id)}
                            style={{
                              flex: 1, padding: '0.6rem', borderRadius: '6px', border: 'none',
                              background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
                              color: '#fff', fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer',
                              display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.4rem'
                            }}
                          >
                            <Scissors size={14} /> Render 9:16 Reel
                          </button>

                          <button 
                            onClick={() => setPreviewVideoUrl(`/api/projects/${activeProjectId}/output/${clip.candidate_id}.mp4`)}
                            style={{
                              padding: '0.6rem', borderRadius: '6px', border: '1px solid var(--border-color)',
                              background: 'rgba(255,255,255,0.05)', color: '#fff', cursor: 'pointer',
                              display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}
                            title="Preview Rendered Video"
                          >
                            <Play size={14} />
                          </button>
                        </div>

                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="glass-panel" style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              <Film size={48} color="var(--gold-primary)" style={{ marginBottom: '1rem', opacity: 0.5 }} />
              <h3 style={{ fontSize: '1.25rem', color: '#fff', marginBottom: '0.5rem' }}>No Active Project Selected</h3>
              <p>Paste a YouTube URL or local video file path on the left to start generating reels.</p>
            </div>
          )}

        </main>
      </div>

      {/* Video Preview Modal */}
      {previewVideoUrl && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, padding: '2rem'
        }}>
          <div className="glass-panel" style={{ width: '400px', maxWidth: '100%', padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Rendered 9:16 Vertical Reel</h3>
              <button 
                onClick={() => setPreviewVideoUrl(null)}
                style={{ background: 'none', border: 'none', color: '#fff', fontSize: '1.25rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <video 
              controls 
              autoPlay 
              src={previewVideoUrl} 
              style={{ width: '100%', borderRadius: '12px', maxHeight: '600px', background: '#000' }}
            />

            <a 
              href={previewVideoUrl} 
              download 
              style={{
                marginTop: '1rem', padding: '0.75rem 1.5rem', borderRadius: '8px',
                background: 'var(--gold-primary)', color: '#000', fontWeight: 700,
                textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem'
              }}
            >
              <Download size={16} /> Download Reel MP4
            </a>
          </div>
        </div>
      )}

    </div>
  );
}
