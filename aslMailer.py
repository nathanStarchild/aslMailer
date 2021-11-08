from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import time
import logging
import logging.handlers
import sys


logging.basicConfig()
fac = 'local4'
hdl = logging.handlers.SysLogHandler(address="/dev/log", facility=fac)
logger = logging.getLogger(__name__)
logger.addHandler(hdl)
logger.setLevel(logging.INFO)

searches = {
    "twoDays": [
        # {'searchVal': "55563", "templateVal": "88376", "desc": "Accepted - Session 2 days reminder"},#on hold
    ],
    "weeklyFri": [
        {'searchVal': "55558", "templateVal": "84937", "desc": "Accepted - Feedback Reminder"},
        {'searchVal': "55560", "templateVal": "84939", "desc": "Accepted - Police check expired"},
        # {'searchVal': "55561", "templateVal": "84941", "desc": "Accepted - PLI expired"}, #on hold
    ],
    "weeklySun": [
        {'searchVal': "55562", "templateVal": "84938", "desc": "Accepted - Session 7 days reminder"},
    ],
    "monthly": [
        # {'searchVal': "55557", "templateVal": "84943", "desc": "Accepted - dormant volunteers"}, #on hold
        # {'searchVal': "55568", "templateVal": "84806", "desc": "In Process - training not scheduled"},
        {'searchVal': "55564", "templateVal": "84940", "desc": "Accepted - WWCC expired"},
        {'searchVal': "56852", "templateVal": "84269", "desc": "In Process - Checks not received"},
    ]
}


def sendEmails(emailList):
    #set some options
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    exPath = '/usr/local/bin/chromedriver'
    #load the webdriver
    with (webdriver.Chrome(executable_path=exPath,options=options)) as browser:
        wait = WebDriverWait(browser, 5)
        browser.set_window_size(1170, 900)
        #navigate to the login page
        browser.get("https://app.betterimpact.com/Login/Admin")
        usernameInput = wait.until(EC.visibility_of_element_located((By.ID, "UserName")))
        usernameInput.send_keys(os.environ.get("USERNAME"))
        passwordInput = browser.find_element_by_id("Password")
        passwordInput.send_keys(os.environ.get("PASS"))
        browser.find_element_by_id("SubmitLoginForm").click()
        time.sleep(3)
        browser.get("https://app.betterimpact.com/Organization/Email/SendEmail")
        for emailDetails in emailList:
            try:
                logger.info(emailDetails["desc"])
                savedElm = wait.until(EC.visibility_of_element_located((
                    By.ID, 
                    "UserSearchSavedSearchesDropDown"
                )))
                savedSelect = Select(savedElm)
                savedSelect.select_by_value(emailDetails["searchVal"])
                time.sleep(4)
                browser.find_element_by_id("SearchCriteriaUseThisSearchButton").click()
                time.sleep(1)
                browser.find_element_by_id("SearchCriteriaSearchButton").click()
                try:
                    templateElm = wait.until(EC.visibility_of_element_located((
                        By.ID, 
                        "EmailModel_TemplateOptions"
                    )))
                except TimeoutException:
                    logger.info("No emails to send")
                    emailDetails["result"] = "No emails to send"
                    continue
                templateSelect = Select(templateElm)
                templateSelect.select_by_value(emailDetails["templateVal"])
                time.sleep(1)
                browser.find_element_by_id("SendEmailButton").click()
                time.sleep(1)
                try:
                    browser.find_element_by_id("TemplateDialogConfirmButton").click()
                except Exception as e:
                    logger.debug("no confirmation box")
                    logger.debug(str(e))
                logger.debug("Success")
                emailDetails["result"] = "Success"
                time.sleep(4)
            except Exception as e:
                emailDetails["result"] = "Error:\n{}".format(str(e))
                logger.error(str(e))
    # print(emailList)


if __name__ == "__main__":
    try:
        logger.info("Sending {} emails".format(sys.argv[1]))
        sendEmails(searches[sys.argv[1]])
        logger.info("Done")
    except Exception as e:
        logger.error("Fatal Error")
        logger.error(str(e))
