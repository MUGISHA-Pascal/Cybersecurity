import os

import shodan


def main() -> int:
    api_key = os.environ.get("SHODAN_API_KEY")
    if not api_key:
        raise SystemExit("Missing SHODAN_API_KEY environment variable.")

    api = shodan.Shodan(api_key)

    results = api.search("apache")
    print(f"result found : {results['total']}")
    for result in results["matches"]:
        print(f"IP: {result['ip_str']}")
        print(result["data"])
        print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
