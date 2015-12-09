from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from homework.models import Class, Thread, MUST_READ, CORE_LESSON_HOMEWORK, Student, Reply


def index(request):
    class_list = Class.objects.all()
    mustRead_list = Thread.objects.filter(thread_type=MUST_READ)
    coreHw_list = Thread.objects.filter(thread_type=CORE_LESSON_HOMEWORK)
    total_last_update_time = datetime.now()
    for i in  mustRead_list:
        if i.last_update_time < total_last_update_time:
            total_last_update_time = i.last_update_time
    for i in  coreHw_list:
        if i.last_update_time < total_last_update_time:
            total_last_update_time = i.last_update_time
    return render(request, 'homework/index.html', {'class_list': class_list,
                                                   'mustRead_list': mustRead_list,
                                                   'coreHw_list': coreHw_list,
                                                   'total_last_update_time': total_last_update_time})

def index2(request):
    return render(request, 'homework/index2.html')

def kclass(request, class_id):
    kclass = get_object_or_404(Class, pk=class_id)
    student_list = kclass.student.all()
    student_with_situation_list = []
    for s in student_list:
        student_with_situation_list.append((s, s.work_completed))
    return render(request, 'homework/class.html', {'class': kclass, 'student_with_situation_list': student_with_situation_list})

def thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    return render(request, 'homework/thread.html', {'thread': thread})

def student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    situation = student.work_completed()
    mustRead_list = Thread.objects.filter(thread_type=MUST_READ)
    mustRead_list_tuple = []
    for mr in mustRead_list:
        if situation.has_key(mr.id):
            mustRead_list_tuple.append((mr, situation[mr.id], len(Reply.objects.filter(author=student, thread=mr))))
        else:
            mustRead_list_tuple.append((mr, 0, 0))
    coreHw_list = Thread.objects.filter(thread_type=CORE_LESSON_HOMEWORK)
    coreHw_list_tuple = []
    for c in coreHw_list:
        if situation.has_key(c.id):
            coreHw_list_tuple.append((c, situation[c.id], len(Reply.objects.filter(author=student, thread=c))))
        else:
            coreHw_list_tuple.append((c, 0, 0))
    return render(request, 'homework/student.html', {'student': student, 'situation': situation,
                                                     'mustRead_list': mustRead_list_tuple, 'coreHw_list': coreHw_list_tuple})

def student_by_bbs_id(request, bbs_id):
    student = get_object_or_404(Student, bbs_id=bbs_id)
    situation = student.work_completed()
    mustRead_list = Thread.objects.filter(thread_type=MUST_READ)
    mustRead_list_tuple = []
    for mr in mustRead_list:
        if situation.has_key(mr.id):
            mustRead_list_tuple.append((mr, situation[mr.id], len(Reply.objects.filter(author=student, thread=mr))))
        else:
            mustRead_list_tuple.append((mr, 0, 0))
    coreHw_list = Thread.objects.filter(thread_type=CORE_LESSON_HOMEWORK)
    coreHw_list_tuple = []
    for c in coreHw_list:
        if situation.has_key(c.id):
            coreHw_list_tuple.append((c, situation[c.id], len(Reply.objects.filter(author=student, thread=c))))
        else:
            coreHw_list_tuple.append((c, 0, 0))
    return render(request, 'homework/student.html', {'student': student, 'situation': situation,
                                                     'mustRead_list': mustRead_list_tuple, 'coreHw_list': coreHw_list_tuple})


def updateAll(request):
    for i in Thread.objects.all():
        print 'update thread ' + str(i.id)
        i.update()
    return HttpResponse("processing all")

def updateAll(request):
    for i in Thread.objects.all():
        print 'update thread ' + str(i.id)
        i.update()
    return HttpResponse("processing all")

def updateAllwithpage(request, start_page, end_page):
    for i in Thread.objects.all():
        print 'update thread ' + str(i.id)
        i.update(start_page=int(start_page), end_page=int(end_page))
    return HttpResponse("processing all")

def update(request, thread_id):
    t = get_object_or_404(Thread, pk=thread_id)
    t.update()
    return HttpResponse("processing one")

def updatewithpage(request, thread_id, start_page, end_page):
    t = get_object_or_404(Thread, pk=thread_id)
    t.update(start_page=int(start_page), end_page=int(end_page))
    return HttpResponse("processing one")