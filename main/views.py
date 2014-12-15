from django.shortcuts import render
import simplejson
from django.http import HttpResponse
from django.template import RequestContext
from django.db import connection

import subprocess
import os


def run_code(file_name, text):
    if 'import' in text:
        output = ''
        err = 'Using import is not allowed!'
    else:
        f = open(file_name, 'w+')
        f.write(text)
        f.close()
        sub_process = subprocess.Popen(["python", file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            output, err = sub_process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            sub_process.kill()
            output = ""
            err = "TimeoutExpired"
        os.remove(file_name)
    return output, err


def code_edit(request):
    if request.POST:
        text = request.POST['code_text']
        file_name = request.COOKIES['csrftoken'] + '.py'
        output, err = run_code(file_name, text)
        return HttpResponse(simplejson.dumps([output, err]), content_type="application/json")
    else:
        return render(request, 'code.html', context_instance=RequestContext(request))


def run_sql(query, return_answer=False):
    if 'insert' in query.lower() or 'update' in query.lower() or 'delete' in query.lower() or 'drop' in query.lower():
        print('Error!')
    else:
        cursor = connection.cursor()
        try:
            cursor.execute(query)
        except:
            return False
        else:
            if return_answer:
                return cursor.fetchall()