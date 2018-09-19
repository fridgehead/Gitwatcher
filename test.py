import logging
import sys
import datetime
import certstream
import Queue
from threading import Thread
import urllib2
import signal


todoQueue = Queue.Queue()
running = True

def print_callback(message, context):
    global todoQueue
    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        if len(all_domains) == 0:
            domain = "NULL"
        else:
            domain = all_domains[0]

        #sys.stdout.write(u"[{}] {} (SAN: {})\n".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'), domain, ", ".join(message['data']['leaf_cert']['all_domains'][1:])))
        sys.stdout.write(".")


        sys.stdout.flush()
        # push the domain to a queue for fun processing
        todoQueue.put(domain)



def queueWorker():
   while running:
      domain = todoQueue.get()
      if domain[0] != "*" :
         try:
            url = "https://" + domain + "/.git/HEAD"
            response = urllib2.urlopen(url, timeout=2)
            html = response.read()
            if "refs/" in html:
	       f = open("out/" + domain + ".txt", "w")
               f.write(html)
               f.close()
               sys.stdout.write("GOTONE! " + domain +  "\n")
               sys.stdout.flush()
         except:
            pass 

      todoQueue.task_done()

def signal_handler(sig, frame):
        print('killing threads')
        running = False
        sys.exit(0)

for i in range (10):
   t = Thread(target=queueWorker)
   t.daemon = True
   t.start()

signal.signal(signal.SIGINT, signal_handler)
logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

certstream.listen_for_events(print_callback)
todoQueue.join()
