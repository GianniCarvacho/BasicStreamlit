import pickle
from pathlib import Path
import streamlit_authenticator as stauth



nombres =  ["Gianni", "lala","fito"]
usernames = ["Ugianni", "Ulala", "Ufito"]
passwords = ["1234", "1234", "1234"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "Pw_Hashed.pkl"

with open(file_path, "wb") as file:
 pickle.dump(hashed_passwords, file)
 