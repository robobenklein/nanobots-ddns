#!/bin/zsh

# You should set the IPv6 token to some pattern which is easily distinguishable from other temporary addresses or interfaces you want to skip.
# This allows us to choose slightly more stable addresses on a system with multiple IPv6 addresses or interfaces.
#
# For netplan this can be set with ipv6-address-token
# For NetworkManager this can be set like
# nmcli connection modify "Wired DHCP" ipv6.token ::ffff:1:2:3
my_ipv6_token_pattern=${IPV6_TOKEN_PATTERN:-":ffff:"}

# Override with a secure secret!
# Either edit here or via the envvar
my_secret_nanobots_token=${NANOBOTS_SECRET}
if [[ -z "${my_secret_nanobots_token}" ]]; then
  echo "No nanobots DDNS secret set!" >&2
  exit 1
fi

typeset -a local_ips=(
  $(ip --json addr show scope global | jq -cr '.[] | .addr_info[] | select(.family == "inet6") | select(.local | test("'$my_ipv6_token_pattern'")) | .local')
)
ip_list_json=$(ip --json addr show scope global | jq -cr '[(.[] | .addr_info[] | select(.family == "inet6") | select(.local | test("'$my_ipv6_token_pattern'")) | .local)]')

if [[ -z "${local_ips[1]}" ]]; then
  echo "No matching system IPs found!" >&2
  exit 1
fi

echo "Found eligible IPs: ${local_ips}"
echo "Sending from first discovered IP: ${local_ips[1]}"

echo $ip_list_json | \
  curl --interface "${local_ips[1]}" --json @- -6X POST \
  "https://v1.nanobots-api.unhexium.dev/v6m/${my_secret_nanobots_token}" -H 'Content-Type: application/json'
