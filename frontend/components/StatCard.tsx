import Link from 'next/link';

interface StatCardProps {
  label: string;
  value: string | number;
  valueColor?: string;
  subtitle?: string;
  action?: {
  label: string;
    href: string;
  };
  monospace?: boolean;
}

export function StatCard({ label, value, valueColor = 'text-gray-900', subtitle, action, monospace = false }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <p className="text-xs text-gray-500 mb-2">{label}</p>
      <p className={`text-2xl font-bold ${valueColor} ${monospace ? 'font-mono' : ''}`}>
        {value}
      </p>
      {subtitle && (
        <p className="text-xs text-gray-500 mt-2">{subtitle}</p>
      )}
      {action && (
        <Link href={action.href} className="text-xs text-brand hover:text-brand-dark mt-2 inline-block">
          {action.label} →
        </Link>
      )}
    </div>
  );
}

