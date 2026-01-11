'use client';

import { useState, useEffect } from 'react';
import { X, ExternalLink, Loader2, CheckCircle, AlertCircle, Shield } from 'lucide-react';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: string;
  invoiceUrl: string;
  amount: string;
  vendorName: string;
}

type PaymentStep = 'preview' | 'authorizing' | 'paying' | 'complete' | 'error';

export function PaymentModal({ isOpen, onClose, orderId, invoiceUrl, amount, vendorName }: PaymentModalProps) {
  const [step, setStep] = useState<PaymentStep>('preview');
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setStep('preview');
      setAuthToken(null);
      setTxHash(null);
      setError(null);
    }
  }, [isOpen]);

  const handleAuthorize = async () => {
    setStep('authorizing');
    setError(null);

    try {
      // Call x402 authorization endpoint
      const response = await fetch('http://localhost:8082/x402/authorize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invoice_id: orderId.replace('#', ''),
          vendor_name: vendorName,
          vendor_id: 'best-egg-co',
          amount_usd: parseFloat(amount.replace('$', '').replace(',', '')),
          budget_total: 2000.00,
          budget_remaining: 1500.00,
          description: `Invoice payment for ${orderId}`,
        }),
      });

      const data = await response.json();

      if (data.status === 'authorized') {
        setAuthToken(data.auth_token);
        setTxHash(data.tx_hash);
        // Automatically proceed to payment
        handlePayment(data.auth_token, data.tx_hash);
      } else {
        setError(data.error || 'Authorization failed');
        setStep('error');
      }
    } catch (err) {
      setError('Failed to connect to payment server');
      setStep('error');
    }
  };

  const handlePayment = async (token: string, hash: string) => {
    setStep('paying');

    try {
      // Call payment execution endpoint
      const response = await fetch('http://localhost:8082/x402/pay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          auth_token: token,
          invoice_id: orderId.replace('#', ''),
          amount_usd: parseFloat(amount.replace('$', '').replace(',', '')),
          vendor_name: vendorName,
          payment_method: 'mock_ach',
        }),
      });

      const data = await response.json();

      if (data.status === 'succeeded' || data.status === 'processing') {
        setStep('complete');
      } else {
        setError(data.error || 'Payment failed');
        setStep('error');
      }
    } catch (err) {
      setError('Failed to process payment');
      setStep('error');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Shield className="text-brand" size={24} />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Pay Invoice {orderId}</h2>
              <p className="text-sm text-gray-500">{vendorName} · {amount}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex h-[600px]">
          {/* Invoice Preview */}
          <div className="flex-1 border-r border-gray-200">
            <div className="p-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Invoice Preview</span>
              <a
                href={invoiceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-sm text-brand hover:text-brand-dark"
              >
                Open in new tab <ExternalLink size={14} />
              </a>
            </div>
            <iframe
              src={invoiceUrl}
              className="w-full h-[calc(100%-52px)]"
              title="Invoice"
            />
          </div>

          {/* Payment Panel */}
          <div className="w-80 p-6 flex flex-col">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">x402 Payment</h3>

            {/* Steps */}
            <div className="space-y-4 flex-1">
              {/* Step 1: Preview */}
              <div className={`p-4 rounded-lg border ${step === 'preview' ? 'border-brand bg-brand-light' : 'border-gray-200 bg-gray-50'}`}>
                <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${step === 'preview' ? 'bg-brand text-white' : 'bg-gray-300 text-white'}`}>
                    1
                  </div>
                  <span className="font-medium text-gray-900">Review Invoice</span>
                </div>
                {step === 'preview' && (
                  <p className="mt-2 text-sm text-gray-600 ml-9">
                    Review the invoice details on the left before authorizing payment.
                  </p>
                )}
              </div>

              {/* Step 2: Authorize */}
              <div className={`p-4 rounded-lg border ${step === 'authorizing' ? 'border-brand bg-brand-light' : step !== 'preview' ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'}`}>
                <div className="flex items-center gap-3">
                  {step === 'authorizing' ? (
                    <Loader2 className="w-6 h-6 text-brand animate-spin" />
                  ) : step !== 'preview' ? (
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  ) : (
                    <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-gray-300 text-white">2</div>
                  )}
                  <span className="font-medium text-gray-900">x402 Authorization</span>
                </div>
                {step === 'authorizing' && (
                  <p className="mt-2 text-sm text-gray-600 ml-9">
                    Transferring USDC to escrow...
                  </p>
                )}
                {txHash && (
                  <p className="mt-2 text-xs text-gray-500 ml-9 font-mono truncate">
                    TX: {txHash.slice(0, 20)}...
                  </p>
                )}
              </div>

              {/* Step 3: Pay */}
              <div className={`p-4 rounded-lg border ${step === 'paying' ? 'border-brand bg-brand-light' : step === 'complete' ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'}`}>
                <div className="flex items-center gap-3">
                  {step === 'paying' ? (
                    <Loader2 className="w-6 h-6 text-brand animate-spin" />
                  ) : step === 'complete' ? (
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  ) : (
                    <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-gray-300 text-white">3</div>
                  )}
                  <span className="font-medium text-gray-900">Execute Payment</span>
                </div>
                {step === 'paying' && (
                  <p className="mt-2 text-sm text-gray-600 ml-9">
                    Processing ACH transfer...
                  </p>
                )}
              </div>

              {/* Error State */}
              {step === 'error' && (
                <div className="p-4 rounded-lg border border-red-200 bg-red-50">
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-6 h-6 text-red-500" />
                    <span className="font-medium text-red-700">Payment Failed</span>
                  </div>
                  <p className="mt-2 text-sm text-red-600 ml-9">{error}</p>
                </div>
              )}

              {/* Success State */}
              {step === 'complete' && (
                <div className="p-4 rounded-lg border border-green-200 bg-green-50">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                    <span className="font-medium text-green-700">Payment Complete!</span>
                  </div>
                  <p className="mt-2 text-sm text-green-600 ml-9">
                    The invoice has been paid via x402 + ACH.
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="mt-6 space-y-3">
              {step === 'preview' && (
                <button
                  onClick={handleAuthorize}
                  className="w-full bg-brand hover:bg-brand-dark text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Authorize Payment ({amount})
                </button>
              )}
              {step === 'error' && (
                <button
                  onClick={handleAuthorize}
                  className="w-full bg-brand hover:bg-brand-dark text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Retry Payment
                </button>
              )}
              {step === 'complete' && (
                <button
                  onClick={onClose}
                  className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Done
                </button>
              )}
              {(step === 'preview' || step === 'error') && (
                <button
                  onClick={onClose}
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              )}
            </div>

            {/* Security Note */}
            <p className="mt-4 text-xs text-gray-400 text-center">
              🔒 Secured by x402 Protocol · USDC on Base
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
