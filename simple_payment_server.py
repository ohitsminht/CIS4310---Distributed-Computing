from http.server import SimpleHTTPRequestHandler, HTTPServer
import logging
import urllib.parse
import os.path
import json
import secrets

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """ HTTP request handler """

    def _set_response(self):
        """Sends additional headers and marks the response as ready to send the body."""
        self.send_response(200)
        self.end_headers()

    def do_POST(self):

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))

        #Query and format Python object
        form_query = dict(urllib.parse.parse_qsl(post_data.decode('utf-8')))

        #Load JSON file with mock credit card information
        with open('CCInformation.json') as f:
            info = json.load(f)

        #Convert object strings to int and float
        card_number = int(form_query['ccn'])
        purchase_amount = float(form_query['amount'])

        #Validate form data against JSON file and grant authorization code
        for card_match in info['CardInformation']:
            if card_match['CardNumber'] == card_number and card_match['CreditLimit'] > purchase_amount:
                logging.info("\n\nAuthorization Code:\n%s\n",
                secrets.token_urlsafe())
                data = urllib.parse.urlencode({'Authorization': 'Granted'})
                break
            else:
                data = urllib.parse.urlencode({'Authorization': 'Failed'})

        # Here we'll make up some data to respond with and send it back to the caller.
        data = data.encode('ascii')
        self._set_response()
        self.wfile.write(data)


def run(server_class=HTTPServer, handler_class=HTTPRequestHandler, port=8000):
    
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()