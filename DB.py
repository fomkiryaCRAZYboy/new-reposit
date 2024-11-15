from PIL.ImImagePlugin import number
from pymongo import MongoClient
client = MongoClient('mongodb+srv://kirillfominyh775:kolep20062014@clusterkirill.psoli.mongodb.net/?retryWrites=true&w=majority&appName=ClusterKirill')
db_users = client['autoFLEX']['users']
db_rented_cars = client['autoFLEX']['rented_cars']
db_cars = client['autoFLEX']['cars']