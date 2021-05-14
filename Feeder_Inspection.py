
from collections import OrderedDict
import datetime
import os
import csv
import re
import sqlite3

from peewee import *

#Database----------------------------------------
db = SqliteDatabase('Feeder Inspection.db')

class FIC(Model):
	id = PrimaryKeyField()
	building_name = CharField(max_length = 255, unique =True)
	date = DateTimeField(default = datetime.datetime.now)
	days_last_inspect = IntegerField()
	
	class Meta:
		database = db


def initialize():
	#Create the database
	db.connect()
	db.create_tables([FIC], safe = True)

#Database----------------------------------------


#System control functions------------------------
def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')
#System control functions------------------------


#Functions---------------------------------------
def menu_loop():
	"""Menu"""
	choice = None

	while choice != 'q':
		print("")
		print("Enter [Q] to quit.")

		for key, value in menu.items(): #loop through the dictionary and print
			print('[{}]) {}'.format(key,value.__doc__)) #the 'value__doc__': Because our values are functions, we need to use __doc__ to use the function

		while True:
			choice = input('>> ').lower().strip()

			if choice != 'i' and choice != 's' and choice != 'v'  and choice != 'q' and choice != 'l' and choice != 'd':
				print("Invalid input. The options are [I], [S], [Q], [V], [L], [D]. Select one of the option.")
			else:
				break

		if choice in menu:
			clear_screen()
			menu[choice]()


def view_entries():
	"""View Data"""
	number_of_items = get_max_item_count()

	for row in range(number_of_items + 1):
		if row == 0:
			print("ID" + "|" + "Building Name" + "|" + "Date" + "|" + "Last Inspected")
		else:
			print("")
			FIC_record = FIC.get(id = row)
			print(str(FIC_record.id) +
				" | "+ FIC_record.building_name +
				" | "+ str(FIC_record.date) +
				" | "+ str(FIC_record.days_last_inspect) + " Days Ago")


def input_entry():
	"""Add/Edit Data"""
	now = datetime.datetime.now()
	
	building_name = input("Enter Building Name: ")
	clear_screen()

	while True:
		print('Date Format >> m/d/y')
		date = input("Day of Inspection:")
		try:
			date = datetime.datetime.strptime(date, '%m/%d/%Y' ) #Checking to see if it's a number
			break
		except:
			print("Invalid format was entered. Try again\n")

	Today= now.strptime(datetime.datetime.today().strftime('%m/%d/%Y'), '%m/%d/%Y')
	

	if Today == date:
		last_inspected = 0
	else:
		last_inspected = date - Today
	#There are two due to the Regex on day vs days
	last_inspected = re.sub(r'-', '', re.sub(r'.days.........','', str(last_inspected))) # more than one day ago
	last_inspected = re.sub(r'-', '', re.sub(r'.day.........','', str(last_inspected))) #For one day ago dates

	date = re.sub(r'.00','',   #keeps the normal format
							re.sub(r'-','/', str(date)))

	new_item = {'building_name': building_name, 
				'date': date, 
				'days_last_inspect': int(last_inspected)}

	clear_screen()
	print(new_item['building_name'].title() + 
		" | " + str(new_item['date']) + 
		" | " + str(new_item['days_last_inspect']) + " Days Ago")

	while True:
		response = input('Save entry? [Y]es | [N]o :').lower()
		if response != 'n' and response != 'y':
			print("Invalid input. The options are [y], [n]. Select one of the option.")
		else:
			break

	if response == 'y':
		number_of_items = get_max_item_count()

		try:
			FIC.create(id = number_of_items + 1, #adding one is for a new line
						building_name = (new_item['building_name']).title(), # 'title' format to look clean
						date = new_item['date'],
						days_last_inspect = new_item['days_last_inspect'])

		except IntegrityError:
			FIC_record = FIC.get(building_name = (new_item['building_name']).title())#Comparing the data with 'title' format

			if FIC_record.id != number_of_items + 1 : #When the notice the product exist in a different spot, run this
				FIC_record.id = FIC_record.id # It updates that spot
				print("The item you've entered was already in the database. It was updated with the new info!")
				
			else:
				FIC_record.id = number_of_items

			FIC_record.date = new_item['date']
			FIC_record.days_last_inspect = new_item['days_last_inspect']
			FIC_record.save()
		print("")
		print("Saved successfully!")


def backup_data():
	"""Save to CSV"""
	dictionary_holder =[]
	id_counter = 0

	number_of_items = get_max_item_count()

	for item in range(number_of_items + 1):
		if item == 0: #there isn't a 0 entry, so skip this
			continue
		else:
			full_records = FIC.get(id = item)

		temp = {'id':full_records.id,
			'building_name':full_records.building_name ,
			'date':full_records.date,
			'days_last_inspect':full_records.days_last_inspect}
		dictionary_holder.append(temp)

	#--------'csv_columns', 'csv_file', 'data' variables were not changed from the source https://www.tutorialspoint.com/How-to-save-a-Python-Dictionary-to-CSV-file
	csv_columns = ['id', 'building_name', 'date', 'days_last_inspect'] 
	csv_file = "Feeder Inspection.csv"
	with open(csv_file, 'w') as csvfile:  #If this file doesn't exist, this creates it
		writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
		writer.writeheader()
		for data in dictionary_holder:
			writer.writerow(data)

	print("Your data was saved. Filename: " + csv_file)

def search_data():
	"""Search Data"""
	clear_screen()
	
	choice = None

	while True:
		print("Enter [Q] to quit search.")
		search_phrase = input("Enter the word/phrase you want to search: ")

		if search_phrase == 'q':
			break

		number_of_items = get_max_item_count()

		for item in range(number_of_items + 1):
			if item == 0: #there isn't a 0 entry, so skip this
				continue
			else:	
				full_records = FIC.get(id = item)

				if (search_phrase).lower() in (full_records.building_name).lower():
					print(str(full_records.id) +
					" | "+ full_records.building_name +
					" | "+ str(full_records.date) +
					" | "+ str(full_records.days_last_inspect) + " Days Ago")
		break
				
def delete_data():
	"""Delete Data"""
	check = True
	checkl = 0
	choice = None
	number_of_items = get_max_item_count()


	while check == True:

		try:
			print("Enter [Q] to quit search.")
			position = int(input("Which entry by # position you want to delete: "))
			checkl = 1
		except:
			if checkl == 0:
				check = False
			else:
				print("")
				print("A number needs to be entered. Try again")
			continue


		if position > 0 and position < number_of_items: #position number outside the range error out
			full_records = FIC.get(id = position)
			print(str(full_records.id) +
					" | "+ full_records.building_name +
					" | "+ str(full_records.date) +
					" | "+ str(full_records.days_last_inspect) + " Days Ago")
			print("")
			print("Are you sure you want to delete this entry? ")
			choice = input('[Y]es | [N]o : ').lower()

			if choice == 'y':
				mycursor = db.cursor() #Using cursor for the database
				sql = """DELETE FROM fic WHERE id = ?""" #Using raw SQL here to search
				mycursor.execute(sql, (position,)) #This is deleting the row
				db.commit() # This is saving the database

				database_refresh(position)

				break
			else:
				break
		else:
			print("The position number you've entered doesn't exist. Try again.")

#This will fix the numbering 
def database_refresh(id):
	boolcheck = True # For while loop
	counter = 1 #This is for the 'for loop'. This is not 0 because there's no ID position that's 0

	number_of_items = get_max_item_count() #Gets the max amount of entries in the database

	while(boolcheck):
			for item in FIC.select(): # looks through the entries
				if item.id == counter: #if the counter is the same number as the item's ID, continue
					counter += 1
					continue

				#If they're not the same and the counter less than the max amount of items
				elif item.id != counter and counter <= number_of_items: 
					entry = FIC.get(item.id) #Get the item's position and its' data
					FIC.get( item.id ).delete_instance()
					FIC.create(id = counter, #Create a new entry in the spot of the deleted entry
									building_name = entry.building_name,
									date = entry.date,
									days_last_inspect = entry.days_last_inspect)

					#At this point, you have two entries with the same data.
					#This deletes the one that out of place
					
					counter = 1 #resetting counter to 1

					break #Break the 'for loop' to restart its loop to find other out of place entries properly

				else: #This run when all numbers have been check and will exit the 'for' and 'while' loop
					boolcheck = False
					break




def get_max_item_count():
	count = 0
	max_loop_count = FIC.select()

	for items in max_loop_count: #Counting each item stored
		count +=1
	return count
#Functions---------------------------------------

#Main-----------------------------------
menu = OrderedDict([
	('i', input_entry),
	('v', view_entries),
	('s', backup_data),
	('l', search_data),
	('d', delete_data),
	])

initialize() #get database ready


now = datetime.datetime.now()

number_of_items = get_max_item_count()

database_refresh(1)

#Dates refresh-------
for item in range(number_of_items + 1):
	if item == 0: #there isn't a 0 entry, so skip this
		continue
	else:	
		full_records = FIC.get(id = item)

		while True:
			rdate = full_records.date
			try:
				rdate = datetime.datetime.strptime(rdate, '%Y/%m/%d' ) #Checking to see if it's a number
				break
			except:
				break

		Today= now.strptime(datetime.datetime.today().strftime('%m/%d/%Y'), '%m/%d/%Y')

		if Today == rdate:
			last_inspected = 0
		else:
			last_inspected = rdate - Today
		last_inspected = re.sub(r'-', '', re.sub(r'.days.........','', str(last_inspected)))

		full_records.days_last_inspect = int(last_inspected)
		full_records.save()




menu_loop() #Menu prompt for user