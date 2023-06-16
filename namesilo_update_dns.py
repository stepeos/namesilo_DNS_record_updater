#!/usr/bin/env python3
"""
Module for updating DNS records on NameSilo
"""
"""
MIT License

Copyright (c) 2023 Steve Oswald

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# https://www.namesilo.com/api/dnsUpdateRecord?version=1&type=xml&key=12345&domain=namesilo.com&rrid=1a2b3&rrhost=test&rrvalue=55.55.55.55&rrttl=7207
# 
#     domain: The domain associated with the DNS resource record to modify
#     rrid: The unique ID of the resource record. You can get this value using dnsListRecords.
#     rrhost: The hostname to use (there is no need to include the ".DOMAIN")
#     rrvalue: The value for the resource record
#         A - The IPV4 Address
#         AAAA - The IPV6 Address
#         CNAME - The Target Hostname
#         MX - The Target Hostname
#         TXT - The Text
#     rrdistance: Only used for MX (default is 10 if not provided)
#     rrttl: The TTL for this record (default is 7207 if not provided)

import xml.etree.ElementTree as ET
import argparse
import requests

def get_public_ipv4():
    """
    Get public IPv4 address
    """
    try:
        response = requests.get('https://ipv4.icanhazip.com', timeout=5)
        return response.text.strip()
    except requests.RequestException:
        return None

def get_public_ipv6():
    """
    Get public IPv6 address
    """
    try:
        response = requests.get('https://ipv6.icanhazip.com', timeout=5)
        return response.text.strip()
    except requests.RequestException:
        return None

def get_dns_list_records(domain, api_key):
    """
    Get DNS records from NameSilo
    :param domain: domain name
    :param api_key: NameSilo API key
    :return: dictionary of DNS records
    """
    try:
        response = requests.get(
            f'https://www.namesilo.com/api/dnsListRecords?version=1&type=xml&key={api_key}&domain={domain}',
            timeout=5)
        # create element tree object from response object
        root = ET.fromstring(response.text)
        ET.tostring(root, encoding='utf8').decode('utf8')
        root.findall('reply')
        # get all resource_record elements
        namesilo_domain_records = {}
        for resource_record in root.findall('reply/resource_record'):
            domain_record = {}
            for child in resource_record:
                domain_record[child.tag] = child.text
            namesilo_domain_records[domain_record['record_id']] = domain_record
        return namesilo_domain_records
    except requests.RequestException as exc:
        raise RuntimeError("Error: get_dns_list_records") from exc

def update_dns_records(domain_record, api_key, dns_records):
    """
    Update DNS records
    :param domain_record: dictionary of DNS records
    :param api_key: NameSilo API key
    :param dns_records: dictionary of DNS records
    :return: None
    """
    api_url = "https://www.namesilo.com/api/dnsUpdateRecord"
    params = {
        "version": "1",
        "type": "xml",
        "key": api_key,
        "domain": ".".join(domain_record['host'].split('.')[-2:]),
        "rrid": domain_record['record_id'],
        "rrhost":  ".".join(domain_record['host'].split('.')[:-2]),
        "rrtl": domain_record['ttl']
    }
    rrvalue_dict = {"A": "ipv4", "AAAA": "ipv6"}
    if rrvalue_dict.get(domain_record["type"])is None:
        return
    params["rrvalue"] = dns_records[rrvalue_dict[domain_record["type"]]]
    try:
        response = requests.get(api_url, params=params, timeout=5)
    except requests.RequestException as exc:
        raise RuntimeError("Error: update_dns_records") from exc
    if response.status_code != 200:
        raise RuntimeError("Error: update_dns_records")

def get_dns_records():
    """
    Get public DNS records
    :return: dictionary of DNS records
    """
    dns_getter = {"ipv4": get_public_ipv4, "ipv6": get_public_ipv6}
    public_dns_records = {}
    for proto in ['ipv4', 'ipv6']:
        ip = dns_getter[proto]()
        public_dns_records[proto] = ip
    return public_dns_records

    
if __name__ == "__main__":
    # get public DNS records from icanhazip.com
    dns_records = get_dns_records()

    # NameSilo API credentials
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", help="NameSilo API key", type=str, required=True)
    parser.add_argument("--domain", help="Domain name", type=str, required=True)
    args = parser.parse_args()
    api_key = args.api_key
    domain = args.domain
    domain_records = get_dns_list_records(domain, api_key)
    for record_id, domain_record in domain_records.items():
        # update DNS records for records with type A or AAAA
        update_dns_records(domain_record, api_key, dns_records)
        print(f"DNS record {domain_record['host']} of type "
              f"{domain_record['type']} updated successfully")
