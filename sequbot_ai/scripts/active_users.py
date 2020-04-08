sa = models.SocialAccount.objects.filter(work_seconds__gt=0).exclude(status__in=['Stopped by user', 'Needs Authentication']).order_by('id')
