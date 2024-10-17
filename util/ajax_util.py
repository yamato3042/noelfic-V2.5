from flask import request, abort

def checkFormsVal(vals: list):
    #Abort si il manque un élement de la liste
    for i in vals:
        if i not in request.form:
            abort(500)