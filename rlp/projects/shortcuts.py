from rlp.accounts.models import User


def group_invite_choices(group):
    '''return (ID, name) pairs for any user not already a member'''
    if group:
        current = group.users.all()
        for user in User.objects.all():
            if user in current:
                continue
            yield (user.id, user.get_full_name())
