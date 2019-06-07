
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

  i = 5	
  while (i * i) <= n :
    if n % i == 0 or n % (i+2) == 0 :
      return False
    i += 6

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

@app.route('/isPrime/<number>')
def primality_test(number):
  is_prime_res = is_prime(int(number))
  if is_prime_res:
    retries = 5
    while True:
      try:
        cache.lpush('primes', number)
        return '{} is prime'.format(number)
      except redis.exceptions.ConnectionError as exc:
        if retries == 0:
          raise exc
        retries -= 1
        time.sleep(0.5)
  else:
    return '{} is not prime'.format(number)


@app.route('/primesStored')
def prime_numbers():
  output_string = 'Prime Numbers: <br>'
  prime_number_list = cache.lrange('primes', 0, -1)

  for number in prime_number_list:
    output_string += number.decode('utf-8') + '<br>\n'

  return output_string

@app.route('/test')
def test():
  for i in range(-13, 20):
    primality_test(i)

  return prime_numbers()

@app.route('/clearCache')
def clear_cache():
  cache.flushall()

  return 'cache cleared'
