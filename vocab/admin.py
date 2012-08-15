from vocab.models import StudentProfile, Course, StudyUnit, Card
from django.contrib import admin

class CardInline(admin.TabularInline):
	model = Card
	extra = 2

class CardAdmin(admin.ModelAdmin):
#	fieldsets = [
#		(None, {'fields': ['name']}),
#		('Card List', {'fields': ['cards'], 'classes': ['collapse']})
#	]
	list_display = ('front', 'back', 'studyunit')

class StudyUnitAdmin(admin.ModelAdmin):
	list_display = ('name', 'num_cards')
	inlines = [CardInline]

admin.site.register(StudentProfile)
admin.site.register(Course)
admin.site.register(Card, CardAdmin)
admin.site.register(StudyUnit, StudyUnitAdmin)
