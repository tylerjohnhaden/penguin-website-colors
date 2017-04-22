import os

from selenium import webdriver

relative_path = 'chromedriver'
absolute_path = os.getcwd() + '/chromedriver'

print 'webdriver.Chrome(\'%s\')' % relative_path
try:
    driver = webdriver.Chrome(relative_path)
except:
    print 'Failed\n'
    print 'webdriver.Chrome(\'%s\')' % absolute_path
    try:
        driver = webdriver.Chrome(absolute_path)
    except:
        print 'Failed\n'
        print 'os.environ["webdriver.chrome.driver"] = %s' % relative_path
        print 'webdriver.Chrome(\'%s\')' % relative_path
        try:
            os.environ["webdriver.chrome.driver"] = relative_path
            driver = webdriver.Chrome(relative_path)
        except:
            print 'Failed\n'
            print 'os.environ["webdriver.chrome.driver"] = %s' % absolute_path
            print 'webdriver.Chrome(\'%s\')' % absolute_path
            try:
                os.environ["webdriver.chrome.driver"] = absolute_path
                driver = webdriver.Chrome(absolute_path)
            except:
                print 'Failed\n'
                quit()

driver.get('http://google.com')
driver.save_screenshot('google.png')
driver.quit()
