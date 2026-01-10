type Status = 'sourcing' | 'negotiating' | 'awaiting-approval' | 'paying' | 'complete' | 'failed';

const statusStyles: Record<Status, string> = {
  'sourcing': 'bg-status-blue-light text-status-blue',
  'negotiating': 'bg-status-orange-light text-status-orange',
  'awaiting-approval': 'bg-status-yellow-light text-status-yellow',
  'paying': 'bg-status-purple-light text-status-purple',
  'complete': 'bg-brand-light text-brand',
  'failed': 'bg-status-rose-light text-status-rose',
};

const statusLabels: Record<Status, string> = {
  'sourcing': 'Sourcing',
  'negotiating': 'Negotiating',
  'awaiting-approval': 'Awaiting Approval',
  'paying': 'Paying',
  'complete': 'Complete',
  'failed': 'Failed',
};

interface StatusBadgeProps {
  status: Status;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status]}`}>
      {statusLabels[status]}
    </span>
  );
}

