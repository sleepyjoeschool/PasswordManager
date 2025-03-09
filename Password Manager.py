import tkinter as tk
from tkinter import messagebox, simpledialog
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import pyperclip

# AES NEW PASSWORD
def aes_encrypt(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode()

# AES DECRYPT PASSWORD
def aes_decrypt(key, ciphertext):
    data = base64.b64decode(ciphertext.encode())
    iv = data[:16]
    ciphertext = data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()

# Generate the corresponding AES key based on the master password
def generate_valid_aes_key(password):
    key = password.encode()
    while len(key) not in [16, 24, 32]:
        key += b'0'
    return key[:32]

# Add password clicked
def on_encrypt():
    # New Window
    PasswordManagerWindow = tk.Tk()
    PasswordManagerWindow.withdraw()  # Hide main window
    # New message
    messagebox.showinfo(" Warning ", "Warning: Use a secure master password, as losing it means you can't access your encrypted passwords and if someone has your master password, they can access all your encrypted passwords.")
    password = simpledialog.askstring("Setup or enter your Master Password", "Enter the master password (the entered password will not be displayed):", show=' ')
    if not password:
        return
    key = generate_valid_aes_key(password)
    plaintext = simpledialog.askstring("Encrypt password", "Enter the password to encrypt:", show='*')
    if not plaintext:
        return
    PasswordManagerWindow = tk.Tk()
    PasswordManagerWindow.withdraw()   # Hide main window
    # New message
    messagebox.showinfo(" Warning ", "Warning: Do not use the same string for your note twice. Or the program may only find the first position of the password with that note.")
    note = simpledialog.askstring(" Domain name and account ID ", "Add a note with the domain name and account ID for easy find password:")
    if not note:
        return
    ciphertext = aes_encrypt(key, plaintext)
    with open("key.bin", "a") as f:
        f.write(f"{note}:{ciphertext}\n")
        file_path = "note.txt"
        lines_to_add = [note]
        with open(file_path, "a", encoding="utf-8") as file:
            for line in lines_to_add:
                file.write(line + "\n")
    messagebox.showinfo(" Operation complete ", "Password has been stored in key.bin in form of ciphertext.")

# Decrypt button clicked
def on_decrypt():
    if not os.path.exists("key.bin"):
        messagebox.showerror("Whoops!", "File key.bin not find! Are you sure it exist in the same directory along with this program?")
        return
    with open("key.bin", "r") as f:
        lines = f.readlines()
    notes = [line.split(':')[0] for line in lines]
    selected_note = simpledialog.askstring("Enter the note", "Enter the note. You can find them in the file [note.txt]:", initialvalue=notes[0])
    if not selected_note:
        return
    password = simpledialog.askstring("Enter master password", "Enter your master password:", show='*')
    if not password:
        return
    key = generate_valid_aes_key(password)
    for line in lines:
        if line.startswith(selected_note):
            ciphertext = line.split(':')[1].strip()
            try:
                plaintext = aes_decrypt(key, ciphertext)
                copy = messagebox.askyesno("Operation complete", f"Encrypted Password: {plaintext}\n Put the password in your clipboard?")
                if copy:
                    pyperclip.copy(plaintext)
                break
            except:
                messagebox.showerror("Whoops!", "Invalid master password! You may try again.")
                break

# Main window
PasswordManagerWindow = tk.Tk()
PasswordManagerWindow.title("Password manager")

# Buttons clicked
encrypt_button = tk.Button(PasswordManagerWindow, text="New password", command=on_encrypt)
encrypt_button.pack(pady=10)

decrypt_button = tk.Button(PasswordManagerWindow, text="Find password", command=on_decrypt)
decrypt_button.pack(pady=10)

# END
PasswordManagerWindow.mainloop()
