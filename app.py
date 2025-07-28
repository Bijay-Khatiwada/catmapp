""" Flask app for MongoDB CRUD operations """

from datetime import datetime, timedelta
from flask import Flask, jsonify, make_response, request
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

client = MongoClient("mongodb+srv://<user>:<pass>@cluster0.mongodb.net/?retryWrites=true&w=majority&ssl=true&tls=true&tlsAllowInvalidCertificates=true&tlsInsecure=true")


db = client.bizDB # select the database
tasks = db.tasks_data # selects the collection 

@app.route("/task-summary/time", methods=["GET"])
def get_task_summary():
    """ Return all tasks in JSON format"""
    pipeline = [
        {"$group": {"_id": "$label", "total_time": {"$sum": "$time"}}}
    ]
    summary = list(tasks.aggregate(pipeline))
    print(f'Summary: {summary}')
    return make_response(jsonify(summary), 200)

@app.route("/task-summary/status", methods=["GET"])
def get_task_summary_by_status():
    """ Return all tasks in JSON format"""
    pipeline = [
        {"$group": {"_id": "$status", "total_time": {"$sum": "$time"}}}
    ]
    summary = list(tasks.aggregate(pipeline))
    print(f'Summary: {summary}')
    return make_response(jsonify(summary), 200)
@app.route("/task-summary/priority", methods=["GET"])
def get_task_summary_by_priority():
    """ Return all tasks in JSON format"""
    pipeline = [
        {"$group": {"_id": "$priority", "total_time": {"$sum": "$time"}}}
    ]
    summary = list(tasks.aggregate(pipeline))
    print(f'Summary: {summary}')
    return make_response(jsonify(summary), 200)
@app.route("/task-summary/date", methods=["GET"])
def get_task_summary_date():
    """ Return all tasks in JSON format"""
    # Get the start and end dates from the query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # If start_date and end_date are not provided, use the current date and the date 30 days ago
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

    # Construct the pipeline to filter by date range and group by label
    pipeline = [
        {"$match": {"date": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {"_id": "$label", "total_time": {"$sum": "$time"}}}
    ]

    # Execute the pipeline and return the result
    summary = list(tasks.aggregate(pipeline))
    print(f'summary: {summary}')
    return make_response(jsonify(summary), 200)

@app.route("/tasks", methods=["GET"])
def show_all_tasks():
   """ Return all tasks in JSON format"""
   page_num, page_size = 1, 100
   if request.args.get('pn'):
      page_num = int(request.args.get('pn'))

   if request.args.get('ps'):
      page_size = int(request.args.get('ps'))
   
   page_start = (page_size * (page_num - 1))

   data_to_return = []
   cursor = tasks.find().sort('date', -1).skip(page_start).limit(page_size)
   
   for task in cursor:
        # Convert ObjectId to string for JSON serialization
        task['_id'] = str(task['_id'])
        data_to_return.append(task)
   return make_response( jsonify(data_to_return), 200 )  


@app.route("/task/<string:id>", methods=["GET"])
def show_one_task(id):
    """ Return a single task in JSON format"""
    task = tasks.find_one({'_id': ObjectId(id)})
    if task is not None:
        task['_id'] = str(task['_id'])
        print(f'task: {task}')
        return make_response(jsonify([task]), 200)
    else:
        return make_response(jsonify({"error": "Invalid task ID"}), 404)
@app.route('/addTask', methods=['POST'])
def add_data():
    """ Add new task in JSON format"""
    data = request.get_json()  # Assuming data is sent as JSON in the request body
    
    # Extract fields from JSON data
    name = data.get('name')
    label = data.get('label')
    description = data.get('description')
    time= data.get('time')
    date= datetime.strptime(data.get('date'), "%Y-%m-%d").strftime("%d-%m-%Y")
    status= data.get('status')
    priority= data.get('priority')

    # Create a document to insert into MongoDB
    new_record = {
        'name': name,
        'label': label,
        'description': description,
        'time': time,
        'date': date,
        'status': status,
        'priority': priority
    }

    # Insert the document into the MongoDB collection
    result = tasks.insert_one(new_record)

    # Prepare a response
    response = {
        'message': 'Data added successfully',
        'inserted_id': str(result.inserted_id)  # Convert ObjectId to string
    }

    return jsonify(response), 201  # Respond with HTTP status code 201 (Created)


@app.route("/task-del/<string:id>", methods=["DELETE"])
def delete_task(id):
    """ Delete a task in JSON format"""
    result = tasks.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return make_response(jsonify({}), 204)
    else:
        return make_response(jsonify({"error": "Invalid task ID"}), 404)


@app.route("/update-task/<string:id>", methods=["PUT"])
def edit_task(id):
    """ Edit a task in JSON format"""
    required_fields = ["name", "label", "time", "description", "date", "status", "priority"]
    if all(field in request.json for field in required_fields):
        result = tasks.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": request.json["name"],
                "time": request.json["time"],
                "label": request.json["label"],
                "description": request.json["description"],
                "date": request.json["date"],
                "status": request.json["status"],
                "priority": request.json["priority"]
            }}
        )
        if result.matched_count == 1:
            edited_link = "http://localhost:5000/tasks/" + id
            return make_response(jsonify({"url": edited_link}), 200)
        else:
            return make_response(jsonify({"error": "Invalid ID"}), 404)
    else:
        return make_response(jsonify({"error": "Missing form data"}), 400)
    
@app.route("/task-summary/multiline-plot", methods=["GET"])
def get_task_summary_multiline_plot():
    """ Return task data for multiline plot in JSON format"""
    pipeline = [
        {"$sort": {"date": -1}},  # sort tasks by date
        {"$group": {"_id": {"date": "$date", "label": "$label"}, "total_time": {"$sum": "$time"}}}
    ]
    multiline_plot_data = list(tasks.aggregate(pipeline))
    # reformat data for multiline plot
    labels = set(item["_id"]["label"] for item in multiline_plot_data)
    data = {label: [] for label in labels}
    for item in multiline_plot_data:
        data[item["_id"]["label"]].append({"date": item["_id"]["date"], "total_time": item["total_time"]})
    # print(f'Multiline Plot Data: {data}')
    return make_response(jsonify(data), 200)


if __name__ == "__main__":
    app.run(debug=True, port=5000)