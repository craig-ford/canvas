import { getCanvas, getVbu } from '../api/canvas';
import { apiClient } from '../api/client';
import type { Canvas, Thesis, ProofPoint, Attachment } from '../api/canvas';

interface ReviewCommitment { text: string; order: number; }
interface ReviewAttachment { id: string; filename: string; label: string | null; size_bytes: number; }
interface Review {
  id: string;
  review_date: string;
  what_moved: string | null;
  what_learned: string | null;
  what_threatens: string | null;
  commitments: ReviewCommitment[];
  attachments: ReviewAttachment[];
}

const STATUS_LABELS: Record<string, string> = {
  not_started: 'Not Started', in_progress: 'In Progress', observed: 'Observed',
  not_observed: 'Not Observed', stalled: 'Stalled',
};
const STATUS_COLORS: Record<string, string> = {
  not_started: '#94a3b8', in_progress: '#f59e0b', observed: '#22c55e',
  not_observed: '#ef4444', stalled: '#6b7280',
};
const LANE_LABELS: Record<string, string> = { build: 'Build', sell: 'Sell', milk: 'Milk', reframe: 'Reframe' };
const LANE_COLORS: Record<string, string> = { build: '#3b82f6', sell: '#22c55e', milk: '#f59e0b', reframe: '#a855f7' };
const HEALTH_LABELS: Record<string, { icon: string; color: string }> = {
  'Not Started': { icon: '⚪', color: '#94a3b8' },
  'In Progress': { icon: '🟡', color: '#f59e0b' },
  'On Track': { icon: '🟢', color: '#22c55e' },
  'At Risk': { icon: '🔴', color: '#ef4444' },
};

function esc(v?: string | null): string {
  if (!v) return '';
  return v.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** Render rich text HTML safely — keep formatting tags, strip scripts */
function richHtml(html?: string | null): string {
  if (!html || html === '<p></p>' || html === '<p><br></p>') return '<span class="empty">—</span>';
  // Strip script tags but keep formatting
  return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
}

function plainOrEmpty(v?: string | null): string {
  if (!v) return '<span class="empty">—</span>';
  return esc(v);
}

function buildHtml(vbuName: string, canvas: Canvas, reviews: Review[], categories: { id: string; name: string; color?: string | null }[]): string {
  const lane = LANE_LABELS[canvas.lifecycle_lane] || canvas.lifecycle_lane || 'Not Set';
  const laneColor = LANE_COLORS[canvas.lifecycle_lane] || '#6b7280';
  const health = canvas.health_indicator || 'Not Started';
  const hi = HEALTH_LABELS[health] || HEALTH_LABELS['Not Started']!;

  // Currently testing
  let currentlyTestingHtml = '';
  if (canvas.currently_testing_type && canvas.currently_testing_id) {
    let label = '';
    if (canvas.currently_testing_type === 'thesis') {
      const t = canvas.theses.find(t => t.id === canvas.currently_testing_id);
      label = t ? `Thesis: ${esc(t.text)}` : 'Thesis (unknown)';
    } else {
      for (const t of canvas.theses) {
        const pp = t.proof_points.find(p => p.id === canvas.currently_testing_id);
        if (pp) { label = `Proof Point: ${esc(pp.description)} (from thesis "${esc(t.text)}")`; break; }
      }
      if (!label) label = 'Proof Point (unknown)';
    }
    currentlyTestingHtml = `
      <div class="section">
        <div class="sh">🔬 Currently Testing</div>
        <div class="testing-label">${label}</div>
      </div>`;
  }

  // Theses
  const thesesHtml = canvas.theses.length > 0
    ? [...canvas.theses].sort((a, b) => a.order - b.order).map((thesis, idx) => {
        const cat = categories.find(c => c.id === thesis.category_id);
        const catBadge = cat ? (() => {
          const parts = (cat.color || '#f3f4f6,#6b7280').split(',');
          return `<span class="cat" style="background:${parts[0]};color:${parts[1]};">${esc(cat.name)}</span>`;
        })() : '';

        const descHtml = thesis.description
          ? `<div class="thesis-desc">${richHtml(thesis.description)}</div>`
          : '';

        const pps = [...thesis.proof_points].sort((a, b) => a.order - b.order).map(pp => {
          const st = STATUS_LABELS[pp.status] || pp.status;
          const sc = STATUS_COLORS[pp.status] || '#94a3b8';

          const notesHtml = pp.notes
            ? `<div class="pp-field"><span class="pp-field-label">Notes</span><div class="pp-field-value rich">${richHtml(pp.notes)}</div></div>`
            : '';

          const evidenceHtml = pp.evidence_note
            ? `<div class="pp-field"><span class="pp-field-label">Evidence</span><div class="pp-field-value">${esc(pp.evidence_note)}</div></div>`
            : '';

          const attsHtml = (pp.attachments && pp.attachments.length > 0)
            ? `<div class="pp-field"><span class="pp-field-label">Attachments</span><div class="pp-attachments">${pp.attachments.map((a: Attachment) =>
                `<span class="att">📎 ${esc(a.label || a.filename)} <span class="att-size">(${(a.size_bytes / 1024).toFixed(0)} KB)</span></span>`
              ).join('')}</div></div>`
            : '';

          return `
            <div class="pp">
              <div class="pp-header">
                <span class="pp-desc">${esc(pp.description)}</span>
                <span class="pp-status" style="background:${sc}15;color:${sc};border:1px solid ${sc}40;">${st}</span>
              </div>
              ${notesHtml}${evidenceHtml}${attsHtml}
            </div>`;
        }).join('');

        const ppSection = thesis.proof_points.length > 0
          ? `<div class="pp-section"><div class="pp-section-title">Proof Points</div>${pps}</div>`
          : '';

        return `
          <div class="thesis">
            <div class="thesis-header">
              <span class="thesis-num">${idx + 1}</span>
              <span class="thesis-text">${esc(thesis.text)}</span>
              ${catBadge}
            </div>
            ${descHtml}
            ${ppSection}
          </div>`;
      }).join('')
    : '<div class="empty-block">No investment theses defined</div>';

  // Reviews
  const reviewsHtml = reviews.length > 0
    ? reviews.map(r => {
        const date = new Date(r.review_date).toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
        const fields = [
          r.what_moved ? `<div class="review-field"><strong>What moved forward:</strong><div class="rich">${richHtml(r.what_moved)}</div></div>` : '',
          r.what_learned ? `<div class="review-field"><strong>What we learned:</strong><div class="rich">${richHtml(r.what_learned)}</div></div>` : '',
          r.what_threatens ? `<div class="review-field"><strong>What threatens progress:</strong><div class="rich">${richHtml(r.what_threatens)}</div></div>` : '',
        ].filter(Boolean).join('');
        const commitments = r.commitments.length > 0
          ? `<div class="review-field"><strong>Commitments:</strong><ol class="commitments">${r.commitments.sort((a, b) => a.order - b.order).map(c => `<li>${esc(c.text)}</li>`).join('')}</ol></div>`
          : '';
        const atts = r.attachments.length > 0
          ? `<div class="review-field">${r.attachments.map(a => `<span class="att">📎 ${esc(a.label || a.filename)} (${Math.round(a.size_bytes / 1024)} KB)</span>`).join(' ')}</div>`
          : '';
        return `<div class="review"><div class="review-date">${date}</div>${fields}${commitments}${atts}</div>`;
      }).join('')
    : '<div class="empty-block">No reviews yet</div>';

  return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${esc(vbuName)} — Strategy Canvas</title>
<style>
@page { size: A4 landscape; margin: 12mm 14mm; }
@media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, 'Segoe UI', system-ui, sans-serif; color: #1e293b; font-size: 10px; line-height: 1.4; }

/* Header */
.header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0f172a; padding-bottom: 10px; margin-bottom: 12px; }
.header h1 { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
.header-product { font-size: 12px; color: #64748b; }
.header-right { display: flex; align-items: center; gap: 10px; }
.badge-lane { display: inline-block; padding: 4px 14px; border-radius: 14px; font-size: 11px; font-weight: 700; color: white; }
.badge-health { font-size: 12px; font-weight: 600; }

/* Sections */
.section { border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 12px; margin-bottom: 10px; }
.sh { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #64748b; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 1px solid #f1f5f9; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 6px; }

/* Fields */
.field { margin-bottom: 6px; }
.field-label { font-size: 8.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #94a3b8; display: block; margin-bottom: 2px; }
.field-value { font-size: 10px; color: #334155; }
.field-value.rich p { margin: 2px 0; }
.field-value.rich ul, .field-value.rich ol { margin: 2px 0 2px 16px; }
.empty { color: #cbd5e1; font-style: italic; }
.empty-block { color: #cbd5e1; font-style: italic; padding: 8px 0; font-size: 10px; }

/* Theses */
.thesis { margin-bottom: 10px; padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 5px; background: #fff; }
.thesis:last-child { margin-bottom: 0; }
.thesis-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; }
.thesis-num { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; background: #eff6ff; color: #2563eb; font-size: 10px; font-weight: 700; flex-shrink: 0; }
.thesis-text { font-size: 11px; font-weight: 600; color: #0f172a; }
.cat { font-size: 8.5px; padding: 2px 8px; border-radius: 10px; font-weight: 600; white-space: nowrap; }
.thesis-desc { margin: 4px 0 6px 28px; font-size: 9.5px; color: #475569; }
.thesis-desc p { margin: 2px 0; }
.thesis-desc ul, .thesis-desc ol { margin: 2px 0 2px 16px; }

/* Proof points */
.pp-section { margin-left: 28px; margin-top: 6px; }
.pp-section-title { font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #94a3b8; margin-bottom: 4px; }
.pp { margin-bottom: 6px; padding: 6px 8px; background: #f8fafc; border-radius: 4px; border-left: 3px solid #e2e8f0; }
.pp:last-child { margin-bottom: 0; }
.pp-header { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.pp-desc { font-size: 10px; color: #1e293b; font-weight: 500; flex: 1; }
.pp-status { font-size: 8px; padding: 2px 8px; border-radius: 10px; font-weight: 700; white-space: nowrap; }
.pp-field { margin-top: 4px; }
.pp-field-label { font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; color: #94a3b8; display: block; margin-bottom: 1px; }
.pp-field-value { font-size: 9.5px; color: #475569; }
.pp-field-value.rich p { margin: 1px 0; }
.pp-field-value.rich ul, .pp-field-value.rich ol { margin: 1px 0 1px 14px; }
.pp-attachments { display: flex; flex-wrap: wrap; gap: 6px; }
.att { font-size: 9px; color: #475569; background: #f1f5f9; padding: 2px 6px; border-radius: 3px; }
.att-size { color: #94a3b8; }

/* Currently testing */
.testing-label { font-size: 11px; color: #1e293b; font-weight: 500; padding: 4px 0; }

/* Reviews */
.review { margin-bottom: 8px; padding: 8px 10px; background: #f8fafc; border-radius: 5px; border-left: 3px solid #3b82f6; }
.review:last-child { margin-bottom: 0; }
.review-date { font-size: 11px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.review-field { font-size: 9.5px; color: #475569; margin: 3px 0; }
.review-field strong { color: #334155; }
.review-field .rich p { margin: 1px 0; }
.commitments { margin: 3px 0 0 16px; }
.commitments li { margin: 2px 0; }

.top-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
.top-row .section { margin-bottom: 0; }
.grid3x2 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px 10px; }
.grid2x2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 10px; }
.footer { font-size: 8px; color: #94a3b8; text-align: right; margin-top: 10px; padding-top: 5px; border-top: 1px solid #f1f5f9; }
</style></head><body>

<div class="header">
  <div>
    <h1>${esc(vbuName)}</h1>
    ${canvas.product_name ? `<div class="header-product">${esc(canvas.product_name)}</div>` : ''}
  </div>
  <div class="header-right">
    <span class="badge-health">${hi.icon} ${health}</span>
    <span class="badge-lane" style="background:${laneColor};">${lane}</span>
  </div>
</div>

<!-- Context + Strategic Focus side by side -->
<div class="top-row">
  <div class="section">
    <div class="sh">Context</div>
    <div class="grid3x2">
      <div class="field"><span class="field-label">Product Name</span><span class="field-value">${plainOrEmpty(canvas.product_name)}</span></div>
      <div class="field"><span class="field-label">Health Indicator</span><span class="field-value" style="color:${hi.color};font-weight:600;">${hi.icon} ${health}</span></div>
      <div class="field"><span class="field-label">Lifecycle Lane</span><span class="field-value"><span class="badge-lane" style="background:${laneColor};font-size:9px;padding:2px 10px;border-radius:10px;">${lane}</span></span></div>
      <div class="field"><span class="field-label">Success Description</span><div class="field-value rich">${richHtml(canvas.success_description)}</div></div>
      <div class="field"><span class="field-label">Future State Intent</span><div class="field-value rich">${richHtml(canvas.future_state_intent)}</div></div>
      <div></div>
    </div>
  </div>
  <div class="section">
    <div class="sh">Strategic Focus</div>
    <div class="grid2x2">
      <div class="field"><span class="field-label">Primary Focus</span><div class="field-value rich">${richHtml(canvas.primary_focus)}</div></div>
      <div class="field"><span class="field-label">Primary Constraint</span><div class="field-value rich">${richHtml(canvas.primary_constraint)}</div></div>
      <div class="field"><span class="field-label">Resist Doing</span><div class="field-value rich">${richHtml(canvas.resist_doing)}</div></div>
      <div class="field"><span class="field-label">Good Discipline</span><div class="field-value rich">${richHtml(canvas.good_discipline)}</div></div>
    </div>
  </div>
</div>

<!-- Investment Theses -->
<div class="section">
  <div class="sh">Investment Theses</div>
  ${thesesHtml}
</div>

<!-- Currently Testing -->
${currentlyTestingHtml}

<!-- Review History -->
<div class="section">
  <div class="sh">Review History</div>
  ${reviewsHtml}
</div>

<div class="footer">Exported ${new Date().toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' })} · Strategy Canvas</div>

</body></html>`;
}

export async function exportCanvasPdf(vbuId: string): Promise<void> {
  const [canvas, vbu] = await Promise.all([getCanvas(vbuId), getVbu(vbuId)]);

  let reviews: Review[] = [];
  try {
    const resp = await apiClient.get(`/canvases/${canvas.id}/reviews`);
    reviews = resp.data.data || [];
  } catch { /* reviews are optional */ }

  let categories: { id: string; name: string; color?: string | null }[] = [];
  try {
    const resp = await apiClient.get('/thesis-categories');
    categories = resp.data.data || [];
  } catch { /* categories are optional */ }

  const html = buildHtml(vbu.name, canvas, reviews, categories);
  const win = window.open('', '_blank');
  if (!win) { alert('Please allow popups to export PDF'); return; }
  win.document.write(html);
  win.document.close();
  setTimeout(() => win.print(), 300);
}
