#!/usr/bin/env python3

import os
from pymongo import MongoClient

clients = MongoClient().db.clients
clients.find_one_and_update(
    {"cn": os.environ["X509_0_CN"]},
    {"$set": {
        "ip": None
    }},
    upsert=True
)

