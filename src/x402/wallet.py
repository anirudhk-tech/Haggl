"""CDP Wallet integration for x402 authorization.

Supports both real Base Sepolia USDC transfers and mock mode for demos.
"""

import os
import logging
import secrets
import hashlib
import pathlib
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv

# Load .env from project root
_project_root = pathlib.Path(__file__).parent.parent.parent
load_dotenv(_project_root / ".env")

from .schemas import WalletInfo

logger = logging.getLogger(__name__)

# Check if web3 is available
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger.warning("web3 not installed. Running in mock mode.")

# Check if CDP SDK is available
try:
    from cdp import CdpClient
    CDP_AVAILABLE = True
except ImportError:
    CDP_AVAILABLE = False
    logger.info("CDP SDK not installed. Using web3 direct mode if available.")


# Base Sepolia configuration
BASE_SEPOLIA_RPC = "https://base-sepolia-rpc.publicnode.com"
BASE_SEPOLIA_CHAIN_ID = 84532

# USDC on Base Sepolia (Circle's testnet USDC)
USDC_CONTRACT_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"

# USDC has 6 decimals
USDC_DECIMALS = 6

# ERC20 Transfer ABI (minimal for transfers)
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]


class CDPWallet:
    """
    CDP Wallet wrapper for x402 authorization.
    
    Supports three modes:
    - Real mode (web3): Uses web3.py with private key for Base Sepolia
    - Real mode (CDP): Uses CDP SDK with Base Sepolia testnet  
    - Mock mode: Simulates wallet for demos without credentials
    """
    
    def __init__(self, mock_mode: bool = False):
        self.network = os.getenv("CDP_NETWORK", "base-sepolia")
        self.escrow_address = os.getenv("ESCROW_WALLET_ADDRESS", "0xMockEscrow...")
        
        # Check for private key (web3 mode)
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")
        
        # Initialize web3 if available
        self._web3: Optional[Web3] = None
        self._account = None
        
        # Determine mode
        if mock_mode:
            self.mock_mode = True
            self.mode = "mock"
        elif self.private_key and WEB3_AVAILABLE:
            self.mock_mode = False
            self.mode = "web3"
            self._init_web3()
        elif CDP_AVAILABLE:
            self.mock_mode = False
            self.mode = "cdp"
            self._init_cdp_client()
        else:
            self.mock_mode = True
            self.mode = "mock"
            logger.warning("No wallet credentials found. Running in mock mode.")
        
        # Mock state
        self._mock_balance_usdc = 10000.0
        self._mock_balance_eth = 1.0
        self._mock_address = f"0x{secrets.token_hex(20)}"
        
        self._cdp_client = None
        self._cdp_account = None
    
    def _init_web3(self):
        """Initialize web3 connection to Base Sepolia."""
        try:
            self._web3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))
            
            if not self._web3.is_connected():
                logger.error("Failed to connect to Base Sepolia RPC")
                self.mock_mode = True
                self.mode = "mock"
                return
            
            # Create account from private key
            self._account = Account.from_key(self.private_key)
            logger.info(f"Web3 wallet initialized: {self._account.address}")
            logger.info(f"Network: Base Sepolia (Chain ID: {BASE_SEPOLIA_CHAIN_ID})")
            
        except Exception as e:
            logger.error(f"Failed to initialize web3: {e}")
            self.mock_mode = True
            self.mode = "mock"
    
    def _init_cdp_client(self):
        """Initialize the CDP client."""
        try:
            if os.path.exists("cdp_api_key.json"):
                self._cdp_client = CdpClient.from_json("cdp_api_key.json")
                logger.info("CDP client initialized from JSON file")
            else:
                api_key_name = os.getenv("CDP_API_KEY_NAME")
                api_key_private = os.getenv("CDP_API_KEY_PRIVATE_KEY")
                
                if api_key_name and api_key_private:
                    self._cdp_client = CdpClient(
                        api_key_name=api_key_name,
                        api_key_private_key=api_key_private
                    )
                    logger.info("CDP client initialized from environment")
                else:
                    logger.warning("No CDP credentials found. Falling back to mock mode.")
                    self.mock_mode = True
                    self.mode = "mock"
        except Exception as e:
            logger.error(f"Failed to initialize CDP client: {e}")
            self.mock_mode = True
            self.mode = "mock"
    
    async def create_account(self) -> WalletInfo:
        """Create or get wallet account."""
        if self.mode == "web3" and self._account:
            balance = await self.get_balance()
            return WalletInfo(
                address=self._account.address,
                network=self.network,
                balance_usdc=balance.get("usdc", 0.0),
                balance_eth=balance.get("eth", 0.0)
            )
        elif self.mode == "cdp" and self._cdp_client:
            self._cdp_account = self._cdp_client.evm.create_account(network=self.network)
            logger.info(f"Created CDP account: {self._cdp_account.address}")
            return WalletInfo(
                address=self._cdp_account.address,
                network=self.network,
                balance_usdc=0.0,
                balance_eth=0.0
            )
        else:
            logger.info(f"[MOCK] Creating wallet on {self.network}")
            return WalletInfo(
                address=self._mock_address,
                network=self.network,
                balance_usdc=self._mock_balance_usdc,
                balance_eth=self._mock_balance_eth
            )
    
    async def get_or_create_account(self) -> WalletInfo:
        """Get existing account or create new one."""
        if self.mode == "web3" and self._account:
            balance = await self.get_balance()
            return WalletInfo(
                address=self._account.address,
                network=self.network,
                balance_usdc=balance.get("usdc", 0.0),
                balance_eth=balance.get("eth", 0.0)
            )
        elif self.mode == "cdp" and self._cdp_account:
            return WalletInfo(
                address=self._cdp_account.address,
                network=self.network,
                balance_usdc=0.0,
                balance_eth=0.0
            )
        
        return await self.create_account()
    
    async def request_testnet_funds(self) -> dict:
        """Request testnet ETH and USDC from faucet."""
        if self.mock_mode:
            logger.info("[MOCK] Requesting testnet funds...")
            return {
                "eth_tx": f"0x{secrets.token_hex(32)}",
                "usdc_tx": f"0x{secrets.token_hex(32)}",
                "status": "mock_funded"
            }
        
        # For web3 mode, user needs to get funds from faucet manually
        if self.mode == "web3":
            return {
                "status": "manual_required",
                "message": "Please use the Base Sepolia faucet: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet",
                "address": self._account.address if self._account else None
            }
        
        # CDP faucet
        if self.mode == "cdp" and self._cdp_account:
            eth_result = self._cdp_client.evm.request_faucet(
                address=self._cdp_account.address,
                network=self.network,
                token="eth"
            )
            usdc_result = self._cdp_client.evm.request_faucet(
                address=self._cdp_account.address,
                network=self.network,
                token="usdc"
            )
            return {
                "eth_tx": eth_result.transaction_hash,
                "usdc_tx": usdc_result.transaction_hash,
                "status": "funded"
            }
        
        return {"status": "error", "message": "No funding method available"}
    
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
                "network": self.network,
                "mode": "mock"
            }
        
        # Real web3 transfer
        if self.mode == "web3" and self._web3 and self._account:
            return await self._web3_transfer(amount_usdc, memo)
        
        # CDP transfer
        if self.mode == "cdp" and self._cdp_client:
            return await self._cdp_transfer(amount_usdc, memo)
        
        return {"success": False, "error": "No transfer method available"}
    
    async def _web3_transfer(self, amount_usdc: float, memo: str) -> dict:
        """Execute real USDC transfer on Base Sepolia using web3."""
        try:
            # Get USDC contract
            usdc_contract = self._web3.eth.contract(
                address=Web3.to_checksum_address(USDC_CONTRACT_ADDRESS),
                abi=ERC20_ABI
            )
            
            # Convert amount to USDC units (6 decimals)
            amount_raw = int(amount_usdc * (10 ** USDC_DECIMALS))
            
            # Check balance first
            balance = usdc_contract.functions.balanceOf(self._account.address).call()
            if balance < amount_raw:
                return {
                    "success": False,
                    "error": f"Insufficient USDC balance: {balance / (10 ** USDC_DECIMALS)} < {amount_usdc}"
                }
            
            # Build transaction
            nonce = self._web3.eth.get_transaction_count(self._account.address)
            
            tx = usdc_contract.functions.transfer(
                Web3.to_checksum_address(self.escrow_address),
                amount_raw
            ).build_transaction({
                'from': self._account.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': self._web3.eth.gas_price,
                'chainId': BASE_SEPOLIA_CHAIN_ID
            })
            
            # Sign and send
            signed_tx = self._web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self._web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"🔗 USDC Transfer sent: {tx_hash_hex}")
            logger.info(f"   Amount: {amount_usdc} USDC")
            logger.info(f"   To: {self.escrow_address}")
            
            # Wait for confirmation
            receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            if receipt['status'] == 1:
                logger.info(f"✅ Transaction confirmed in block {receipt['blockNumber']}")
                return {
                    "success": True,
                    "tx_hash": tx_hash_hex,
                    "explorer_url": f"https://sepolia.basescan.org/tx/{tx_hash_hex}",
                    "amount": amount_usdc,
                    "memo": memo,
                    "escrow_address": self.escrow_address,
                    "network": self.network,
                    "block_number": receipt['blockNumber'],
                    "gas_used": receipt['gasUsed'],
                    "mode": "web3"
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed",
                    "tx_hash": tx_hash_hex
                }
                
        except Exception as e:
            logger.exception(f"Web3 transfer failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _cdp_transfer(self, amount_usdc: float, memo: str) -> dict:
        """Execute transfer using CDP SDK."""
        try:
            account = await self.get_or_create_account()
            
            transfer = self._cdp_client.evm.transfer(
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
                "network": self.network,
                "mode": "cdp"
            }
        except Exception as e:
            logger.exception(f"CDP transfer failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_balance(self) -> dict:
        """Get current wallet balance."""
        if self.mock_mode:
            return {
                "usdc": self._mock_balance_usdc,
                "eth": self._mock_balance_eth,
                "network": self.network,
                "mode": "mock"
            }
        
        if self.mode == "web3" and self._web3 and self._account:
            try:
                # Get ETH balance
                eth_balance = self._web3.eth.get_balance(self._account.address)
                eth_balance_formatted = float(self._web3.from_wei(eth_balance, 'ether'))
                
                # Get USDC balance
                usdc_contract = self._web3.eth.contract(
                    address=Web3.to_checksum_address(USDC_CONTRACT_ADDRESS),
                    abi=ERC20_ABI
                )
                usdc_balance = usdc_contract.functions.balanceOf(self._account.address).call()
                usdc_balance_formatted = usdc_balance / (10 ** USDC_DECIMALS)
                
                return {
                    "usdc": usdc_balance_formatted,
                    "eth": eth_balance_formatted,
                    "network": self.network,
                    "address": self._account.address,
                    "mode": "web3"
                }
            except Exception as e:
                logger.error(f"Failed to get balance: {e}")
                return {
                    "usdc": 0.0,
                    "eth": 0.0,
                    "network": self.network,
                    "error": str(e)
                }
        
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
        # Auto-detect: use real if credentials are available
        mock_mode = not (
            os.getenv("WALLET_PRIVATE_KEY") or
            os.path.exists("cdp_api_key.json") or
            os.getenv("CDP_API_KEY_NAME")
        )
    
    if _wallet is None:
        _wallet = CDPWallet(mock_mode=mock_mode)
    
    return _wallet


def reset_wallet():
    """Reset the global wallet instance."""
    global _wallet
    _wallet = None
