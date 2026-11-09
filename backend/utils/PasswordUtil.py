from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(mot_de_passe: str) -> str:
    return password_hash.hash(mot_de_passe)

def verifier_mot_de_passe(mot_de_passe: str, hash_enregistre: str) -> bool:
    return password_hash.verify(mot_de_passe, hash_enregistre)
