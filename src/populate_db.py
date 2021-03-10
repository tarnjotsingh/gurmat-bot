from pymongo import MongoClient

#Connect to MongoDB
client = MongoClient(port=27017)
db = client.gurmatbot

station_links = {
    "akj": "http://listen.akjradio.org:3232/128k",
    "sdo": "http://107.190.128.24:9302",
    "ds": "http://live16.sgpc.net:8000/;nocache=889869",
    "247": "http://janus.shoutca.st:8195/stream",
    "raag": "https://www.youtube.com/watch?v=tsshX6bWsNg"
}


for s in station_links:
    link = station_links[s]
    key = {'name': s}
    data = {'name': s, 'link': link}

    result = None
    if db.stations.find(key).count() > 0:
        result = db.stations.update_one(key, {'$set': {'link': link}})
        print(f"Updated station \"{s}\" with link {link}")
    else:
        result = db.stations.insert_one(data)
        print(f"Created station \"{s}\" with link {link}")


print(db.stations.find())

print("Finished creating stations databse")
