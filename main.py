import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# TRC20 contract address on TRON
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

def create_retry_session():
    session = requests.Session()
    retries = Retry(
        total=5, 
        backoff_factor=1, 
        status_forcelist=[500, 502, 503, 504, 429], 
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.timeout = 30 
    return session

def get_balances(wallet_address, session):
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Get TRX balance
            response = session.get(f"https://api.trongrid.io/v1/accounts/{wallet_address}")
            data = response.json()
            
            if not data.get("data") or len(data["data"]) == 0:
                return 0, 0
                
            trx_balance = int(data["data"][0].get("balance", 0)) / 1_000_000
            
            trc20_url = f"https://api.trongrid.io/v1/accounts/{wallet_address}/trc20"
            response = session.get(trc20_url)
            data = response.json()
            usdt_balance = 0
            
            print(f"Checking USDT balance for {wallet_address}")
            
            for token in data.get("data", []):
                if token.get("contract_address") == USDT_CONTRACT:
                    usdt_balance = int(token.get("balance", "0")) / 1_000_000
                    print(f"Found USDT balance: {usdt_balance}")
                    break
            
            return trx_balance, usdt_balance
            
        except Exception as e:
            attempt += 1
            if attempt == max_attempts:
                raise e
            print(f"Attempt {attempt} failed for {wallet_address}: {str(e)}. Retrying...")


with open("adress.txt", "r") as f:
    addresses = [addr.strip() for addr in f.readlines()]

session = create_retry_session()

total_trx = 0
total_usdt = 0

for address in addresses:
    try:
        trx_balance, usdt_balance = get_balances(address, session)
        total_trx += trx_balance
        total_usdt += usdt_balance
        
        result = f"{address} trx_balance {trx_balance} Usdt_balance {usdt_balance}\n"
        with open("trx_balance.txt", "a") as f:
            f.write(result)
        print(result.strip())  
    except Exception as e:
        print(f"Error checking address {address} after all retries: {str(e)}")
        with open("trx_balance.txt", "a") as f:
            f.write(f"{address} trx_balance 0 Usdt_balance 0\n")

total_result = f"\nTotal Balances:\nTotal TRX: {total_trx}\nTotal USDT: {total_usdt}"
print(total_result)


with open("trx_balance.txt", "a") as f:
    f.write("\n" + "-" * 50 + "\n")
    f.write(f"Total TRX Balance: {total_trx}\n")
    f.write(f"Total USDT Balance: {total_usdt}\n")
    f.write("-" * 50 + "\n")
