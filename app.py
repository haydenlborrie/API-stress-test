import time
import redis
from flask import Flask

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

def is_prime(n):
  if n <= 3 :
    return n > 1
  elif n % 2 == 0 or n % 3 == 0 :
    return False

  for i in range(5, n, 6) :
    if n % i == 0 or n % (i+2) == 0 :
      return False

  return True

def get_hit_count():
  retries = 5
  while True:
    try:
      return cache.incr('hits')
    except redis.exceptions.ConnectionError as exc:
      if retries == 0:
        raise exc
      retries -= 1
      time.sleep(0.5)


@app.route('/')
def hello():
  count = get_hit_count()
  return 'Hello World! I have been seen {} times.\n'.format(count)

@app.route('/isPrime/<number>')
def test(number):
  is_prime_res = is_prime(int(number))
  if is_prime_res:
    return '{} is prime'.format(number)
  else:
    return '{} is not prime'.format(number)
