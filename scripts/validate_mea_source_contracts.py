from __future__ import annotations

import json

from MEA.common.mea_source_contracts import (
    load_reaction_contract,
    load_sentinel_contract,
    validate_reaction_contract,
    validate_sentinel_contract,
)


def main() -> None:
    reactions = load_reaction_contract()
    result = {
        "reaction_contract": validate_reaction_contract(reactions),
        "sentinel_contract": validate_sentinel_contract(
            load_sentinel_contract(), reactions
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
