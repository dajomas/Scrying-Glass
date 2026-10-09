"""Character turn eligibility is independent of positive current HP."""
def is_character(item): return 'monster_species' not in item

def permanently_dead(item):
    if item.get('life_state')=='dead': return True
    failures=item.get('death_failures',0)
    return is_character(item) and type(failures) is int and failures>=3

def can_take_turn(item):
    if not item or not item.get('active') or permanently_dead(item): return False
    return True if is_character(item) else item.get('alive',True)
