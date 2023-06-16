# DNS Record Updater

This Python module provides functionality for updating DNS records on NameSilo. It allows you to programmatically update DNS records associated with a specific domain using the NameSilo API.
Prerequisites

    Python 3.x
    requests library (pip install requests)

## Usage

1. Obtain a NameSilo API key from the NameSilo website.

2. Modify the following command-line arguments in the code:
    --api_key: Your NameSilo API key.
    --domain: The domain name for which you want to update DNS records.

3. Run the code using the following command:

```
python dns_updater.py --api_key <your_api_key> --domain <your_domain>
```
Make sure to replace <your_api_key> and <your_domain> with the appropriate values.

4. The code will retrieve the public IPv4 and IPv6 addresses from https://ipv4.icanhazip.com and https://ipv6.icanhazip.com, respectively.

5. It will then retrieve the current DNS records associated with the specified domain using the NameSilo API.

6. For each DNS record of type A or AAAA, the code will update the record with the new IP address obtained in step 4.

7. The updated DNS records will be printed to the console.

Note: The code relies on the requests library to make HTTP requests. If you don't have it installed, you can install it by running pip install requests before executing the code.
## API Reference

The code uses the NameSilo API to interact with the DNS records. The following NameSilo API endpoints are utilized:

    dnsListRecords: Retrieves the DNS records associated with a specific domain.
    dnsUpdateRecord: Updates a DNS record with a new value.

For more details about the NameSilo API and its usage, refer to the official documentation.
