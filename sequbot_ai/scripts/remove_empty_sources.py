from sequbot_data import models

sa = models.SocialAccount.objects\
        .filter(work_seconds__gt=0)\
        .exclude(status='Stopped by user').order_by('id')
for u in sa:
    if u.instagramsource_set.count() > 200:
        a = InstagramAutomaton(u.id)
        a.authenticate(u.username, u.get_password())
        for fs in u.instagramsource_set.all():
            if fs.instagramtestsubject_set.count() < 1:
                fs.delete()
