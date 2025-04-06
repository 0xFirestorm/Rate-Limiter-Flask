import time
import redis
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
redis_client = redis.StrictRedis(host='', port=, db=0, decode_responses=True)

CAPACITY = 3
REFILL_RATE = 1 / 60 # 1 refill per 60 seconds       

def create_tokens(key):
    current_time = time.time()
    bucket_data = redis_client.hgetall(key)

    if not bucket_data:
        tokens = CAPACITY
        last_refill = current_time
    else:
        tokens = float(bucket_data['tokens'])
        last_refill = float(bucket_data['last_refill'])

        new_tokens = (current_time - last_refill) * REFILL_RATE
        tokens = min(CAPACITY, tokens + new_tokens)
        last_refill = current_time

    return tokens, last_refill

def consume_tokens(key):
    tokens, last_refill = create_tokens(key)

    if tokens >= 1:
        tokens -= 1
        redis_client.hmset(key,mapping={'tokens':tokens,'last_refill':last_refill})
        return True
    
    else:
        redis_client.hmset(key,mapping={'tokens':tokens,'last_refill':last_refill})
        return False

@app.route("/requests")
def handle_request():
    ip = request.remote_addr
    
    if consume_tokens(ip):
        return jsonify({'status':'allowed'}),200
    else:
        return jsonify({'status':'limit exceeded'}),429

@app.route("/")
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug='on')