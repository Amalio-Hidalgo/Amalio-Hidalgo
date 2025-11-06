#!/usr/bin/env python3
"""
Snapshot Labs Treasury Analysis - Manual Input Version
Compares holdings from October 23, 2025 to November 6, 2025

TO USE:
1. Go to Etherscan.io and check each wallet's current token balances
2. Update the WALLET_HOLDINGS dictionary below with actual balances
3. Run the script to get prices and perform analysis
"""

import requests
import json
from datetime import datetime
from collections import defaultdict
import time

# WALLET ADDRESSES (corrected)
WALLETS = {
    "Schnaps Payment": "0xe40b2B0d1E236cd5cBd7a37bea88a7FBc9540D41",  # Removed extra 0
    "Snapshot Labs Inc": "0x01e80c7a4c000cEd0Bd5E5C0e912C9239E9e0e38",
    "Prototype Foundation": "0x431b5a84acc1297Eda88259f300262F1bc3A74d0",  # Removed extra 0
    "Snapshot Labs AG": "0x6a87Cf1fA55C27D7706A390bCD48aD36Bab03d70"
}

# MANUAL INPUT: Update these with actual current balances from Etherscan
# Format: {'TOKEN_SYMBOL': balance_amount}
WALLET_HOLDINGS = {
    "Schnaps Payment": {
        'ETH': 0.0,
        'USDC': 0.0,
        # Add more tokens as needed
    },
    "Snapshot Labs Inc": {
        'ETH': 0.0,
        'USDC': 0.0,
        # Add more tokens as needed
    },
    "Prototype Foundation": {
        'ETH': 0.0,
        'USDC': 0.0,
        # Add more tokens as needed
    },
    "Snapshot Labs AG": {
        'ETH': 0.0,
        'USDC': 0.0,
        # Add more tokens as needed
    }
}

# Token classification
GOVERNANCE_TOKENS = ['ENS', 'SAFE', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'BAL', 'CRV', 'LDO', 'SUSHI', 'GNO']
STABLECOINS = ['USDC', 'USDT', 'DAI', 'USDC.E', 'FRAX', 'LUSD', 'USDS']

# CoinGecko token ID mapping
COINGECKO_IDS = {
    'ETH': 'ethereum',
    'WETH': 'weth',
    'USDC': 'usd-coin',
    'USDT': 'tether',
    'DAI': 'dai',
    'USDS': 'usds',
    'ENS': 'ethereum-name-service',
    'SAFE': 'safe',
    'UNI': 'uniswap',
    'AAVE': 'aave',
    'COMP': 'compound-governance-token',
    'MKR': 'maker',
    'SNX': 'havven',
    'BAL': 'balancer',
    'CRV': 'curve-dao-token',
    'LDO': 'lido-dao',
    'SUSHI': 'sushi',
    'GNO': 'gnosis',
    'stETH': 'staked-ether',
    'wstETH': 'wrapped-steth',
    'rETH': 'rocket-pool-eth',
    'ARB': 'arbitrum',
    'OP': 'optimism'
}

def get_coingecko_price(token_symbol, date=None):
    """Get token price from CoinGecko (current or historical)"""
    token_id = COINGECKO_IDS.get(token_symbol)

    if not token_id:
        print(f"Warning: No CoinGecko ID found for {token_symbol}, skipping...")
        return 0.0

    try:
        if date:
            # Historical price (format: dd-mm-yyyy)
            date_str = date.strftime('%d-%m-%Y')
            url = f"https://api.coingecko.com/api/v3/coins/{token_id}/history?date={date_str}"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if 'market_data' in data and 'current_price' in data['market_data']:
                    price = data['market_data']['current_price'].get('usd', 0.0)
                    print(f"  ✓ {token_symbol} price on {date_str}: ${price:.2f}")
                    return price
            else:
                print(f"  ✗ Failed to fetch {token_symbol} historical price: HTTP {response.status_code}")
                return 0.0
        else:
            # Current price
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if token_id in data and 'usd' in data[token_id]:
                    price = data[token_id]['usd']
                    print(f"  ✓ {token_symbol} current price: ${price:.2f}")
                    return price
            else:
                print(f"  ✗ Failed to fetch {token_symbol} current price: HTTP {response.status_code}")
                return 0.0

        time.sleep(1.5)  # CoinGecko rate limiting
        return 0.0
    except Exception as e:
        print(f"  ✗ Error fetching price for {token_symbol}: {e}")
        return 0.0

def analyze_treasury():
    """Main analysis function"""
    print("=" * 80)
    print("SNAPSHOT LABS TREASURY ANALYSIS")
    print("=" * 80)
    print(f"Analysis Period: October 23, 2025 to November 6, 2025 (14 days)")
    print("=" * 80)

    # Dates
    oct_23 = datetime(2025, 10, 23)
    nov_6 = datetime(2025, 11, 6)
    days_elapsed = 14

    # Aggregate holdings
    all_holdings = defaultdict(float)

    print("\n" + "=" * 80)
    print("AGGREGATING WALLET HOLDINGS")
    print("=" * 80)

    for wallet_name, holdings in WALLET_HOLDINGS.items():
        print(f"\n{wallet_name}:")
        for token, balance in holdings.items():
            if balance > 0:
                print(f"  {token}: {balance:,.4f}")
                all_holdings[token] += balance

    print("\n" + "=" * 80)
    print("TOTAL AGGREGATED HOLDINGS")
    print("=" * 80)
    for token, balance in sorted(all_holdings.items()):
        if balance > 0:
            print(f"  {token}: {balance:,.4f}")

    if not all_holdings or all(v == 0 for v in all_holdings.values()):
        print("\n⚠️  WARNING: No holdings data provided!")
        print("Please update the WALLET_HOLDINGS dictionary in the script with actual balances.")
        return

    print("\n" + "=" * 80)
    print("FETCHING CURRENT PRICES FROM COINGECKO")
    print("=" * 80)

    token_data = {}

    for token, balance in sorted(all_holdings.items()):
        if balance > 0:
            print(f"\n{token}:")
            current_price = get_coingecko_price(token)
            time.sleep(1.2)  # Rate limiting

            token_data[token] = {
                'balance': balance,
                'current_price': current_price,
                'current_value': balance * current_price
            }

    print("\n" + "=" * 80)
    print("FETCHING HISTORICAL PRICES (October 23, 2025)")
    print("=" * 80)

    for token in sorted(token_data.keys()):
        print(f"\n{token}:")
        historical_price = get_coingecko_price(token, oct_23)
        time.sleep(1.2)  # Rate limiting

        token_data[token]['historical_price'] = historical_price
        token_data[token]['historical_value'] = token_data[token]['balance'] * historical_price

        if historical_price > 0:
            change_pct = ((token_data[token]['current_price'] - historical_price) / historical_price * 100)
            token_data[token]['change_pct'] = change_pct
        else:
            token_data[token]['change_pct'] = 0.0

    # Calculate aggregates
    total_current = sum(t['current_value'] for t in token_data.values())
    total_historical = sum(t['historical_value'] for t in token_data.values())
    total_loss = total_current - total_historical
    loss_pct = (total_loss / total_historical * 100) if total_historical > 0 else 0

    # Categorize holdings
    governance_value = sum(token_data[t]['current_value'] for t in token_data if t in GOVERNANCE_TOKENS)
    governance_historical = sum(token_data[t]['historical_value'] for t in token_data if t in GOVERNANCE_TOKENS)
    stablecoin_value = sum(token_data[t]['current_value'] for t in token_data if t in STABLECOINS)
    eth_value = token_data.get('ETH', {}).get('current_value', 0) + token_data.get('WETH', {}).get('current_value', 0)
    other_value = total_current - governance_value - stablecoin_value - eth_value

    governance_pct = (governance_value / total_current * 100) if total_current > 0 else 0
    stablecoin_pct = (stablecoin_value / total_current * 100) if total_current > 0 else 0
    eth_pct = (eth_value / total_current * 100) if total_current > 0 else 0
    other_pct = (other_value / total_current * 100) if total_current > 0 else 0

    # Governance token decline
    gov_decline_pct = ((governance_value - governance_historical) / governance_historical * 100) if governance_historical > 0 else 0

    # Top holdings
    sorted_holdings = sorted(token_data.items(), key=lambda x: x[1]['current_value'], reverse=True)
    top_3_value = sum(t[1]['current_value'] for t in sorted_holdings[:3])
    top_3_pct = (top_3_value / total_current * 100) if total_current > 0 else 0

    # Calculate foregone yield
    avg_treasury = (total_current + total_historical) / 2
    annual_yield_rate = 0.12  # 12% APY
    foregone_yield_14d = avg_treasury * annual_yield_rate * (days_elapsed / 365)
    daily_opportunity_cost = foregone_yield_14d / days_elapsed
    annual_opportunity_cost = avg_treasury * annual_yield_rate

    # Daily burn rate
    daily_burn = abs(total_loss) / days_elapsed

    # Print summary
    print("\n" + "=" * 80)
    print("TREASURY SUMMARY")
    print("=" * 80)
    print(f"\nTotal Value Oct 23: ${total_historical:,.2f}")
    print(f"Total Value Nov 6: ${total_current:,.2f}")
    print(f"Change: ${total_loss:,.2f} ({loss_pct:+.2f}%)")
    print(f"\nDaily Burn Rate: ${daily_burn:,.2f}/day")

    print("\n" + "-" * 80)
    print("BREAKDOWN BY CATEGORY")
    print("-" * 80)
    print(f"Governance Tokens: ${governance_value:,.2f} ({governance_pct:.1f}%)")
    print(f"  - Change from Oct 23: {gov_decline_pct:+.1f}%")
    print(f"Stablecoins: ${stablecoin_value:,.2f} ({stablecoin_pct:.1f}%)")
    print(f"ETH/WETH: ${eth_value:,.2f} ({eth_pct:.1f}%)")
    print(f"Other: ${other_value:,.2f} ({other_pct:.1f}%)")

    print("\n" + "-" * 80)
    print("TOP 5 HOLDINGS")
    print("-" * 80)
    for i, (token, data) in enumerate(sorted_holdings[:5], 1):
        pct = (data['current_value'] / total_current * 100) if total_current > 0 else 0
        print(f"{i}. {token}: ${data['current_value']:,.2f} ({pct:.1f}%) | Change: {data['change_pct']:+.1f}%")

    print(f"\nTop 3 Concentration: {top_3_pct:.1f}%")

    print("\n" + "-" * 80)
    print("OPPORTUNITY COST ANALYSIS")
    print("-" * 80)
    print(f"Average Treasury Balance: ${avg_treasury:,.2f}")
    print(f"Foregone Yield (14 days @ 12% APY): ${foregone_yield_14d:,.2f}")
    print(f"Daily Opportunity Cost: ${daily_opportunity_cost:,.2f}/day")
    print(f"Annualized Opportunity Cost: ${annual_opportunity_cost:,.2f}/year")

    # Generate formatted paragraph
    print("\n" + "=" * 80)
    print("FORMATTED OUTPUT FOR SECTION 3.2.A")
    print("=" * 80)

    # Get top governance tokens
    gov_tokens = [(t, token_data[t]) for t in token_data if t in GOVERNANCE_TOKENS]
    gov_tokens_sorted = sorted(gov_tokens, key=lambda x: x[1]['current_value'], reverse=True)

    # Build token list for paragraph
    top_gov_text = ""
    if len(gov_tokens_sorted) >= 2:
        token1, data1 = gov_tokens_sorted[0]
        token2, data2 = gov_tokens_sorted[1]
        top_gov_text = f"{token1}: ${data1['current_value']/1000:.1f}k, {token2}: ${data2['current_value']/1000:.1f}k"
    elif len(gov_tokens_sorted) == 1:
        token1, data1 = gov_tokens_sorted[0]
        top_gov_text = f"{token1}: ${data1['current_value']/1000:.1f}k"

    # Format wallet addresses for paragraph
    w1 = WALLETS['Schnaps Payment']
    w2 = WALLETS['Snapshot Labs Inc']
    w3 = WALLETS['Prototype Foundation']
    w4 = WALLETS['Snapshot Labs AG']

    paragraph = f"""Treasury analysis as of November 6, 2025 across four wallets ({w1[:6]}...{w1[-4:]} Schnaps payment, {w2[:6]}...{w2[-3:]} Snapshot Labs Inc, {w3[:6]}...{w3[-3:]} Prototype Foundation, {w4[:6]}...{w4[-3:]} Snapshot Labs AG) reveals total holdings of ${total_current/1000:.1f}k, with {governance_pct:.1f}% concentrated in governance tokens ({top_gov_text}) that have declined {abs(gov_decline_pct):.1f}% from October 23, 2025 valuations. Over the 14-day period from October 23 to November 6, 2025, treasury declined from ${total_historical/1000:.1f}k to ${total_current/1000:.1f}k—a {abs(loss_pct):.1f}% drawdown (${abs(total_loss):,.0f} unrealized loss) driven by governance token correlation during market declines. Stablecoin holdings of ${stablecoin_value/1000:.1f}k remain idle. Applying actively managed DeFi strategies (12% APY baseline) to the average treasury balance over this period would have generated ${foregone_yield_14d/1000:.1f}k, representing ${daily_opportunity_cost:,.0f}/day in foregone yield—an annualized opportunity cost of ${annual_opportunity_cost/1000:.1f}k/year. The top three holdings represent {top_3_pct:.1f}% of total treasury value, indicating significant concentration risk. Combined with governance token exposure, idle capital, and no active treasury management, this composition creates urgency for sustainable revenue generation independent of volatile holdings."""

    print("\n" + paragraph)

    # Generate summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)

    table = f"""
| Metric | Value |
|--------|-------|
| **Treasury Value (Oct 23, 2025)** | ${total_historical:,.2f} |
| **Treasury Value (Nov 6, 2025)** | ${total_current:,.2f} |
| **14-Day Change** | ${total_loss:,.2f} ({loss_pct:+.2f}%) |
| **Daily Burn Rate** | ${daily_burn:,.2f}/day |
| **Governance Token Exposure** | ${governance_value:,.2f} ({governance_pct:.1f}%) |
| **Governance Token Decline** | {gov_decline_pct:+.1f}% |
| **Stablecoin Holdings** | ${stablecoin_value:,.2f} ({stablecoin_pct:.1f}%) |
| **ETH Holdings** | ${eth_value:,.2f} ({eth_pct:.1f}%) |
| **Top 3 Concentration** | {top_3_pct:.1f}% |
| **Average Treasury Balance** | ${avg_treasury:,.2f} |
| **Foregone Yield (14 days @ 12% APY)** | ${foregone_yield_14d:,.2f} |
| **Daily Opportunity Cost** | ${daily_opportunity_cost:,.2f}/day |
| **Annualized Opportunity Cost** | ${annual_opportunity_cost:,.2f}/year |
"""

    print(table)

    # Detailed breakdown
    print("\n" + "=" * 80)
    print("DETAILED TOKEN BREAKDOWN")
    print("=" * 80)
    print(f"\n{'Token':<10} {'Balance':>15} {'Current $':>15} {'Oct 23 $':>15} {'Change %':>12}")
    print("-" * 80)

    for token, data in sorted_holdings:
        print(f"{token:<10} {data['balance']:>15,.4f} ${data['current_value']:>14,.2f} ${data['historical_value']:>14,.2f} {data['change_pct']:>11.2f}%")

if __name__ == "__main__":
    print("\n⚠️  MANUAL INPUT VERSION")
    print("Please update WALLET_HOLDINGS dictionary with actual balances from Etherscan")
    print("Then run this script to perform the full analysis with live prices.\n")

    analyze_treasury()
