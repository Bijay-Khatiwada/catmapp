import datetime
import random, json

def generate_tasks():
    """ Generate random tasks data """
    tasks_list = []
    for i in range(1, 100):
        _name  = f'Task {i}'
        _time = random.randint(1,12)
        _status = random.choice(['Not Started', 'In Progress', 'Completed'])
        _priority = random.choice(['Low', 'Medium', 'High'])
        _label = random.choice(['Breakfast', 'Plants', 'Jog', 'Emails',\
        'Groceries', 'Laundry', 'Clean', 'Call', 'Read', 'Dinner','Meeting',\
            'Exercise', 'Report', 'Lunch', 'Shopping', 'Dishes', 'Workout',\
                'Presentation', 'Dinner','Feed', 'Walk', 'Groom', 'Play', 'Vet'])
        _description = f'This is a description of task {i}'
        _date= (datetime.datetime.now()+ datetime.timedelta(days=random.randint(-30,0))).strftime("%d-%m-%Y")
        tasks_list.append(
            { "name": _name, "time":_time, "label":_label, "description": _description,"date": _date, "status": _status, "priority": _priority}
        )
    return tasks_list

tasks = generate_tasks()
print(tasks)
fout = open("data.json", "w")
fout.write(json.dumps(tasks))
fout.close()

    
