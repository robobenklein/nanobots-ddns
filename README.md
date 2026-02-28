
# DDNS for nanobots

Here's the idea, a DDNS that doesn't require anything more than a single `curl` in a cronjob.

No accounts, no logins, no names. You just make a HTTPS request to the server and it updates a cryptographically-determined subdomain with the new IP address. That way you can just point your own DNS to it as a subdomain and throw one cronjob line into place.

## Status

Just an idea, stil figuring out the right tech to make it happen.

# Goals

The client-side should be dead simple. Nothing more than a HTTP client like curl and perhaps a bash script at most for the advanced use-cases. You should be able to type even 'complex' requests into a machine by hand.

This means the official DDNS protocol doesn't fit the use case. 

## How?

1. You send: `curl -6sSL https://api.nanobots.club/v6/TotallyRandomString` (but `TotallyRandomString` is actually random)
2. The server uses a salted key derivation function on TotallyRandomString to update the subdomain `65446a0d-fcf1-465c-8fd5-f2d99369cdcb.v6.nanobots.club`
3. Your CNAME to `65446a0d-fcf1-465c-8fd5-f2d99369cdcb.v6.nanobots.club` now resolves to the IPv6 address that sent the curl request.

### Implementation

Whatever `TotallyRandomString` you pass to the API is the basis for securing the DDNS updates against malicious actors, so you treat it like a secret key of sorts. Most likely it should be a very long random string of characters.

`/v6` is essentially the "type" of update you want to perform, and determines the subdomain like in v6.nanobots.club

We need different subdomains so we can support different use-cases, for example if a name needs to resolve to multiple A or AAAA addresses, you can't reliably update such without sending additional data in the HTTP request.

Additionally, we want to ensure we separate the types of subdomains based on the security paradigm of each. For example `65446a0d-fcf1-465c-8fd5-f2d99369cdcb.v6.nanobots.club` would be guaranteed to point to the same IP that made the request, while `65446a0d-fcf1-465c-8fd5-f2d99369cdcb.v6m.nanobots.club` might point to a few AAAAs that the server didn't verify belonged to the requester.

For abuse prevention reasons, if you want to update records to more than a single A or AAAA, the requester (your) IP will need to be in that list. This is a DDNS service, not intended for anyone to arbitrarily point at anyone else.

To investigate:

- Minimize storage per subdomain. Each subdomain should be well under 1KiB required serverside:
  - While the HTTP API shouldn't need to persist any data, the authoritative DNS backend server will, so some care needs to be taken in choosing a good implementation.
- Appropriate rate limits
  - perhaps a maximum of 500 unique subdomains per /64 per day? 100 per IPv4?
  - 1 request per 30 seconds per secret key?
- Expiring old names
  - For DDNS usage, if an update request hasn't been received in over a week we can probably delete the record.
  - Whether the machine went down or network is dead, we don't really care since as soon as it comes back online the same DNS name will work again when the next update API call is made.
- Can/should we support non-IP record types like MX or SSHFP?
  - MX might be too ripe for abuse
  - SSHFP could be interesting to get some amount of MITM protection automatically.
    - e.g. API server automatically tries port 22 on the requester IP and sets the SSHFP record based on that

### Endpoints

|Subdomain|Methodology|
|-|-|
|v6, v4|Only hold a single A or AAAA address, based on the requester IP. No additional request data is permitted. Intended to be a 'set and forget' solution to tracking a system's IP as it moves networks, IPs, etc.|
|v6m, v4m|Can hold a few A or AAAA records, but you need to pass the whole list on each request. For abuse prevention reasons, one of the IPs in the list you send must match the one you're requesting from.|
|m|Resolves to both A and AAAA records, so you can have a dual-stack DDNS name. When you make the request with IPv6 it sets all AAAA records, and respectively for IPv4.|

