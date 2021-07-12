from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import time
import logging

"""
saved searches:
55048 - 84943 - Accepted - dormant volunteers / reconnect - Monthly
55050 - 84937 - Acc - Feedback reminder - Weekly
55052 - 84939 - acc - Police check expired - Weekly
55053 - 84941 - Acc - PLI expired - Weekly
55054 - 84938 - acc - session reminder (7 days ahead) - Weekly
55056 - 84940 - Acc - WWCC expired - Weekly
55060 - 84269 - In process - checks not received - weekly
55062 - 84806 - in process - training not scheduled - monthly
"""
searches = {
    "weekly": [
        {'searchVal': "55050", "templateVal": "84937", "desc": "Accepted - Feedback Reminder"},
        {'searchVal': "55052", "templateVal": "84939", "desc": "Accepted - Police check expired"},
        {'searchVal': "55053", "templateVal": "84941", "desc": "Accepted - PLI expired"},
        {'searchVal': "55054", "templateVal": "84938", "desc": "Accepted - Session reminder"},
        {'searchVal': "55056", "templateVal": "84940", "desc": "Accepted - WWCC expired"},
        {'searchVal': "55060", "templateVal": "84269", "desc": "In Process - Checks not received"},
    ],
    "monthly": [
        {'searchVal': "55048", "templateVal": "84943", "desc": "Accepted - dormant volunteers"},
        {'searchVal': "55062", "templateVal": "84806", "desc": "In Process - training not scheduled"},
    ]
}


def tester(emailList):
    #set some options
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    exPath = '/usr/local/bin/chromedriver'
    #load the webdriver
    with (webdriver.Chrome(executable_path=exPath,options=options)) as browser:
        wait = WebDriverWait(browser, 5)
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
                print()
                print(emailDetails["desc"])
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
                    print("No results")
                    emailDetails["result"] = "No emails to send"
                    continue
                templateSelect = Select(templateElm)
                templateSelect.select_by_value(emailDetails["templateVal"])
                time.sleep(1)
                # browser.find_element_by_id("SendEmailButton").click()
                # time.sleep(1)
                # try:
                #     browser.find_element_by_id("TemplateDialogConfirmButton").click()
                # except Exception as e:
                #     print("no confirmation box")
                #     print(str(e))
                emailDetails["result"] = "Success"
                print("success")
                time.sleep(4)
            except Exception as e:
                emailDetails["result"] = "Error:\n{}".format(str(e))
    print(emailList)


if __name__ == "__main__":
    tester(searches["weekly"])