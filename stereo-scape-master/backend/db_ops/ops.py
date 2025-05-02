from bson import ObjectId
from .__con import db
from datetime import datetime

def saveUsersData (data):
    col = db['user_projects']
    date = datetime.now().isoformat()
    return col.insert_one({**data, 'createdAt': date, 'active': True})

def updateVideoPath(_id, video_path):
    col = db['user_projects']
    fetch = col.find_one({'_id': ObjectId(_id)})
    if fetch:
        _id = ObjectId(_id)
        toUpdate = {**fetch, 'video': video_path}
        up = col.update_one({'_id': _id}, {'$set': toUpdate})
        return up
    return 0
