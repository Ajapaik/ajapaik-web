from django.db.models import Sum
from project.home.models import Points, Profile

def calculate_recent_activity_scores():
    thousand_actions_ago = Points.objects.order_by('-created')[1000].created
    recent_actions = Points.objects.filter(created__gt=thousand_actions_ago).values('user_id').annotate(total_points=Sum('points'))
    for each in recent_actions:
        Profile.objects.filter(user_id=each['user_id']).update(score_recent_activity=each['total_points'])