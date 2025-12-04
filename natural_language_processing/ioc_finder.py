import re
from ioc_finder import find_iocs
import ioc_fanger


IOC_TYPE_DISPLAY_NAMES = {
    "asns": "ASN",
    "attack_mitigations": "Attack Mitigation",
    "attack_tactics": "Attack Tactic",
    "attack_techniques": "Attack Technique",
    "authentihashes": "Authentihash",
    "bitcoin_addresses": "Bitcoin Address",
    "cves": "CVE",
    "domains": "Domain",
    "email_addresses": "Email Address",
    "email_addresses_complete": "Email Address Complete",
    "file_paths": "File Path",
    "google_adsense_publisher_ids": "Google AdSense Publisher ID",
    "google_analytics_tracker_ids": "Google Analytics Tracker ID",
    "imphashes": "Imphash",
    "ipv4_cidrs": "IPv4 CIDR",
    "ipv4s": "IPv4",
    "ipv6s": "IPv6",
    "mac_addresses": "MAC Address",
    "md5s": "MD5",
    "monero_addresses": "Monero Address",
    "registry_key_paths": "Registry Key Path",
    "sha1s": "SHA1",
    "sha256s": "SHA256",
    "sha512s": "SHA512",
    "ssdeeps": "SSDeep",
    "tlp_labels": "TLP Label",
    "urls": "URL",
    "user_agents": "User Agent",
    "xmpp_addresses": "XMPP Address",
}



def extract_ioc(text: str):
    included_ioc_types = [
        "bitcoin_addresses",
        "cves",
        "md5s",
        "sha1s",
        "sha256s",
        "sha512s",
        "ssdeeps",
        "registry_key_paths",
        "ipv4_cidrs",
    ]

    ioc_data = find_iocs(text=text, included_ioc_types=included_ioc_types)
    results = []
    for key, iocs in ioc_data.items():
        for ioc in iocs:
            if match := re.search(ioc, text):
                ioc_start, ioc_end = match.span()
            else:
                ioc_start, ioc_end = "", ""
            results.append({"ioc": ioc_fanger.fang(str(ioc)),
                            "type": IOC_TYPE_DISPLAY_NAMES.get(key, key),
                            "start": ioc_start,
                            "end": ioc_end,
                            "probability": 1.0}
            )
    return results
