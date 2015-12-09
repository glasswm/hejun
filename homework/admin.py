from django.contrib import admin
from models import Class, Student, Thread, Reply

class StudentInline(admin.StackedInline):
    model = Student
    extra = 3

class ClassAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['title']}),
    ]
    inlines = [StudentInline]

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['bbs_id']

class ReplyAdmin(admin.ModelAdmin):
    search_fields = ['reply_id']

# Register your models here.
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Thread)
admin.site.register(Reply, ReplyAdmin)