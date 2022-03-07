from distutils import extension
from statistics import mode
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import pyrebase 
import environ
from pprint import pprint

from rsa import decrypt

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

config = {
  'apiKey': env('apiKey'),
  'authDomain': env('authDomain'),
  'databaseURL': env('databaseURL'),
  'projectId': env('projectId'),
  'storageBucket': env('storageBucket'),
  'messagingSenderId': env('messagingSenderId'),
  'appId': env('appId')
}

firebase = pyrebase.initialize_app(config)
try:
    IsUser=user['userId']
except:
       IsUser = None

auth = firebase.auth()
db = firebase.database()

# create the root window
root = tk.Tk()
root.title('File Vault')
root.geometry('300x550')

authenticate_page = ttk.Frame(root)
authenticate_page.pack()

main = ttk.Frame(root)

def signup(email, password):
    email = email.get()
    password = password.get()
    try:
        user = auth.create_user_with_email_and_password(email, password)
    except:
        showinfo(
            title="Error!",
            message="Signup failed"
        )
    else:
        print('Sucessfully created account')
        user = auth.refresh(user['refreshToken'])
        global IsUser
        IsUser=user['userId']
        authenticate_page.pack_forget()
        main.pack()

def login(email, password):
    email = email.get()
    password = password.get()
    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except:
        showinfo(
            title="Error!",
            message="Login failed"
        )
    else:
        print('Sucessfully logged in')
        user = auth.refresh(user['refreshToken'])
        global IsUser
        IsUser = user['userId']
        authenticate_page.pack_forget()
        main.pack()

#Authentication Widgets

#email label and entry box
emailLabel = ttk.Label(authenticate_page, text="User Name").grid(row=0, column=0)
email = tk.StringVar()
emailEntry = ttk.Entry(authenticate_page, textvariable=email).grid(row=0, column=1)  

#password label and entry box
passwordLabel = ttk.Label(authenticate_page,text="Password").grid(row=1, column=0)  
password = tk.StringVar()
passwordEntry = ttk.Entry(authenticate_page, textvariable=password, show='*').grid(row=1, column=1) 

#login and signup button
loginButton = ttk.Button(authenticate_page, text="Login", command=lambda:login(email, password)).grid(row=4, column=0)  
SignupButton = ttk.Button(authenticate_page, text="Signup", command=lambda:signup(email, password)).grid(row=4, column=1)  

#function to logout, hides main and shows authenticate_page page
def logout():
    main.pack_forget()
    authenticate_page.pack()

logout_button = ttk.Button(main, text="Logout", command=lambda: logout())
logout_button.pack()
  
def generate_key():
    # key generation
    key = Fernet.generate_key()
    # string the key in a file
    data = {"value": key.decode("utf-8")}
    try:
        db.child("keys").child(IsUser).set(data)
    except:
        showinfo(
            title="Error!",
            message="Failed to create key"
        )
    else:
        showinfo(
            title='Success!',
            message='Key successfully created!'
        )

#function to create key, hides main and shows create key page
def create_key():
    # This will recover the widget from toplevel
    generate_key()
  
  
# See, in command create_key() function is passed to hide Button B1
create_key_button = ttk.Button(main, text="Create New Key", command=lambda: create_key())
create_key_button.pack()

def select_file(fernet):
    file = fd.askopenfilename(
        title='Open a file',
        initialdir='/',)
    try:
        extension = file.split(".")[-1]
        file_name = file.split("/")[-1].split(".")[0]
    except:
        showinfo(
            title="Error!",
            message="Something went wrong"
        )
        
    with open(file, 'rb') as tf:
        data = tf.read()
    encrypted = fernet.encrypt(data)
    data = {"value": encrypted.decode("utf-8"), "extension":extension}
    try:
        db.child("vault").child(IsUser).child(file_name).set(data)
    except:
        showinfo(
            title="Error!",
            message="Something went wrong"
        )
    else:
        showinfo(
            title='Success!',
            message='File encrypted and saved successfully!'
        )

def get_key():
    print(IsUser)
    try:
        item = db.child("keys").child(IsUser).get()
        fernet = Fernet(item.val()["value"])
    except: 
        showinfo(
            title='Error!',
            message='You dont have any saved keys'
        )
    else:
        select_file(fernet)

#Dashboard widgets
encrypt_button = ttk.Button(main, text='Select file to store', command=lambda: get_key())
encrypt_button.pack()

view_files_page = ttk.Frame(root)

def return_from_view_files(my_files):
    for i in range(len(my_files)):
        my_files[i].pack_forget()
    view_files_page.pack_forget()
    main.pack()

def download_file(value):
    print(value)

def view_stored_files():
    global my_files
    my_files = []
    main.pack_forget()
    view_files_page.pack()
    back_button = ttk.Button(view_files_page, text="Back", command=lambda: [back_button.pack_forget(), return_from_view_files(my_files)])
    back_button.pack()
    try:
        files = db.child("vault").child(IsUser).get()
        print(files.key())
        for file in files.each():
            btn = ttk.Button(view_files_page, text={file.key() + '.' + file.val()['extension']}, command=lambda this_file=file: download_file(this_file.val()['value']))
            btn.pack()
            my_files.append(btn)
    except:
        showinfo(
            title="Error!",
            message="Something went wrong"
        )

decrypt_button = ttk.Button(main, text='View stored files', command=lambda: view_stored_files())
decrypt_button.pack()
# run the application
root.mainloop()