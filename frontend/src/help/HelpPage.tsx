import React from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../auth/useAuth';

const Section: React.FC<{ title: string; children: React.ReactNode; defaultOpen?: boolean }> = ({ title, children, defaultOpen }) => {
  const [open, setOpen] = React.useState(defaultOpen ?? false);
  return (
    <div className="bg-white border border-neutral-200 rounded-lg">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-neutral-50">
        <span className="text-lg font-semibold text-navy">{title}</span>
        <ChevronDownIcon className={`h-5 w-5 text-neutral-400 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="px-5 pb-5 text-sm text-neutral-700 space-y-3">{children}</div>}
    </div>
  );
};

const HelpPage: React.FC = () => {
  const { user } = useAuth();
  const isGM = user?.role === 'gm';
  return (
  <div className="max-w-3xl mx-auto p-6 space-y-6">
    <h1 className="text-2xl font-semibold text-navy">Help Guide</h1>
    <p className="text-neutral-600">
      Canvas implements a Strategy + Lifecycle methodology: <strong>Intent → Theses → Proof Points → Monthly Review</strong>. 
      It privileges evidence over activity.
    </p>

    <Section title="Key Concepts" defaultOpen>
      <dl className="space-y-4">
        <div><dt className="font-semibold text-navy italic">Canvas</dt>
        <dd className="mt-1">A living strategy document per VBU/product. One canvas per VBU — not a static plan, but a continuously updated view of strategic direction.</dd></div>
        <div><dt className="font-semibold text-navy italic">Thesis</dt>
        <dd className="mt-1">A strategic hypothesis about what must become true over 12–36 months. Phrased as a "new normal", not a project. Max 5 per canvas.</dd></div>
        <div><dt className="font-semibold text-navy italic">Proof Point</dt>
        <dd className="mt-1">An observable signal (not an activity) that a thesis is strengthening or weakening. Think "what would we see in the real world?" — aim for 3–6 month horizon.</dd></div>
        <div><dt className="font-semibold text-navy italic">Lifecycle Lane</dt>
        <dd className="mt-1"><strong>Build</strong> = invest to prove the model. <strong>Sell</strong> = replicate what works. <strong>Milk</strong> = maximise cash, manage risk. <strong>Reframe</strong> = current model exhausted, pivot required.</dd></div>
        <div><dt className="font-semibold text-navy italic">Primary Constraint</dt>
        <dd className="mt-1">The single biggest blocker preventing the next proof point from appearing. Not a risk register — just the one thing that, if removed, would most accelerate progress.</dd></div>
        <div><dt className="font-semibold text-navy italic">Currently Testing</dt>
        <dd className="mt-1">The thesis or proof point that is the primary focus for the next review period.</dd></div>
      </dl>
    </Section>

    <Section title="Editing Your Canvas">
      <ul className="list-disc pl-5 space-y-1">
        <li>All fields autosave — just click, edit, and move on.</li>
        <li>Click any text field to edit it inline. Changes save automatically after you stop typing or leave the field.</li>
        <li>Rich text fields (descriptions, notes) support <strong>bold</strong>, <em>italic</em>, and lists via the toolbar.</li>
        <li>Use "Add Thesis" to create a new strategic thesis (max 5).</li>
        <li>Use "Add Proof Point" under each thesis to add observable signals.</li>
        <li>Set proof point status: Not Started → In Progress → Observed or Stalled.</li>
        <li>Drag theses to reorder them by priority.</li>
        <li>Upload evidence files (images, PDFs) to proof points.</li>
      </ul>
    </Section>

    <Section title="Monthly Reviews">
      <p>Click <strong>Start Review</strong> on your canvas page to begin a monthly review. The wizard walks you through four prompts:</p>
      <ol className="list-decimal pl-5 space-y-1">
        <li><strong>What moved since last month?</strong> — Evidence, not activities.</li>
        <li><strong>What did we learn that changes our beliefs?</strong></li>
        <li><strong>What now threatens the next proof point?</strong></li>
        <li><strong>What are the 1–3 commitments to the next review?</strong></li>
      </ol>
      <p>After completing the review, select which thesis or proof point you're primarily testing next. Review history is visible on your canvas page.</p>
    </Section>

    {!isGM && (
    <Section title="Portfolio Dashboard">
      <p>Admins and Group Leaders see all VBUs at a glance. The dashboard shows:</p>
      <ul className="list-disc pl-5 space-y-1">
        <li>VBU name, lifecycle lane, GM, what's being tested, next review date</li>
        <li>Health indicator — computed from proof point statuses</li>
        <li>Filters by lane, GM, and health status</li>
        <li>Click <strong>View</strong> to open a canvas, or <strong>Export PDF</strong> to download it</li>
      </ul>
      <p>GMs with a single VBU land directly on their canvas page.</p>
    </Section>
    )}

    <Section title="PDF Export">
      <p>Export a canvas to PDF from the dashboard (Export PDF button) or from the canvas page itself. The PDF contains all canvas sections including theses, proof points, and their statuses.</p>
    </Section>

    {!isGM && (
    <Section title="Roles">
      <ul className="list-disc pl-5 space-y-1">
        <li><strong>Admin</strong> — View/edit all VBUs, manage users, portfolio notes.</li>
        <li><strong>Group Leader</strong> — View/edit assigned VBUs, see portfolio dashboard.</li>
        <li><strong>GM</strong> — View/edit own VBU(s) and run monthly reviews.</li>
        <li><strong>Viewer</strong> — Read-only access to all VBUs.</li>
      </ul>
    </Section>
    )}

    <Section title="Password & Account">
      <ul className="list-disc pl-5 space-y-1">
        <li>If you see a password reset screen on login, your admin has set a temporary password. Enter a new password to continue.</li>
        <li>To change your password voluntarily, contact your administrator.</li>
        <li>Forgot your password? Contact your administrator for a reset.</li>
      </ul>
    </Section>
  </div>
  );
};

export default HelpPage;
