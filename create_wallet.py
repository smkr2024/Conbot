import requests, settings

def generate_ltc_address():
    api_key = settings.api_key
    base_url = "https://api.blockcypher.com/v1"
    endpoint = f"{base_url}/ltc/main/addrs"

    try:
        # Sending a POST request to the BlockCypher API
        response = requests.post(endpoint, json={}, params={"token": api_key})
        data = response.json()
        print(data)
        # Extracting the LTC address from the response
        address = data["LSeLe3tKMEh25GEaqf3kGB12BxiU9sntwu"]
        return address

    except requests.exceptions.RequestException as e:
        # Error handling if the request fails
        print("Error:", e)
        return None

# Calling the function to generate an LTC address
ltc_address = generate_ltc_address()

# Checking if the address was successfully generated
if ltc_address is not None:
    print("LTC Address:", ltc_address)
else:
    print("Failed to generate LTC address.")

#cmd에 뜨는 private랑 ltc_address 기록하세요 알아서.    