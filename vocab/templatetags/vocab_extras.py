from django import template
from vocab.models import StudentProfile, StudyUnit, Scheduler, Card, Course

register = template.Library()

@register.filter(name='num_cards_due')
def num_cards_due(profile, studyunit):
	return profile.num_cards_due(studyunit)

#Takes a list of schedulers, and returns the front text of the first
#card that is associated with the first scheduler
@register.filter(name='first_card_front')
def first_card_front(scheduler_list):
	return scheduler_list[0].card.front
