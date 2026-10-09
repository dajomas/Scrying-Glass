"""Readable, change-based event descriptions for encounter feature updates."""
def feature_changes(before, after, delta=None):
    changes=[]
    for field,label in (('hp','HP'),('temp_hp','Temporary HP'),('life_state','Life state'),('death_successes','Death-save successes'),('death_failures','Death-save failures')):
        default=None if field in ('hp','life_state') else 0
        old=before.get(field,default);new=after.get(field,default)
        if old!=new: changes.append(f'{label}: {old} → {new}')
    events=[]
    if changes:
        events.append(('combat-features',abs(delta) if delta is not None else None,'; '.join(changes)))
    old=before.get('concentrating',False);new=after.get('concentrating',False)
    if old!=new:
        events.append(('concentration-started' if new else 'concentration-ended',None,'Concentration started' if new else 'Concentration ended; linked effects removed'))
    return events
