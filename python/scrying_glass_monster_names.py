"""Create valid batch labels without hiding an invalid base monster name."""

MAX_MONSTER_NAME_LENGTH = 100


def numbered_monster_name(name, quantity, number):
    if not isinstance(name, str):
        raise ValueError("Monster name must be text")
    name = name.strip()
    if not 1 <= len(name) <= MAX_MONSTER_NAME_LENGTH:
        raise ValueError("Monster name must contain 1-100 characters after trimming")
    if quantity == 1:
        return name
    # One shared prefix budget keeps all names in the batch consistent.
    prefix_length = MAX_MONSTER_NAME_LENGTH - len(f" - {quantity}")
    return name[:prefix_length] + f" - {number}"
