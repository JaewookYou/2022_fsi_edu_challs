#-*-coding: utf-8-*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.remote_connection import LOGGER
import flask
import traceback, os, time

app = flask.Flask(__name__)
app.secret_key = os.urandom(16)
app.config['MAX_CONTENT_LENGTH'] = 80 * 1024 * 1024

def interceptor(request):
	pass

class Crawler:
	def __init__(self):
		caps = DesiredCapabilities.CHROME
		caps['goog:loggingPrefs'] = {'performance': 'ALL'}

		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option("useAutomationExtension", False)

		self.driver = webdriver.Chrome("/app/bot/chromedriver", options=options, desired_capabilities=caps)
		self.driver.request_interceptor = interceptor
		self.driver.implicitly_wait(3)
		self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
		self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'navigator.'})
		self.driver.set_page_load_timeout(3)

	def req(self, url):
		try:
			print(f"[+] doing crawler req {url}")
			self.driver.get(url)
		except:
			print(f"[x] crawler driver req fail - {url}")
			print(traceback.format_exc())
			return False

		return self.driver

def doCrawl(url):
	crawler = Crawler()
	driver = crawler.driver
	adminid = "admin"
	adminpw = "th1s_1s_adm111n_p4ssw0rd"
	try:
		crawler.req('http://172.22.0.4:9090/login')

		driver.find_element(By.ID,"userid").send_keys(adminid)
		driver.find_element(By.ID,"userpw").send_keys(adminpw)
		driver.find_element(By.ID,"submit-login").click()
		
		time.sleep(2)

		if crawler.req(url):
			uploadFile = driver.find_element(By.ID,"uploadFile")
			if uploadFile:
				uploadFile.click()
			time.sleep(10)
		
		driver.quit()
	except:
		driver.quit()
		print(f"[x] error...")
		print(traceback.format_exc())

@app.route("/run", methods=["GET"])
def run():
	url = flask.request.args['url']
	print(f"[+] bot run {url}")
	doCrawl(url)
	return "<script>history.go(-1);</script>"
		

if __name__ == "__main__":
	try:
		app.run(host="0.0.0.0", port=9000, debug=True)
	except Exception as ex:
		logging.info(str(ex))
		pass