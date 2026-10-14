"""Require numeric initiative before joining battle, independent of UI controls."""
import inspect


def has_initiative(item):
    return type(item.get('initiative')) is int


def require_initiative(context, items):
    missing = [str(item.get('name') or item.get('id') or 'Combatant')
               for item in items if not has_initiative(item)]
    if missing:
        raise context.HTTPException(400, 'Enter initiative before joining battle: ' + ', '.join(missing))


def validate_initiative_request(context, handler, args, kwargs):
    name = handler.__name__
    if name not in {'update_character', 'update_monster', 'bulk_characters', 'bulk_monsters', 'battle_start'}:
        return
    params = inspect.signature(handler).bind_partial(*args, **kwargs).arguments
    if name == 'battle_start':
        require_initiative(context, [item for kind in ('characters', 'monsters')
                                    for item in context.STATE.get(kind, []) if item.get('active')])
        return
    kind = 'characters' if 'character' in name else 'monsters'
    if name.startswith('bulk_'):
        body = params.get('body')
        if body is not None and body.action == 'join-battle':
            require_initiative(context, context.selected_entities(kind, body.ids))
        return
    update = params.get('update')
    if update is None:
        return
    values = update.model_dump(exclude_unset=True)
    item = next((item for item in context.STATE.get(kind, []) if item['id'] == params.get('ident')), None)
    if item is None:
        return  # Keep the handler's existing not-found response.
    candidate = {**item, **values}
    if candidate.get('active') and (values.get('active') is True or 'initiative' in values):
        require_initiative(context, [candidate])


def validate_initiative_transition(context, original, operation):
    operations = {'update_character', 'update_monster', 'edit_monster',
                  'bulk_characters', 'bulk_monsters', 'create_character', 'create_monster',
                  'import_characters_csv', 'import_monsters_csv', 'import_monster'}
    if operation not in operations:
        return
    invalid = []
    for kind in ('characters', 'monsters'):
        previous = {item['id']: item for item in original.get(kind, [])}
        for item in context.STATE.get(kind, []):
            before = previous.get(item['id'])
            if item.get('active') and not has_initiative(item) and (
                before is None or not before.get('active') or has_initiative(before)
            ):
                invalid.append(item)
    require_initiative(context, invalid)
