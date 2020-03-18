from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from email.mime.multipart import MIMEMultipart 
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from selenium import webdriver
from email import encoders
from flask import Flask, render_template
import requests 
import smtplib
import time

file = open("./files/years_to_check.txt", "r")
target_list = eval(file.read())
file.close()
file = open("./files/user_credentials.json", "r")
user_credentials = eval(file.read())
file.close()
file = open("./files/email_credentials.json", "r")
email_credentials = eval(file.read())
file.close()


course_label = ""
count = 0


def email(email_id, course_label, body):
    message = MIMEMultipart()
    message['Subject'] = f"{course_label} was added!"
    message.attach(MIMEText(body, "html"))


    # file = open("/home/shamoilarsi/Desktop/result.html", 'r')
    # file = open("D:\\Desktop\\result.html", 'r')
    # p = MIMEBase('application', 'octet-stream') 
    # p.set_payload((file).read()) 
    # encoders.encode_base64(p) 
    # p.add_header('Content-Disposition', "attachment; filename= result.html") 
    # message.attach(p) 


    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login((email_credentials['email']), (email_credentials['password']))
        smtpObj.sendmail((email_credentials['email']), email_id, message.as_string())
        smtpObj.close()      
        print("Successfully sent email")
    except:
        print("Error: unable to send email")


def wait_for_element(element_id, check_alert):
    if check_alert:
        time.sleep(3)
        try:
            alert = driver.switch_to.alert
            alert.accept()
            print ("Alert Accepted")
            return False
        except:
            return True
    
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, element_id)))
        return True
    except TimeoutException:
        print ("Element took more more than 3 seconds to load!")
        return False

chrome_options = Options()
chrome_options.add_argument("--headless")

# driver = webdriver.Chrome("./chromedriver_linux64/chromedriver")
driver = webdriver.Chrome(executable_path=".\\chromedriver_win32\\chromedriver")#, options=chrome_options)
driver.get("https://results.unipune.ac.in/")

while True:
    count += 1
    print("Try : " + str(count))

    for i in range(2, 5):
        course_label = driver.find_element_by_xpath(f"/html/body/form/div[5]/div/center/div/table/tbody/tr[{i}]/td[2]/span").text
        if course_label[:14] in target_list:
            year_name = course_label[:2]
            target_list.remove(course_label[:14])
            file = open("./files/years_to_check.txt", "w")
            file.write(str(target_list))
            file.close()
            
            submit_button = driver.find_element_by_xpath(f"/html/body/form/div[5]/div/center/div/table/tbody/tr[{i}]/td[4]/input")
            submit_button.click()
            wait_for_element("ctl00_ContentPlaceHolder1_btnSubmit", False)

            for email_id in user_credentials[year_name]:
                submit_button = driver.find_element_by_xpath("/html/body/form/div[5]/div[1]/center[1]/div[4]/input")
                PRN_text_field = driver.find_element_by_xpath("/html/body/form/div[5]/div[1]/center[1]/div[2]/input") 
                Mo_text_field = driver.find_element_by_xpath("/html/body/form/div[5]/div[1]/center[1]/div[3]/input")
                
                PRN_text_field.clear()
                Mo_text_field.clear()
                PRN_text_field.send_keys(user_credentials[year_name][email_id]["PRN"])
                Mo_text_field.send_keys(user_credentials[year_name][email_id]["Mo"])
                submit_button.click()

                if wait_for_element("ctl00_ContentPlaceHolder1_pnlContents", True):
                    contents = driver.execute_script(f"return document.getElementById(\"ctl00_ContentPlaceHolder1_pnlContents\").innerHTML;")
                    contents = contents[contents.find("<hr>"):]

                    # file = open("/home/shamoilarsi/Desktop/result.html", 'w')
                    # file = open("D:\\Desktop\\result.html", 'w')
                    # file.write("<html><body>")
                    # file.write(contents)
                    # file.write("</body></html>")
                    # file.close()

                    body = f"""<html><body>{contents} <br><br><br><a href="https://results.unipune.ac.in/">Click here</a> to view result. </body></html>"""
                    email(email_id, course_label, body)
                else:
                    body = f"""<html><body> Your Credentials are invalid! <br><br><a href="https://results.unipune.ac.in/">Click here</a> to view result. </body></html>"""
                    email(email_id, course_label, body)
                
            driver.get("https://results.unipune.ac.in/")
    #exit(0)
