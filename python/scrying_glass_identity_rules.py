"""Validate campaign-owned roster IDs against encounter-owned participants."""


def validate_roster_setup_ids(characters, setups, *, label="Campaign roster"):
    """Reject collisions against setups whose encounter data will remain intact."""
    roster_ids = {character["id"] for character in characters}
    for name, state in setups.items():
        participant_ids = {
            item["id"]
            for item in [*state.get("monsters", []), *state.get("lairs", [])]
        }
        conflicting = roster_ids & participant_ids
        if conflicting:
            raise ValueError(
                f"{label} character IDs conflict with setup {name}: "
                + ", ".join(sorted(conflicting)[:5])
            )
