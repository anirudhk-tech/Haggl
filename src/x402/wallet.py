"""CDP Wallet integration for x402 authorization.

Supports both real CDP wallets (testnet) and mock mode for demos.
"""

import os
import logging
import secrets
import hashlib
from typing import Optional
from datetime import datetime

from .schemas import WalletInfo

logger = logging.getLogger(__name__)

# Check if CDP SDK is available
try:
    from cdp import CdpClient
    CDP_AVAILABLE = True
except ImportError:
    CDP_AVAILABLE = False
    logger.warning("CDP SDK not installed. Running in mock mode.")


class CDPWallet:
    """
    CDP Wallet wrapper for x402 authorization.
    
    Supports two modes:
    - Real mode: Uses actual CDP SDK with Base Sepolia testnet
    - Mock mode: Simulates wallet for demos without CDP credentials
    """
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode or not CDP_AVAILABLE
        self.network = os.getenv("CDP_NETWORK", "base-sepolia")
        self.escrow_address = os.getenv("ESCROW_WALLET_ADDRESS", "0xMockEscrow...")
        
        self._client: Optional[CdpClient] = None
        self._account = None
        self._mock_balance_usdc = 10000.0  # Mock balance for demos
        self._mock_balance_eth = 1.0
        self._mock_address = f"0x{secrets.token_hex(20)}"
        
        if not self.mock_mode:
            self._init_cdp_client()
    
    def _init_cdp_client(self):
        """Initialize the CDP client."""
        try:
            # Try JSON file first
            if os.path.exists("cdp_api_key.json"):
                self._client = CdpClient.from_json("cdp_api_key.json")
                logger.info("CDP client initialized from JSON file")
            else:
                # Fall back to environment variables
                api_key_name = os.getenv("CDP_API_KEY_NAME")
                api_key_private = os.getenv("CDP_API_KEY_PRIVATE_KEY")
                
                if api_key_name and api_key_private:
                    self._client = CdpClient(
                        api_key_name=api_key_name,
                        api_key_private_key=api_key_private
                    )
                    logger.info("CDP client initialized from environment")
                else:
                    logger.warning("No CDP credentials found. Falling back to mock mode.")
                    self.mock_mode = True
        except Exception as e:
            logger.error(f"Failed to initialize CDP client: {e}")
            self.mock_mode = True
    
    async def create_account(self) -> WalletInfo:
        """Create a new wallet account."""
        if self.mock_mode:
            logger.info(f"[MOCK] Creating wallet on {self.network}")
            return WalletInfo(
                address=self._mock_address,
                network=self.network,
                balance_usdc=self._mock_balance_usdc,
                balance_eth=self._mock_balance_eth
            )
        
        # Real CDP wallet creation
        self._account = self._client.evm.create_account(network=self.network)
        logger.info(f"Created CDP account: {self._account.address}")
        
        return WalletInfo(
            address=self._account.address,
            network=self.network,
            balance_usdc=0.0,
            balance_eth=0.0
        )
    
    async def get_or_create_account(self) -> WalletInfo:
        """Get existing account or create new one."""
        if self._account is None and not self.mock_mode:
            return await self.create_account()
        
        return WalletInfo(
            address=self._mock_address if self.mock_mode else self._account.address,
            network=self.network,
            balance_usdc=self._mock_balance_usdc if self.mock_mode else 0.0,
            balance_eth=self._mock_balance_eth if self.mock_mode else 0.0
        )
    
    async def request_testnet_funds(self) -> dict:
        """Request testnet ETH and USDC from faucet."""
        if self.mock_mode:
            logger.info("[MOCK] Requesting testnet funds...")
            return {
                "eth_tx": f"0x{secrets.token_hex(32)}",
                "usdc_tx": f"0x{secrets.token_hex(32)}",
                "status": "mock_funded"
            }
        
        account = await self.get_or_create_account()
        
        # Request ETH
        eth_result = self._client.evm.request_faucet(
            address=account.address,
            network=self.network,
            token="eth"
        )
        
        # Request USDC
        usdc_result = self._client.evm.request_faucet(
            address=account.address,
            network=self.network,
            token="usdc"
        )
        
        return {
            "eth_tx": eth_result.transaction_hash,
            "usdc_tx": usdc_result.transaction_hash,
            "status": "funded"
        }
    
    async def transfer_to_escrow(
        self,
        amount_usdc: float,
        memo: str
    ) -> dict:
        """
        Transfer USDC to escrow wallet for authorization.
        
        This is the core x402 authorization step - proves budget commitment.
        """
        if self.mock_mode:
            # Simulate transfer
            if amount_usdc > self._mock_balance_usdc:
                return {
                    "success": False,
                    "error": f"Insufficient balance: {self._mock_balance_usdc} < {amount_usdc}"
                }
            
            self._mock_balance_usdc -= amount_usdc
            tx_hash = f"0x{hashlib.sha256(f'{memo}{datetime.utcnow().isoformat()}'.encode()).hexdigest()}"
            
            logger.info(f"[MOCK] Transferred ${amount_usdc} USDC to escrow")
            logger.info(f"[MOCK] TX Hash: {tx_hash}")
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "explorer_url": f"https://sepolia.basescan.org/tx/{tx_hash}",
                "amount": amount_usdc,
                "memo": memo,
                "escrow_address": self.escrow_address,
                "network": self.network
            }
        
        # Real CDP transfer
        account = await self.get_or_create_account()
        
        transfer = self._client.evm.transfer(
            from_address=account.address,
            to_address=self.escrow_address,
            amount=str(amount_usdc),
            asset="usdc",
            network=self.network
        )
        
        return {
            "success": True,
            "tx_hash": transfer.transaction_hash,
            "explorer_url": f"https://sepolia.basescan.org/tx/{transfer.transaction_hash}",
            "amount": amount_usdc,
            "memo": memo,
            "escrow_address": self.escrow_address,
            "network": self.network
        }
    
    async def get_balance(self) -> dict:
        """Get current wallet balance."""
        if self.mock_mode:
            return {
                "usdc": self._mock_balance_usdc,
                "eth": self._mock_balance_eth,
                "network": self.network
            }
        
        # Real balance check would go here
        return {
            "usdc": 0.0,
            "eth": 0.0,
            "network": self.network
        }


# Global wallet instance
_wallet: Optional[CDPWallet] = None


def get_wallet(mock_mode: bool = None) -> CDPWallet:
    """Get or create the global wallet instance."""
    global _wallet
    
    if mock_mode is None:
        # Auto-detect: use mock if no CDP credentials
        mock_mode = not (
            os.path.exists("cdp_api_key.json") or
            os.getenv("CDP_API_KEY_NAME")
        )
    
    if _wallet is None:
        _wallet = CDPWallet(mock_mode=mock_mode)
    
    return _wallet
