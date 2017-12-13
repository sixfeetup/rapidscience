def past_tense_verb(action):
    action_map = {
        'author_review_edit': 'edited',
        'submit': 'submitted',
        'send_back': 'sent back',
        'admin_edit': 'pulled for revision',
        '_retract_by_author': 'pulled for revision',
        '_retract_by_admin': 'pulled for revision',
        'revise': 'pulled for revision',
    }
    verb = action.lower()
    if verb in action_map:
        return action_map[verb]
    if verb.endswith('e'):
        return verb + 'd'
    return verb + 'ed'
