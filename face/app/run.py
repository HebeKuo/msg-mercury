from flask import Flask
from flask import request, json
from google.cloud import pubsub_v1
from random import randint
import os, uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

project_id     = os.environ.get('GCP_PROJECT_ID') or 'project id error'
pubsub_topic  = os.environ.get('GCP_PUBSUB_TOPIC') or 'request name error'

@app.route("/api/image", methods=['POST'])
def publish():
    print(request.full_path) 
    
    error_code = ''
    error_message = ''
    result = ''
    object_id = ''
    
    try:
        input = request.json
        object_id = input['object_id']  
        cam_id = input['cam_id'] 
        image = input['image'] 
        created_datetime = input['created_datetime'] 
        print('input >> ', input)
        
        # 運算
        message_id = str(uuid.uuid1())    
        confidence_level = randint(80, 100)
        user_id = object_id    
        message = {"id": message_id,
                   "cam_id": cam_id,
                   "object_id": object_id,
                   "image": image,
                   "created_datetime": created_datetime,
                   "confidence_level": confidence_level,
                   "user_id": user_id}
        print('message >> ', message)
        
        data = json.dumps(message).encode('utf-8')
        print('data >> ', data)
        
        # https://googleapis.github.io/google-cloud-python/latest/pubsub/publisher/api/client.html
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, pubsub_topic)
        print('topic_path >> ', topic_path)
        
        # Data being published to Pub/Sub must be sent " "as a bytestring.
        message_future = publisher.publish(topic_path, data=data)
        print('message_future >> ', message_future)
        
        # Check publish
        if message_future == None:
            error_code = '01'
            error_message = 'message_future is None'
            result = "xx"
        
        #result = "message_future"

    except Exception as e:
        error_code = '99'
        error_message = 'Exception'
        raise e
    
    output = {'error_code': error_code, 'error_message': error_message, 'result': result, 'object_id': object_id}
    return json.dumps(output)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
