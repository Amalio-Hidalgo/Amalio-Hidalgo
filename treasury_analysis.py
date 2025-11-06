#!/usr/bin/env python3
"""
Snapshot Labs Treasury Analysis
Compares holdings from October 23, 2025 to November 6, 2025
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time

# Configuration
ETHERSCAN_API_KEY = "MI756JCZPPW8CBMJWUK3SWU4AMIJ8JQM39"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Wallet addresses (corrected for proper length)
WALLETS = {
    "Schnaps Payment": "0xe40b2B0d1E236cd5cBd7a37bea88a7FBc9540D41",
    "Snapshot Labs Inc": "0x01e80c7a4c000cEd0Bd5E5C0e912C9239E9e0e38",
    "Prototype Foundation": "0x431b5a84acc1297Eda88259f300262F1bc3A74d0",
    "Snapshot Labs AG": "0x6a87Cf1fA55C27D7706A390bCD48aD36Bab03d70"
}

# Token classification
GOVERNANCE_TOKENS = ['ENS', 'SAFE', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'BAL', 'CRV', 'LDO', 'SUSHI']
STABLECOINS = ['USDC', 'USDT', 'DAI', 'USDC.E', 'FRAX', 'LUSD']

# CoinGecko token ID mapping
COINGECKO_IDS = {
    'ETH': 'ethereum',
    'USDC': 'usd-coin',
    'USDT': 'tether',
    'DAI': 'dai',
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
    'WETH': 'weth',
    'stETH': 'staked-ether',
    'wstETH': 'wrapped-steth',
    'rETH': 'rocket-pool-eth'
}

def get_eth_balance(address):
    """Get ETH balance for an address"""
    params = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': ETHERSCAN_API_KEY
    }

    try:
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)

        if response.status_code != 200:
            print(f"  Error: HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return 0.0

        data = response.json()

        if data.get('status') == '1':
            return float(data['result']) / 1e18
        else:
            print(f"  API Error: {data.get('message', 'Unknown error')}")
            return 0.0
    except Exception as e:
        print(f"  Exception fetching ETH balance: {e}")
        return 0.0

def get_erc20_balances(address):
    """Get ERC20 token balances for an address"""
    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'page': 1,
        'offset': 10000,
        'sort': 'desc',
        'apikey': ETHERSCAN_API_KEY
    }

    try:
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)

        if response.status_code != 200:
            print(f"  Error fetching token transactions: HTTP {response.status_code}")
            return {}

        data = response.json()
        token_balances = {}

        if data.get('status') == '1' and data.get('result'):
            # Get unique tokens
            tokens = {}
            for tx in data['result']:
                token_address = tx['contractAddress']
                if token_address not in tokens:
                    tokens[token_address] = {
                        'symbol': tx['tokenSymbol'],
                        'decimals': int(tx['tokenDecimal']) if tx['tokenDecimal'] else 18
                    }

            # Get balance for each token
            for token_address, token_info in tokens.items():
                balance = get_token_balance(address, token_address)
                if balance > 0:
                    token_balances[token_info['symbol']] = {
                        'balance': balance / (10 ** token_info['decimals']),
                        'address': token_address,
                        'decimals': token_info['decimals']
                    }
                time.sleep(0.2)  # Rate limiting

        return token_balances
    except Exception as e:
        print(f"  Exception fetching ERC20 balances: {e}")
        return {}

def get_token_balance(wallet_address, token_address):
    """Get specific ERC20 token balance"""
    params = {
        'module': 'account',
        'action': 'tokenbalance',
        'contractaddress': token_address,
        'address': wallet_address,
        'tag': 'latest',
        'apikey': ETHERSCAN_API_KEY
    }

    try:
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)

        if response.status_code != 200:
            return 0.0

        data = response.json()

        if data.get('status') == '1':
            return float(data['result'])
        return 0.0
    except Exception as e:
        return 0.0

def get_coingecko_price(token_symbol, date=None):
    """Get token price from CoinGecko (current or historical)"""
    token_id = COINGECKO_IDS.get(token_symbol)

    if not token_id:
        print(f"Warning: No CoinGecko ID found for {token_symbol}")
        return 0.0

    try:
        if date:
            # Historical price (format: dd-mm-yyyy)
            date_str = date.strftime('%d-%m-%Y')
            url = f"https://api.coingecko.com/api/v3/coins/{token_id}/history?date={date_str}"
            response = requests.get(url)
            data = response.json()

            if 'market_data' in data and 'current_price' in data['market_data']:
                return data['market_data']['current_price'].get('usd', 0.0)
        else:
            # Current price
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()

            if token_id in data and 'usd' in data[token_id]:
                return data[token_id]['usd']

        time.sleep(1.2)  # CoinGecko rate limiting (free tier)
        return 0.0
    except Exception as e:
        print(f"Error fetching price for {token_symbol}: {e}")
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
    print("FETCHING WALLET BALANCES")
    print("=" * 80)

    # Fetch balances for each wallet
    for wallet_name, wallet_address in WALLETS.items():
        print(f"\n{wallet_name}: {wallet_address}")
        print("-" * 80)

        # Get ETH balance
        eth_balance = get_eth_balance(wallet_address)
        if eth_balance > 0:
            print(f"  ETH: {eth_balance:.4f}")
            all_holdings['ETH'] += eth_balance

        # Get ERC20 balances
        token_balances = get_erc20_balances(wallet_address)
        for symbol, info in token_balances.items():
            balance = info['balance']
            if balance > 0.01:  # Filter dust
                print(f"  {symbol}: {balance:.4f}")
                all_holdings[symbol] += balance

        time.sleep(0.5)

    print("\n" + "=" * 80)
    print("FETCHING PRICES")
    print("=" * 80)

    # Get prices for all tokens
    token_data = {}

    for token, balance in all_holdings.items():
        print(f"\nFetching prices for {token}...")

        current_price = get_coingecko_price(token)
        historical_price = get_coingecko_price(token, oct_23)

        current_value = balance * current_price
        historical_value = balance * historical_price

        token_data[token] = {
            'balance': balance,
            'current_price': current_price,
            'historical_price': historical_price,
            'current_value': current_value,
            'historical_value': historical_value,
            'change_pct': ((current_price - historical_price) / historical_price * 100) if historical_price > 0 else 0
        }

        print(f"  Balance: {balance:.4f}")
        print(f"  Price Oct 23: ${historical_price:.2f}")
        print(f"  Price Nov 6: ${current_price:.2f}")
        print(f"  Current Value: ${current_value:,.2f}")
        print(f"  Change: {token_data[token]['change_pct']:.2f}%")

    # Calculate aggregates
    total_current = sum(t['current_value'] for t in token_data.values())
    total_historical = sum(t['historical_value'] for t in token_data.values())
    total_loss = total_current - total_historical
    loss_pct = (total_loss / total_historical * 100) if total_historical > 0 else 0

    # Categorize holdings
    governance_value = sum(token_data[t]['current_value'] for t in token_data if t in GOVERNANCE_TOKENS)
    stablecoin_value = sum(token_data[t]['current_value'] for t in token_data if t in STABLECOINS)
    eth_value = token_data.get('ETH', {}).get('current_value', 0)
    other_value = total_current - governance_value - stablecoin_value - eth_value

    governance_pct = (governance_value / total_current * 100) if total_current > 0 else 0
    stablecoin_pct = (stablecoin_value / total_current * 100) if total_current > 0 else 0
    eth_pct = (eth_value / total_current * 100) if total_current > 0 else 0

    # Top 3 holdings
    sorted_holdings = sorted(token_data.items(), key=lambda x: x[1]['current_value'], reverse=True)
    top_3_value = sum(t[1]['current_value'] for t in sorted_holdings[:3])
    top_3_pct = (top_3_value / total_current * 100) if total_current > 0 else 0

    # Calculate foregone yield
    avg_treasury = (total_current + total_historical) / 2
    annual_yield_rate = 0.12  # 12% APY
    foregone_yield_14d = avg_treasury * annual_yield_rate * (days_elapsed / 365)
    daily_opportunity_cost = foregone_yield_14d / days_elapsed
    annual_opportunity_cost = avg_treasury * annual_yield_rate

    # Daily burn rate (loss per day)
    daily_burn = abs(total_loss) / days_elapsed

    # Print results
    print("\n" + "=" * 80)
    print("TREASURY SUMMARY")
    print("=" * 80)
    print(f"\nTotal Value Oct 23: ${total_historical:,.2f}")
    print(f"Total Value Nov 6: ${total_current:,.2f}")
    print(f"Change: ${total_loss:,.2f} ({loss_pct:.2f}%)")
    print(f"\nDaily Burn Rate: ${daily_burn:,.2f}/day")

    print("\n" + "-" * 80)
    print("BREAKDOWN BY CATEGORY")
    print("-" * 80)
    print(f"Governance Tokens: ${governance_value:,.2f} ({governance_pct:.1f}%)")
    print(f"Stablecoins: ${stablecoin_value:,.2f} ({stablecoin_pct:.1f}%)")
    print(f"ETH: ${eth_value:,.2f} ({eth_pct:.1f}%)")
    print(f"Other: ${other_value:,.2f} ({(other_value/total_current*100):.1f}%)")

    print("\n" + "-" * 80)
    print("TOP HOLDINGS")
    print("-" * 80)
    for i, (token, data) in enumerate(sorted_holdings[:5], 1):
        pct = (data['current_value'] / total_current * 100) if total_current > 0 else 0
        print(f"{i}. {token}: ${data['current_value']:,.2f} ({pct:.1f}%)")

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

    # Get governance token decline
    gov_historical = sum(token_data[t]['historical_value'] for t in token_data if t in GOVERNANCE_TOKENS)
    gov_decline_pct = ((governance_value - gov_historical) / gov_historical * 100) if gov_historical > 0 else 0

    # Build token list for paragraph
    top_gov_text = ""
    if len(gov_tokens_sorted) >= 2:
        token1, data1 = gov_tokens_sorted[0]
        token2, data2 = gov_tokens_sorted[1]
        top_gov_text = f"{token1}: ${data1['current_value']/1000:.1f}k, {token2}: ${data2['current_value']/1000:.1f}k"

    paragraph = f"""Treasury analysis as of November 6, 2025 across four wallets ({WALLETS['Schnaps Payment'][:6]}...{WALLETS['Schnaps Payment'][-4:]} Schnaps payment, {WALLETS['Snapshot Labs Inc'][:6]}...{WALLETS['Snapshot Labs Inc'][-3:]} Snapshot Labs Inc, {WALLETS['Prototype Foundation'][:6]}...{WALLETS['Prototype Foundation'][-3:]} Prototype Foundation, {WALLETS['Snapshot Labs AG'][:6]}...{WALLETS['Snapshot Labs AG'][-3:]} Snapshot Labs AG) reveals total holdings of ${total_current/1000:.1f}k, with {governance_pct:.1f}% concentrated in governance tokens ({top_gov_text}) that have declined {abs(gov_decline_pct):.1f}% from October 23, 2025 valuations. Over the 14-day period from October 23 to November 6, 2025, treasury declined from ${total_historical/1000:.1f}k to ${total_current/1000:.1f}k—a {abs(loss_pct):.1f}% drawdown (${abs(total_loss):,.0f} unrealized loss) driven by governance token correlation during market declines. Stablecoin holdings of ${stablecoin_value/1000:.1f}k remain idle. Applying actively managed DeFi strategies (12% APY baseline) to the average treasury balance over this period would have generated ${foregone_yield_14d/1000:.1f}k, representing ${daily_opportunity_cost:,.0f}/day in foregone yield—an annualized opportunity cost of ${annual_opportunity_cost/1000:.1f}k/year. The top three holdings represent {top_3_pct:.1f}% of total treasury value, indicating significant concentration risk. Combined with governance token exposure, idle capital, and no active treasury management, this composition creates urgency for sustainable revenue generation independent of volatile holdings."""

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
| **14-Day Change** | ${total_loss:,.2f} ({loss_pct:.2f}%) |
| **Daily Burn Rate** | ${daily_burn:,.2f}/day |
| **Governance Token Exposure** | ${governance_value:,.2f} ({governance_pct:.1f}%) |
| **Governance Token Decline** | {gov_decline_pct:.1f}% |
| **Stablecoin Holdings** | ${stablecoin_value:,.2f} ({stablecoin_pct:.1f}%) |
| **ETH Holdings** | ${eth_value:,.2f} ({eth_pct:.1f}%) |
| **Top 3 Concentration** | {top_3_pct:.1f}% |
| **Average Treasury Balance** | ${avg_treasury:,.2f} |
| **Foregone Yield (14 days @ 12% APY)** | ${foregone_yield_14d:,.2f} |
| **Daily Opportunity Cost** | ${daily_opportunity_cost:,.2f}/day |
| **Annualized Opportunity Cost** | ${annual_opportunity_cost:,.2f}/year |
"""

    print(table)

    # Save detailed holdings
    print("\n" + "=" * 80)
    print("DETAILED HOLDINGS")
    print("=" * 80)

    for token, data in sorted_holdings:
        print(f"\n{token}:")
        print(f"  Balance: {data['balance']:,.4f}")
        print(f"  Current Price: ${data['current_price']:,.2f}")
        print(f"  Current Value: ${data['current_value']:,.2f}")
        print(f"  Historical Price (Oct 23): ${data['historical_price']:,.2f}")
        print(f"  Historical Value: ${data['historical_value']:,.2f}")
        print(f"  Change: {data['change_pct']:.2f}%")

if __name__ == "__main__":
    analyze_treasury()
