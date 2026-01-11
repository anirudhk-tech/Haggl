'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { ChevronDown } from 'lucide-react';

const navLinks = [
  { href: '/new-order', label: 'New Order' },
  { href: '/orders', label: 'Orders' },
  { href: '/products', label: 'Products' },
  { href: '/suppliers', label: 'Suppliers' },
  { href: '/wallet', label: 'Wallet' },
  { href: '/inbox', label: 'Inbox' },
];

export function NavBar() {
  const pathname = usePathname();
  
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 h-16">
      <div className="max-w-[1440px] mx-auto px-16 h-full flex items-center justify-between">
        {/* Logo */}
        <Link href="/orders" className="flex items-center">
          <Image 
            src="/logo.png" 
            alt="Haggl" 
            width={180} 
            height={56} 
            className="h-14 w-auto"
            priority
          />
        </Link>
        
        {/* Nav Links */}
        <div className="flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors ${
                pathname === link.href
                  ? 'text-brand border-b-2 border-brand pb-1'
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
        
        {/* User Avatar */}
        <div className="relative group">
          <button className="w-8 h-8 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors" />
          <div className="absolute right-0 top-10 hidden group-hover:block bg-white rounded-lg shadow-lg border border-gray-200 py-2 min-w-[150px]">
            <Link href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
              Profile
            </Link>
            <Link href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
              Settings
            </Link>
            <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

