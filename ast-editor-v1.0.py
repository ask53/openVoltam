# 10-14-2025 guizero saving and opening text docs, simple text editor with guizero

# original GUI, json file handling added

from guizero import *
import os
import easygui as g
import csv
import matplotlib.pyplot as plt
import json

app = App(title = "AST & json file writing and editing, \
          version 18-Oct-2025", width=1000, height=600)    

# Functions -------------------

# -----------------------------------------------------
# Create new plot of active file
def plot_me():
  x_plot = []
  y_plot = []
  time = 0
  dt = 0
  for line in lstbx_data.items:
    parsed_line = line.split(',')
    stripped_parsed_line = [p.strip() for p in parsed_line]
#    print (stripped_parsed_line)
    if stripped_parsed_line[0] == 'dt':
      dt = float(stripped_parsed_line[1])
#      print('dt found: ', dt, type(dt))
    elif stripped_parsed_line[0] == 'ConstVolts':
      v = float(stripped_parsed_line[1])
      dur = float(stripped_parsed_line[2])*dt
#      print ('ConstVolts V, durSecs: '), v, dur
      x_plot.append(time)
      y_plot.append(v)
#      print ('time & dur at ConstVolts line: ', time, dur)
      time = time + dur
      x_plot.append(time)
      y_plot.append(v)
    elif stripped_parsed_line[0] == 'Ramp': 
      v1 = float(stripped_parsed_line[1])
      v2 = float(stripped_parsed_line[2])
      dur = float(stripped_parsed_line[3])*dt
      x_plot.append(time)
      y_plot.append(v1)
#      print ('time & dur at ConstVolts line: ', time, dur)
      time = time + dur
      x_plot.append(time)
      y_plot.append(v2)
      
  plt.plot(x_plot, y_plot)  
  plt.xlabel("Time - secs")  
  plt.ylabel("Volts")  
  plt.show()
      
# -----------------------------------------------------
# update the working line string that goes into the data file
def update_wlc():
  par = cmds_btn_grp.value
  working_line_cmd.value = par
  if par.strip() == "#":
    final = par +  inbx1.value  + inbx2.value  \
         + inbx3.value  + inbx4.value
  else:
    final = par + ",  " + inbx1.value + ",  " + inbx2.value  \
         + ",  " + inbx3.value + ",  " + inbx4.value
    
  while final[-1] == ' ' or final[-1] == "," :
    print(final[-1])
    final = final[:-1]
  working_line_final.value = final
  
# command hints and nr of parameters limiter  
  print ("par = ", par)
  if par.strip() == "#":
    hint = "Comment:  Enter any text in any parameter box"
    inbx1.enable()
    inbx2.enable()
    inbx3.enable()
    inbx4.enable()    
  elif par.strip() == "dt":
    hint = "dt: Time increment in seconds for info transfer  "
    inbx1.enable()
    inbx2.disable()
    inbx3.disable()
    inbx4.disable()   
  elif par.strip() == "PotParams":
    hint = "PotParams: Par1: Max Voltage.  1,2,3,4 correspond to 1,2,5,10 volts \n " \
           + "   Par2: Curr Meas Range.  1,2,3,4 correspond to 1,10,100,1000 microamps"
    inbx1.enable()
    inbx2.enable()
    inbx3.disable()
    inbx4.disable()  
  elif par.strip() == "ConstVolts":
    hint = "   ConstVolts: A constant voltage.  Par1 = Voltage in volts \n" \
      + "      Par2 = duration in units of dt "
    inbx1.enable()
    inbx2.enable()
    inbx3.disable()
    inbx4.disable()  
  elif par.strip() == "Ramp":
    hint = "   Ramp:  A linear sweep from Par1 in volts to Par2 in volts \n"\
        + "      Par3 = duration in units of dt "
    inbx1.enable()
    inbx2.enable()
    inbx3.enable()
    inbx4.disable()  
  elif par.strip() == "Relay":  
    hint = "   Relay:  Par1 = Select relay. 1=stirrer, 2=laptop charge, 3=vibrator. " \
    + " Par2 = 1 turn selected relay on, = 2 turn off \n" \
    + " Laptop charge should be Off during Rodeostat operation for noise reduction"
    inbx1.enable()
    inbx2.enable()
    inbx3.disable()
    inbx4.disable()  
    
  else:
    hint = "Just Testing for now"
  
  hints.value = hint
 
# -----------------------------------------------------
# insert the working line below selected line in listbox  
def insert_sel_line():
  sel_item = lstbx_data.value
  try:
    row_number = lstbx_data.items.index(sel_item) 
    par = working_line_final.value
    lstbx_data.insert(row_number+1,par)
  except ValueError:
    g.msgbox("No line in active file selected")

# -----------------------------------------------------
# delete the selected line in the listbox
def del_sel_line():
  sel_item = lstbx_data.value
  try:
    row_number = lstbx_data.items.index(sel_item) 
    current_items = lstbx_data.items
    current_items.pop(row_number)
    lstbx_data.clear()
    for row in current_items:
      lstbx_data.append(row)
  except ValueError:
    g.msgbox("No line in active file selected")

# -----------------------------------------------------
# save the listbox to the disk as .json
def save_file_json():
  file_to_save = g.filesavebox()
  if file_to_save[-5:] != '.json':
    file_to_save += '.json'

  dict = {}  # build the data into a dictionary
  i = 0
  for vals in lstbx_data.items:
    i += 1
    line = 'line' + str(i)   # this will be dict key
    vals2 = vals.split(',')
    dict[line] = vals2

  with open(file_to_save, 'w') as f:
    json.dump(dict, f, indent=2)   # save as json file

# -----------------------------------------------------
# save the listbox to the disk as .ast
def save_file_ast():
  file_to_save = g.filesavebox()
  if file_to_save[-4:] != '.ast':
    file_to_save += '.ast'

  with open(file_to_save, 'w') as file:
    for line in lstbx_data.items:
      file.write(line + '\n')

# -----------------------------------------------------
# clear the listbox then add starting lines for new working file
def new_file():
  verify = g.choicebox(msg='Are you sure?', title='Clear and NEW File', 
                       choices=['DON''T CLEAR', 'CLEAR and NEW'])
  if verify == 'CLEAR and NEW':
    lstbx_data.clear()        
    lstbx_data.append("# These two data lines may be modified")  
    lstbx_data.append("# but they must be there")  
    lstbx_data.append("dt   ,  .05")  
    lstbx_data.append("PotParams,   2,   3")  
    
# -----------------------------------------------------
# open from disk and put it in the listbox
def get_file():
  lstbx_data.clear()          
  file_name = g.fileopenbox()

  file_name_area.value = 'Active File:  ' + file_name
  file_name_area.set_text_size = 20
  lstbx_data.clear()
  
#  print ('debug: ', file_name[-5:])
  if file_name[-4:] == '.ast': 
    with open(file_name, "r") as csvfile:
      csv_reader = csv.reader(csvfile)
      for rows in csv_reader:
         prow = ""
         for row in rows:
           prow += row + " , "
         prow = prow[0:-3]  
         lstbx_data.append(prow)
         print(row[0])         
  elif file_name[-5:] == '.json': 
    with open(file_name, 'r') as f:
      dict = json.load(f)
  else:
    print('File type not recognized')

# I am assuming that the dictionary may have been scrambled
  nrKeys = len(dict)
  for keyNr in range(1, nrKeys+1):
    lineNr = 'line' + str(keyNr)
    print ('key nr, line nr: ', keyNr, '  ', lineNr)
  
  for rowNr in range(1, nrKeys+1):
    lineNr = 'line' + str(rowNr)
    myRow = ""
    for item in dict[lineNr]:
      myRow += item + ','
    myRow = myRow[:-1]
    
    lstbx_data.append(myRow)

#  -------------------------------------------    
# Widgets -------------------------------------       

saving_box = Box(app, width='fill')
saving_box.bg = 'AntiqueWhite1'

edit_box = Box(app, width='fill', layout='grid')
# spread the grid
for i in range(10):
  for j in range(10):
    Text(edit_box, text="      ", grid=[i,j])
    
btn_box = Box(saving_box, layout='grid')

btn1 = PushButton(btn_box, text='Open Existing File'
      + '\n .ast or .json', command = get_file, 
                  grid=[0,0])
btn1.bg = 'Light Yellow'

btn2 = PushButton(btn_box, text='Save Active File as .ast', grid=[1,0],
                  command=save_file_ast)
btn2.bg = 'Light Yellow'

btn3 = PushButton(btn_box, text='Save Active File as .json', grid=[2,0],
                  command=save_file_json)
btn3.bg = 'Light Yellow'

btn4 = PushButton(btn_box, text='New File', grid=[3,0],
                  command=new_file)
btn4.bg = 'Light Yellow'

Text(saving_box, text = " ")

Text(saving_box, text = " ", align='bottom')
file_name_area = Text(saving_box, text = "Active File: No choice made yet", 
                        align='left') #, width='fill')
file_name_area.set_text_size = 20

lstbx_data = ListBox(edit_box, width=250, height=250, scrollbar=True, 
                  grid=[1,1, 1, 5], items=["#  These two data lines "  \
                  "may be edited" , "# but they may not be deleted", \
                    "dt   ,  .05", "PotParams,   2,   3"])

btn10 = PushButton(edit_box, text= 'Delete Selected Line', grid=[2,1],
                   command = del_sel_line)
btn11 = PushButton(edit_box, text= 'Insert Working Line Below Selected Line', 
                   grid=[2,2], command = insert_sel_line)

btn12 = PushButton(edit_box, text='Show/Update Plot of Active File', grid=[2,3],
                   command=plot_me)

Text(edit_box, text="Commands", grid=[7,1])
cmds_btn_grp = ButtonGroup(edit_box, options=[["Comment","# "],
        ["dt","dt"], ["PotParams","PotParams"],
        ["ConstVolts","ConstVolts"], ["Ramp","Ramp"], 
        ["Relay","Relay"]], grid = [7,2])
cmds_btn_grp.update_command(update_wlc)   #Funny usage patch found online

Text(edit_box, text= 'Working Line: ', grid=[2,5])

working_line_cmd = Text(edit_box, text = "#", grid=[3,5], width=15)
inbx1 = TextBox(edit_box,grid=[4,5], width=8, command = update_wlc)
inbx2 = TextBox(edit_box,grid=[5,5], width=8, command = update_wlc)
inbx3 = TextBox(edit_box,grid=[6,5], width=8, command = update_wlc)
inbx4 = TextBox(edit_box,grid=[7,5], width=8, command = update_wlc)
working_line_final = Text(edit_box,grid=[3,6], text="# ")

hints_box = Box(app, width='fill', layout="grid")    
    
Text(hints_box, text="Command Hints:", grid=[0,0])
hints = Text(hints_box, text=" ", grid=[1,0])

#  ------------------------------------------    

app.display()

