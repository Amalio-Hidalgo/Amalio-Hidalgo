# Snapshot Labs Treasury Analysis

## Issue: API Access Restricted

The Etherscan API returned "Access denied" in this environment. This could be due to:
1. Network restrictions
2. API key rate limiting
3. Firewall/security settings

## Solution: Manual Data Collection

I've created two scripts:

### 1. `treasury_analysis.py` (Automated - requires API access)
- Fetches balances automatically from Etherscan API
- **Currently blocked by API restrictions**

### 2. `treasury_analysis_manual.py` (Manual input - works now!)
- You provide the wallet balances
- Script fetches prices from CoinGecko
- Performs all calculations automatically

## How to Get the Data

### Step 1: Check Each Wallet on Etherscan

Visit these URLs and note down the token balances:

1. **Schnaps Payment**: https://etherscan.io/address/0xe40b2B0d1E236cd5cBd7a37bea88a7FBc9540D41
2. **Snapshot Labs Inc**: https://etherscan.io/address/0x01e80c7a4c000cEd0Bd5E5C0e912C9239E9e0e38
3. **Prototype Foundation**: https://etherscan.io/address/0x431b5a84acc1297Eda88259f300262F1bc3A74d0
4. **Snapshot Labs AG**: https://etherscan.io/address/0x6a87Cf1fA55C27D7706A390bCD48aD36Bab03d70

### Step 2: Update the Script

Edit `treasury_analysis_manual.py` and fill in the `WALLET_HOLDINGS` dictionary (starting around line 28):

```python
WALLET_HOLDINGS = {
    "Schnaps Payment": {
        'ETH': 1.234,      # Replace with actual balance
        'USDC': 50000,     # Replace with actual balance
        'ENS': 100,        # Add any tokens you find
        # etc...
    },
    "Snapshot Labs Inc": {
        'ETH': 0.5,
        'SAFE': 1000,
        # etc...
    },
    # ... repeat for all four wallets
}
```

### Step 3: Run the Analysis

```bash
python3 treasury_analysis_manual.py
```

The script will:
- Fetch current prices from CoinGecko ✓
- Fetch historical prices (Oct 23, 2025) from CoinGecko ✓
- Calculate all metrics ✓
- Generate the formatted paragraph for your proposal ✓
- Create the summary table ✓

## Alternative: Provide Me the Data

If you prefer, you can:

1. Get the current balances from Etherscan for all 4 wallets
2. Paste them here in a comment or message
3. I'll update the script and run the analysis for you

Just provide it in any format like:
```
Wallet 1:
- ETH: 1.5
- USDC: 50000
- ENS: 250

Wallet 2:
- ETH: 0.8
- SAFE: 1200
etc...
```

## Notes

- Wallet addresses were corrected (removed extra trailing zeros)
- CoinGecko API should work without authentication for basic price queries
- The script includes rate limiting to respect API limits
- All calculations (foregone yield, burn rate, concentration) are automated
