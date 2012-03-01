#_*_ coding: utf-8 _*_

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

#using pyvirtualdisplay to hide the process screen
# https://github.com/ponty/PyVirtualDisplay
from pyvirtualdisplay import Display
display = Display(visible=0, size=(1024, 768))
display.start()

driver = webdriver.Firefox()

## or using the chromedriver, http://code.google.com/p/chromedriver/ 
#driver = webdriver.Chrome(executable_path='./chromedriver')

print 'start loading google ...'

driver.get('http://www.google.com')

print 'now, query the selenium with google'

input = driver.find_element_by_name('q')  #find the input and focus
input.send_keys('selenium')  #send inputs
input.submit()

# wait for the result
WebDriverWait(driver, 10).until(lambda driver: driver.title.lower().startswith('selenium'))
print 'got the result ', driver.title

# save a screen shot
driver.save_screenshot('google.png') # or driver.get_screenshot_as_file('google.png')

driver.quit()

display.stop()

