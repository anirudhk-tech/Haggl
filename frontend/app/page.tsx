'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const onboardingComplete = localStorage.getItem('onboarding_complete');
    if (onboardingComplete) {
      router.push('/orders');
    } else {
      router.push('/onboarding');
    }
  }, [router]);

  return null;
}

